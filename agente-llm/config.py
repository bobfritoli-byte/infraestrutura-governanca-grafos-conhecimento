"""Configurações compartilhadas do Agente ELLAS.

Carrega o .env e centraliza o cliente de LLM (Groq na nuvem OU Ollama local),
usado por app.py, agent.py e evaluate.py.
"""
import os
import time

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Provedor padrão de LLM: "anthropic" (Haiku), "groq" (nuvem) ou "ollama" (local)
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").strip().lower()

# --- Anthropic (Claude Haiku) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

# --- Groq (nuvem) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Ollama (local) ---
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b")

# --- GraphDB (endpoint SPARQL EllasV2) ---
GRAPH_URL = os.environ.get("ELLAS_GRAPH_URL", "https://app.ellas.ufmt.br/repositories/EllasV2")
GRAPH_USER = os.environ.get("ELLAS_GRAPH_USER")
GRAPH_PASS = os.environ.get("ELLAS_GRAPH_PASS")
if not GRAPH_USER or not GRAPH_PASS:
    raise RuntimeError(
        "ELLAS_GRAPH_USER e ELLAS_GRAPH_PASS precisam ser definidas no .env "
        "(veja .env.example). Nenhuma credencial padrão é fornecida por questões de segurança."
    )
GRAPH_AUTH = (GRAPH_USER, GRAPH_PASS)

# Catálogo de competency questions (gabarito validado)
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "Query_SPARQL.txt")


# =============================================================================
# Cliente de LLM unificado
# =============================================================================
def _groq_chat(messages, temperature, max_tokens, timeout, max_retries=3, max_wait=8):
    """Chat via Groq (nuvem), com retry/backoff limitado (resiliente a 429)."""
    payload = {"model": GROQ_MODEL, "messages": messages, "temperature": temperature}
    if max_tokens:
        payload["max_tokens"] = max_tokens
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    last_resp = None
    for attempt in range(max_retries):
        resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=timeout, verify=False)
        if resp.status_code == 429:
            wait = float(resp.headers.get("retry-after") or 0) or (2 ** attempt)
            time.sleep(min(wait, max_wait))
            last_resp = resp
            continue
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    if last_resp is not None:
        last_resp.raise_for_status()
    raise RuntimeError("Groq: falha após múltiplas tentativas (rate limit).")


_anthropic_client = None


def _anthropic_chat(messages, temperature, max_tokens, timeout):
    """Chat via Anthropic (Claude Haiku), usando o SDK oficial `anthropic`.

    A API da Anthropic separa o prompt de sistema das mensagens; extraímos as
    mensagens de role 'system' e as passamos no parâmetro `system`.
    """
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic  # import tardio: dependência só é exigida se usar este provedor
        if not ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY não definida no .env")
        _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_parts = [m["content"] for m in messages if m["role"] == "system"]
    convo = [{"role": m["role"], "content": m["content"]}
             for m in messages if m["role"] != "system"]

    kwargs = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": max_tokens or 2048,
        "messages": convo,
        "temperature": temperature,
    }
    if system_parts:
        kwargs["system"] = "\n\n".join(system_parts)

    resp = _anthropic_client.with_options(timeout=timeout).messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text")


def _ollama_chat(messages, temperature, max_tokens, timeout):
    """Chat via Ollama (local). Sem rate limit; modelo definido em OLLAMA_MODEL."""
    options = {"temperature": temperature}
    if max_tokens:
        options["num_predict"] = max_tokens
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": options,
        "keep_alive": "30m",  # mantém o modelo na memória entre chamadas
    }
    # Modelos locais podem ser mais lentos -> timeout mais generoso
    resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=max(timeout, 180))
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def llm_chat(messages, provider=None, temperature=0.0, max_tokens=None, timeout=30):
    """Roteia a chamada para o provedor escolhido (default: LLM_PROVIDER do .env)."""
    provider = (provider or LLM_PROVIDER).strip().lower()
    if provider == "ollama":
        return _ollama_chat(messages, temperature, max_tokens, timeout)
    if provider == "anthropic":
        return _anthropic_chat(messages, temperature, max_tokens, timeout)
    return _groq_chat(messages, temperature, max_tokens, timeout)


# Compat: nome antigo
def groq_chat(messages, temperature=0.0, max_tokens=None, timeout=30, **_):
    return llm_chat(messages, provider="groq", temperature=temperature,
                    max_tokens=max_tokens, timeout=timeout)
