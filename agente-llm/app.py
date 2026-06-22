from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import urllib3
import time
import re
import sys

# Garante saida UTF-8 no console (evita UnicodeEncodeError com emojis em cp1252/Windows)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Desabilita avisos de certificados SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# =============================================================================
# 🔑 CONFIGURAÇÕES (compartilhadas em config.py) + AGENTE
# =============================================================================
from config import GRAPH_URL, GRAPH_AUTH, llm_chat, LLM_PROVIDER
from agent import run_agent, count_bindings

# =============================================================================
# 🤖 BUSCA COM LLM (NOVO!)
# =============================================================================
def query_llm_knowledge(initiative_name, country=None, provider=None):
    """Pergunta ao LLM o que ele sabe sobre a iniciativa."""
    
    # Monta contexto
    context = f"{initiative_name}"
    if country:
        context += f" from {country}"
    
    prompt = f"""You are an expert on women in technology and STEM initiatives worldwide.

Provide FACTUAL information about this initiative:
"{context}"

If you DON'T have reliable information, respond with: "NO_INFO"

If you DO have information, provide:
- What the initiative is about
- Main focus (STEM, tech, education, etc)
- Target audience
- Where it operates
- Key activities or programs

Maximum 150 words. Be factual and specific. Write in Portuguese (BR).
"""
    
    try:
        llm_response = llm_chat(
            [{"role": "user", "content": prompt}],
            provider=provider, temperature=0.3, max_tokens=300, timeout=15,
        ).strip()

        # Validação de qualidade
        if "NO_INFO" in llm_response.upper():
            return None
        
        if len(llm_response) < 50:
            return None
        
        # Detecta respostas genéricas/incertas
        uncertain_phrases = [
            "não tenho informações",
            "não conheço",
            "não posso fornecer",
            "não tenho certeza",
            "desconheço",
            "não sei"
        ]
        
        if any(phrase in llm_response.lower() for phrase in uncertain_phrases):
            return None
        
        return llm_response
        
    except Exception as e:
        print(f"Erro na consulta LLM: {e}")
        return None

# =============================================================================
# 📡 COMUNICAÇÃO COM GRAPHDB
# =============================================================================
def query_graphdb(sparql_query):
    """Executa a query no repositório EllasV2 da UFMT."""
    try:
        response = requests.get(
            GRAPH_URL,
            params={'query': sparql_query},
            auth=GRAPH_AUTH,
            headers={'Accept': 'application/sparql-results+json'},
            verify=False
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def dedupe_bindings(result_json):
    """Extrai linhas únicas dos resultados SPARQL (remove duplicatas)."""
    if not result_json or "results" not in result_json:
        return []

    bindings = result_json["results"].get("bindings", [])
    seen = set()
    unique = []
    for b in bindings:
        row = {k: v.get("value", "") for k, v in b.items()}
        key = tuple(sorted(row.items()))
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique

def format_results(result_json):
    """Transforma o JSON do SPARQL em texto legível (fallback, já sem duplicatas)."""
    if not result_json or "results" not in result_json:
        return "Nenhum resultado encontrado."

    rows = dedupe_bindings(result_json)
    if not rows:
        return "A consulta não retornou dados no Banco."

    output = []
    for row in rows:
        line = " | ".join(f"{k}: {v}" for k, v in row.items())
        output.append(line)
    return "\n".join(output)

# Rótulos amigáveis (PT-BR) para as colunas mais comuns do grafo
COLUMN_LABELS = {
    "initiativeName": "Iniciativa",
    "initiative": "Iniciativa",
    "status": "Status",
    "countryName": "País",
    "country": "País",
    "name": "Nome",
    "label": "Rótulo",
    "count": "Total",
    "total": "Total",
}

def _md_escape_cell(value):
    """Escapa caracteres que quebrariam uma célula de tabela Markdown.

    Importante para nomes do ELLAS como '|coda, girl| jo' (pipe) ou
    '#include <girls>' (sinais de menor/maior). Os sinais < > são
    tratados no render (frontend); aqui garantimos o pipe e quebras de linha.
    """
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()

def build_markdown_table(rows):
    """Monta uma tabela Markdown determinística (dados 100% fiéis ao grafo)."""
    columns = list(rows[0].keys())
    headers = [COLUMN_LABELS.get(c, c) for c in columns]

    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        cells = [_md_escape_cell(row.get(c, "")) for c in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

def generate_intro(question, n, provider=None):
    """Usa o LLM apenas para uma frase curta de contexto (a narrativa)."""
    prompt = f"""Você é um assistente do Projeto ELLAS (mulheres em tecnologia e STEM).
O usuário perguntou: "{question}"
A consulta ao grafo retornou {n} resultado(s), que serão exibidos logo abaixo em uma tabela.
Escreva APENAS UMA frase curta (máximo 25 palavras), em português (BR), introduzindo esses resultados de forma natural.
NÃO liste os itens, NÃO invente dados, NÃO inclua números além de {n} e NÃO repita a pergunta literalmente."""

    try:
        return llm_chat(
            [{"role": "user", "content": prompt}],
            provider=provider, temperature=0.3, max_tokens=100, timeout=15,
        ).strip().strip('"')
    except Exception as e:
        print(f"Erro ao gerar introdução: {e}")
        return None

def synthesize_answer(question, result_json, provider=None):
    """Resposta em Markdown: frase de contexto (LLM) + tabela determinística (Python).

    A tabela é montada em Python para garantir fidelidade total dos nomes
    (que contêm | e < >); o LLM cuida apenas da narrativa de contexto.
    """
    rows = dedupe_bindings(result_json)
    if not rows:
        return None

    # Valor único (ex.: contagem) -> frase objetiva, determinística
    if len(rows) == 1 and len(rows[0]) == 1:
        value = list(rows[0].values())[0]
        return f"A consulta retornou: **{value}**."

    table = build_markdown_table(rows)
    # No modo local (ollama) evitamos uma 2ª chamada ao LLM (latência): intro determinística.
    intro = None if provider == "ollama" else generate_intro(question, len(rows), provider=provider)
    if not intro:
        intro = f"Encontrei **{len(rows)}** resultado(s) para a sua consulta:"

    return f"{intro}\n\n{table}\n\n*Total: {len(rows)} registro(s).*"

def extract_initiatives_from_results(result_json):
    """Extrai nomes de iniciativas dos resultados SPARQL."""
    if not result_json or "results" not in result_json:
        return []
    
    bindings = result_json["results"].get("bindings", [])
    initiatives = []
    
    for b in bindings:
        if "initiativeName" in b:
            name = b["initiativeName"].get("value", "").strip()
            if name and name not in initiatives:
                initiatives.append(name)
    
    return initiatives

def search_web_about_initiative(initiative_name, country=None):
    """Busca informações na web sobre uma iniciativa usando múltiplas fontes."""
    try:
        # Monta a query de busca
        search_query = f"{initiative_name}"
        if country:
            search_query += f" {country}"
        search_query += " women technology STEM initiative"
        
        results = {
            "initiative": initiative_name,
            "abstract": "",
            "abstract_url": "",
            "related_topics": []
        }
        
        # Estratégia 1: DuckDuckGo Instant Answer API
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": search_query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get("Abstract"):
                results["abstract"] = data.get("Abstract", "")
                results["abstract_url"] = data.get("AbstractURL", "")
            
            # Adiciona tópicos relacionados
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and "Text" in topic:
                    results["related_topics"].append({
                        "text": topic.get("Text", ""),
                        "url": topic.get("FirstURL", "")
                    })
        except:
            pass
        
        # Estratégia 2: Se DuckDuckGo não retornou nada, tenta busca HTML simples
        if not results["abstract"] and not results["related_topics"]:
            try:
                # Busca no Google (usando user agent para evitar bloqueio)
                search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(search_url, headers=headers, timeout=5, verify=False)
                
                if response.status_code == 200:
                    # Extrai snippets simples do HTML
                    snippets = re.findall(r'<div class="[^"]*BNeawe[^"]*">([^<]+)</div>', response.text)
                    
                    if snippets:
                        # Pega os primeiros snippets relevantes
                        clean_snippets = [s.strip() for s in snippets if len(s.strip()) > 50][:3]
                        
                        if clean_snippets:
                            results["abstract"] = clean_snippets[0]
                            results["abstract_url"] = search_url
                            
                            for snippet in clean_snippets[1:]:
                                results["related_topics"].append({
                                    "text": snippet,
                                    "url": search_url
                                })
            except:
                pass
        
        # Estratégia 3: Sempre retorna links úteis de busca
        if not results["abstract"] and not results["related_topics"]:
            # Gera descrição genérica mas informativa
            results["abstract"] = f"Esta é uma iniciativa do Projeto ELLAS focada em mulheres, tecnologia e STEM. Clique nos links abaixo para pesquisar mais informações sobre '{initiative_name}'."
            results["abstract_url"] = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            
            # Fornece um único link de busca útil (evita poluir a resposta)
            busca = f"{initiative_name} {country}".strip() if country else initiative_name
            results["related_topics"] = [
                {
                    "text": f"🔍 Buscar '{initiative_name}' no Google",
                    "url": f"https://www.google.com/search?q={requests.utils.quote(busca + ' women in tech STEM')}"
                }
            ]
        
        return results
        
    except Exception as e:
        return {
            "initiative": initiative_name,
            "abstract": f"Não foi possível buscar informações online no momento. Tente pesquisar diretamente: '{initiative_name}'",
            "abstract_url": f"https://www.google.com/search?q={requests.utils.quote(initiative_name if initiative_name else 'ELLAS initiative')}",
            "related_topics": [],
            "error": str(e)
        }

def analyze_query_intent(question):
    """Analisa se a pergunta solicita busca web adicional."""
    web_keywords = [
        "buscar", "pesquisar", "procurar", "informação", "informacao",
        "mais sobre", "detalhe", "detalhes", "web", "internet",
        "encontrar", "google", "site", "website", "sobre",
        "o que", "quem", "qual", "descri", "iniciativa"
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in web_keywords)

def extract_initiative_name_from_question(question):
    """Tenta extrair nome de iniciativa da pergunta do usuário."""
    # Remove palavras comuns
    stop_words = ['sobre', 'a', 'o', 'que', 'quem', 'qual', 'e', 'é', 'é', 'da', 'do', 'de', 'informação', 'informacao', 
                  'informações', 'informacoes', 'buscar', 'pesquisar', 'procurar',
                  'gostaria', 'quero', 'mostre', 'me', 'diga', 'conte', 'fale',
                  'fazer', 'um', 'uma', 'pão', 'pao', 'web', 'na', 'apenas',
                  'iniciativa', 'iniciativas']
    
    # Limpa a pergunta
    question_lower = question.lower()
    question_clean = re.sub(r'\([^)]*\)', '', question_lower).strip()
    question_clean = re.sub(r'[\?\!\.,;:\"]', ' ', question_clean)
    
    words = question_clean.split()
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Retorna as palavras restantes como possível nome de iniciativa
    if filtered_words:
        return ' '.join(filtered_words)
    
    # Se não encontrou nada, retorna a pergunta original limpa
    return question_clean.strip() if question_clean.strip() else None

# =============================================================================
# 🌐 ROTAS DA API
# =============================================================================
@app.route('/api/query', methods=['POST'])
def handle_query():
    """Endpoint principal: agente NL->SPARQL ancorado + auto-correção, com fallback web."""
    data = request.json
    question = data.get('question', '')
    enable_web_search = data.get('web_search', False)  # Flag opcional
    provider = (data.get('provider') or LLM_PROVIDER)  # "groq" ou "ollama"

    if not question.strip():
        return jsonify({"error": "Pergunta vazia"}), 400

    should_search_web = enable_web_search or analyze_query_intent(question)

    # 1) Agente consulta o grafo (recupera exemplos, gera, valida, executa, corrige)
    agent_res = run_agent(question, provider=provider)
    db_results = agent_res["results"]
    sparql_query = agent_res["sparql"]
    agent_error = agent_res["error"]
    has_data = (db_results is not None and agent_error is None
                and count_bindings(db_results) > 0)

    # Transparência do agente (útil para a dissertação)
    agent_info = {
        "matched_questions": agent_res["matched_questions"][:3],
        "n_attempts": agent_res["n_attempts"],
        "relaxed": agent_res["relaxed"],
    }

    if has_data:
        # Síntese em Markdown (tabela fiel + frase de contexto), com fallback ao texto bruto
        formatted_answer = format_results(db_results)
        synthesized = synthesize_answer(question, db_results, provider=provider)
        answer_md = synthesized if synthesized else formatted_answer

        response_data = {
            "success": True,
            "answer": answer_md,
            "sparql": sparql_query,
            "raw_results": db_results,
            "generation_time": agent_res["elapsed"],
            "agent": agent_info,
            "provider": provider,
            "web_search_performed": False,
            "web_results": None,
        }

        # Enriquecimento IA/Web só em buscas focadas (poucas iniciativas)
        if should_search_web:
            initiatives = extract_initiatives_from_results(db_results)
            if initiatives and len(initiatives) <= 3:
                web_results = []
                for initiative in initiatives:
                    llm_knowledge = query_llm_knowledge(initiative, provider=provider)
                    web_info = search_web_about_initiative(initiative)
                    if llm_knowledge or web_info.get("abstract") or web_info.get("related_topics"):
                        web_info["llm_knowledge"] = llm_knowledge
                        web_results.append(web_info)
                if web_results:
                    response_data["web_search_performed"] = True
                    response_data["web_results"] = web_results

        return jsonify(response_data)

    # 2) Sem dados no grafo -> fallback IA/Web (se habilitado)
    if should_search_web:
        initiative_name = extract_initiative_name_from_question(question)
        if initiative_name:
            llm_knowledge = query_llm_knowledge(initiative_name, provider=provider)
            web_info = search_web_about_initiative(initiative_name)
            web_results = []
            if llm_knowledge or web_info.get("abstract") or web_info.get("related_topics"):
                web_info["llm_knowledge"] = llm_knowledge
                web_results.append(web_info)
            return jsonify({
                "success": True,
                "answer": "Não encontrei dados no grafo ELLAS para essa pergunta, mas busquei informações:",
                "sparql": sparql_query,
                "agent": agent_info,
                "web_search_performed": True,
                "web_results": web_results,
            })

    # 3) Nada encontrado
    msg = ("A consulta ao grafo falhou após tentativas de correção automática."
           if agent_error else
           "Não encontrei dados no grafo ELLAS para essa pergunta.")
    return jsonify({
        "success": False,
        "message": msg,
        "sparql": sparql_query,
        "error": agent_error,
        "agent": agent_info,
    })

@app.route('/api/web-search', methods=['POST'])
def handle_web_search():
    """Endpoint dedicado para busca web sobre iniciativas."""
    data = request.json
    initiative_name = data.get('initiative', '')
    country = data.get('country', None)
    
    if not initiative_name.strip():
        return jsonify({"error": "Nome da iniciativa não fornecido"}), 400
    
    # Busca com LLM + Web
    llm_knowledge = query_llm_knowledge(initiative_name, country)
    web_info = search_web_about_initiative(initiative_name, country)
    web_info["llm_knowledge"] = llm_knowledge
    
    return jsonify(web_info)

@app.route('/api/direct-search', methods=['POST'])
def handle_direct_search():
    """Endpoint para busca direta na web sem passar pelo grafo."""
    data = request.json
    query = data.get('query', '')
    
    if not query.strip():
        return jsonify({"error": "Query vazia"}), 400
    
    # Tenta extrair nome da iniciativa
    initiative_name = extract_initiative_name_from_question(query)
    
    if not initiative_name:
        return jsonify({
            "success": False,
            "message": "Não consegui identificar uma iniciativa na sua pergunta."
        })
    
    # 🤖 Busca com LLM + Web
    llm_knowledge = query_llm_knowledge(initiative_name)
    web_info = search_web_about_initiative(initiative_name)
    
    if llm_knowledge or web_info.get("abstract") or web_info.get("related_topics"):
        web_info["llm_knowledge"] = llm_knowledge
        return jsonify({
            "success": True,
            "answer": f"Informações encontradas sobre '{initiative_name}':",
            "web_search_performed": True,
            "web_results": [web_info]
        })
    else:
        return jsonify({
            "success": False,
            "message": f"Não encontrei informações sobre '{initiative_name}'.",
            "web_search_performed": True,
            "web_results": []
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica se a API está funcionando."""
    return jsonify({"status": "online", "service": "ELLAS Agent API"})

@app.route('/', methods=['GET'])
def serve_index():
    """Serve a interface web estática principal."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve arquivos estáticos do diretório principal."""
    try:
        return send_from_directory('.', path)
    except Exception:
        return jsonify({"error": "Arquivo não encontrado"}), 404

if __name__ == '__main__':
    print("🚀 ELLAS Agent API iniciada!")
    print("📍 Endpoint: http://localhost:5000")
    print("🤖 Busca LLM habilitada!")
    app.run(debug=True, port=5000)
