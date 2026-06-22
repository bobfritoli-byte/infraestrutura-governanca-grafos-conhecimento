"""Agente NL -> SPARQL ancorado e auto-corretivo do projeto ELLAS.

Pipeline:
  1. Recuperação: seleciona as competency questions validadas mais parecidas
     (few-shot) usando TF-IDF/cosseno em Python puro.
  2. Geração: o LLM (Groq/Llama) adapta o exemplo mais próximo, ancorado no
     cartão de schema real.
  3. Validação + execução no GraphDB; em caso de erro de sintaxe, o erro é
     devolvido ao LLM para correção (loop agêntico). Se vier vazio, faz uma
     tentativa de relaxar os filtros.

Exposto: run_agent(question) -> dict com sparql, results, error, attempts, etc.
"""
import re
import math
import time
from collections import Counter

import requests
import urllib3

from config import GRAPH_URL, GRAPH_AUTH, CATALOG_PATH, llm_chat
from schema_ellas import SCHEMA_CARD

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============================================================================
# 1) CATÁLOGO DE COMPETENCY QUESTIONS (gabarito validado)
# =============================================================================
def load_catalog(path=CATALOG_PATH):
    """Faz o parse do Query_SPARQL.txt -> lista de {question, sparql}."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    catalog = []
    for m in re.finditer(r"`([^`]*)`", text, re.DOTALL):
        sparql = m.group(1).strip()
        if "select" not in sparql.lower() and "PREFIX" not in sparql:
            continue
        # Pega o comentário "// ..." mais próximo ANTES do bloco que pareça pergunta
        before = text[: m.start()]
        question = None
        for c in reversed(re.findall(r"//\s*(.+)", before)):
            c = c.strip()
            low = c.lower()
            if not c or "=" in c or low.startswith(("export", "const", "fetch")):
                continue
            question = c
            break
        if question:
            catalog.append({"question": question, "sparql": sparql})
    return catalog


# =============================================================================
# 2) RECUPERADOR (TF-IDF + cosseno, sem dependências externas)
# =============================================================================
_PT_STOP = set(
    "a o as os um uma de da do das dos e em no na nos nas para por com que qual "
    "quais quanto quantos quantas quando onde como qual sao são ser esta está "
    "the of in on is are which what how many where when by for to and".split()
)


def _tokenize(s):
    return [t for t in re.findall(r"[a-z0-9à-ú]+", s.lower()) if t not in _PT_STOP and len(t) > 2]


class Retriever:
    def __init__(self, catalog):
        self.catalog = catalog
        docs = [_tokenize(c["question"]) for c in catalog]
        df = Counter()
        for d in docs:
            df.update(set(d))
        n = max(len(docs), 1)
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}
        self._default_idf = math.log(n + 1) + 1
        self.vecs = [self._vec(d) for d in docs]

    def _vec(self, tokens):
        tf = Counter(tokens)
        return {t: tf[t] * self.idf.get(t, self._default_idf) for t in tf}

    @staticmethod
    def _cosine(a, b):
        if not a or not b:
            return 0.0
        common = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def retrieve(self, question, k=6):
        qv = self._vec(_tokenize(question))
        scored = [(self._cosine(qv, dv), i) for i, dv in enumerate(self.vecs)]
        scored.sort(reverse=True)
        return [self.catalog[i] for s, i in scored[:k]]


# Exemplos-base genéricos (ancoram perguntas simples; ajudam modelos pequenos)
_P = ("PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>\n"
      "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>")
BASE_EXAMPLES = [
    {"question": "Liste as iniciativas (nome, status e país)",
     "sparql": _P + "\nSELECT ?initiativeName ?status ?countryName WHERE {\n"
     "  ?initiative a Ellas:Initiative .\n"
     "  ?initiative rdfs:label ?initiativeName .\n"
     "  OPTIONAL { ?initiative Ellas:initiative_status ?status . }\n"
     "  OPTIONAL { ?initiative Ellas:created_in ?country . ?country rdfs:label ?countryName . }\n"
     "} LIMIT 100"},
    {"question": "Quantas iniciativas existem no total?",
     "sparql": _P + "\nSELECT (COUNT(DISTINCT ?initiative) AS ?total) WHERE {\n"
     "  ?initiative a Ellas:Initiative .\n}"},
    {"question": "Liste os países que possuem iniciativas",
     "sparql": _P + "\nSELECT DISTINCT ?countryName WHERE {\n"
     "  ?initiative a Ellas:Initiative .\n"
     "  ?initiative Ellas:created_in ?country .\n"
     "  ?country rdfs:label ?countryName .\n}"},
]

# Carrega catálogo (gabarito validado) + exemplos-base; constrói o recuperador
try:
    CATALOG = load_catalog() + BASE_EXAMPLES
except Exception as e:  # pragma: no cover
    print(f"[agent] Falha ao carregar catálogo: {e}")
    CATALOG = list(BASE_EXAMPLES)
RETRIEVER = Retriever(CATALOG)


# =============================================================================
# 3) GERAÇÃO DE SPARQL (few-shot, ancorada no schema)
# =============================================================================
def _clean_sparql(text):
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return _postfix_sparql(text.strip())


def _postfix_sparql(q):
    """Corrige erros comuns de modelos pequenos: LIMIT/OFFSET dentro do WHERE { }."""
    last = q.rfind("}")
    if last == -1:
        return q
    body, tail = q[:last], q[last:]
    mods = []

    def grab(pattern):
        nonlocal body
        while True:
            m = re.search(pattern, body, re.IGNORECASE)
            if not m:
                break
            mods.append(m.group(0).strip())
            body = body[:m.start()] + body[m.end():]

    grab(r"\bOFFSET\s+\d+")
    grab(r"\bLIMIT\s+\d+")
    if not mods:
        return q

    limit = [m for m in mods if m.upper().startswith("LIMIT")]
    offset = [m for m in mods if m.upper().startswith("OFFSET")]
    suffix = " ".join(limit + offset)
    return f"{body.rstrip()}{tail} {suffix}".strip()


def generate_sparql(question, examples, error_feedback=None, provider=None):
    ex_text = "\n\n".join(
        f"# Pergunta: {e['question']}\n{e['sparql'].strip()}" for e in examples
    )
    system = f"""Você é um gerador de consultas SPARQL para o grafo de conhecimento ELLAS \
(participação feminina em STEM na América Latina).

{SCHEMA_CARD}

Use os EXEMPLOS VALIDADOS abaixo como referência PRINCIPAL: prefira ADAPTAR o exemplo \
mais parecido com a pergunta (trocando país, status, cidade, público-alvo, etc.) a \
inventar uma consulta do zero. Respeite as REGRAS DE OURO do schema.

EXEMPLOS VALIDADOS (pergunta -> SPARQL que funciona no endpoint):
{ex_text}

SAÍDA: retorne SOMENTE a consulta SPARQL final, sem crases, sem comentários e sem \
texto explicativo. Inclua sempre os PREFIX necessários."""

    user = f"Gere o SPARQL para a pergunta:\n{question}"
    if error_feedback:
        user += (
            f"\n\nA tentativa anterior falhou. Mensagem do GraphDB:\n{error_feedback}\n"
            "Corrija a consulta mantendo-a fiel ao schema e aos exemplos."
        )

    content = llm_chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        provider=provider, temperature=0.0,
    )
    return _clean_sparql(content)


# =============================================================================
# 4) EXECUÇÃO + VALIDAÇÃO NO GRAPHDB
# =============================================================================
def execute_sparql(sparql):
    """Executa no endpoint. Retorna (results_json, None) ou (None, mensagem_erro)."""
    try:
        r = requests.get(
            GRAPH_URL,
            params={"query": sparql},
            auth=GRAPH_AUTH,
            headers={"Accept": "application/sparql-results+json"},
            verify=False,
            timeout=40,
        )
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}: {r.text.strip()[:400]}"
        return r.json(), None
    except Exception as e:
        return None, str(e)


def count_bindings(results):
    if not results or "results" not in results:
        return 0
    return len(results["results"].get("bindings", []))


# =============================================================================
# 5) ORQUESTRAÇÃO COM AUTO-CORREÇÃO
# =============================================================================
def run_agent(question, k=4, max_repairs=2, provider=None):
    """Roda o pipeline completo e retorna um relatório detalhado."""
    examples = RETRIEVER.retrieve(question, k=k)
    attempts = []
    sparql = results = error = None
    t0 = time.time()

    # Geração + correção em caso de erro de sintaxe/execução
    for _ in range(max_repairs + 1):
        try:
            sparql = generate_sparql(question, examples, error_feedback=error, provider=provider)
        except Exception as e:
            error = f"Falha na geração: {e}"
            attempts.append({"sparql": None, "error": error})
            break
        results, error = execute_sparql(sparql)
        attempts.append({"sparql": sparql, "error": error})
        if error is None:
            break

    # Se válido porém vazio, tenta relaxar os filtros uma vez
    relaxed = False
    if error is None and count_bindings(results) == 0:
        relax_fb = (
            "A consulta é válida mas retornou 0 resultados. Relaxe os filtros: troque "
            "igualdades por FILTER(regex(str(?x), \"termo\", \"i\")) e remova tags @en "
            "quando houver, mantendo a intenção da pergunta."
        )
        try:
            sparql_r = generate_sparql(question, examples, error_feedback=relax_fb, provider=provider)
            results_r, error_r = execute_sparql(sparql_r)
            attempts.append({"sparql": sparql_r, "error": error_r, "relaxed": True})
            if error_r is None and count_bindings(results_r) > 0:
                sparql, results, relaxed = sparql_r, results_r, True
        except Exception as e:
            attempts.append({"sparql": None, "error": str(e), "relaxed": True})

    return {
        "question": question,
        "sparql": sparql,
        "results": results,
        "error": error,
        "attempts": attempts,
        "n_attempts": len(attempts),
        "relaxed": relaxed,
        "matched_questions": [e["question"] for e in examples],
        "elapsed": round(time.time() - t0, 2),
    }
