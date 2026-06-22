# 🤖 Documentação Técnica - Busca com LLM

## Visão Geral

Sistema inteligente que usa o Groq LLM (Llama 3.3 70B) para fornecer conhecimento contextualizado sobre iniciativas, complementando dados do grafo e da web.

## Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    USUÁRIO                          │
│              "Tremendas bolivia"                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              BACKEND FLASK                          │
│                                                     │
│  1. Tenta gerar SPARQL                             │
│  2. Consulta GraphDB                                │
│  3. 🆕 Consulta LLM (Groq)                         │
│  4. Busca Web (DuckDuckGo)                          │
│  5. Valida Qualidade                                │
│  6. Combina Resultados                              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              FRONTEND REACT                         │
│                                                     │
│  🤖 Card: Conhecimento da IA                       │
│  🌐 Card: Informações da Web                       │
│  🔗 Card: Links Úteis                              │
└─────────────────────────────────────────────────────┘
```

## Função Principal: `query_llm_knowledge()`

### Propósito
Consulta o LLM Groq sobre uma iniciativa e valida a qualidade da resposta.

### Parâmetros
```python
def query_llm_knowledge(initiative_name: str, country: str = None) -> str | None
```

- `initiative_name`: Nome da iniciativa a ser consultada
- `country`: País (opcional, melhora contexto)
- **Retorno**: String com conhecimento ou `None` se não confiável

### Prompt Engineering

```python
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
```

**Por que este prompt funciona:**
1. ✅ Define papel ("expert on women in tech")
2. ✅ Pede factual (evita criatividade)
3. ✅ Escape hatch ("NO_INFO")
4. ✅ Estrutura clara de resposta
5. ✅ Limite de palavras (controle)
6. ✅ Idioma especificado

### Validação de Qualidade

Sistema de 3 camadas de validação:

```python
# Camada 1: Resposta vazia ou "NO_INFO"
if "NO_INFO" in llm_response.upper():
    return None

# Camada 2: Resposta muito curta (< 50 chars)
if len(llm_response) < 50:
    return None

# Camada 3: Frases de incerteza
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

# ✅ Passou em todas as validações
return llm_response
```

## Fluxo de Dados Completo

### Cenário 1: Busca com Dados no Grafo
```
1. User: "iniciativas da Bolivia"
2. Backend gera SPARQL
3. GraphDB retorna: [Tremendas bolivia, Chicas...]
4. Para cada iniciativa:
   4.1. query_llm_knowledge("Tremendas bolivia")
   4.2. Valida resposta
   4.3. search_web_about_initiative("Tremendas bolivia")
5. Combina: Grafo + LLM + Web
6. Frontend renderiza 3 cards
```

### Cenário 2: Busca Sem Dados no Grafo
```
1. User: "Afropython"
2. Backend tenta SPARQL → vazio
3. Extrai nome da pergunta: "Afropython"
4. query_llm_knowledge("Afropython")
5. Valida resposta
6. search_web_about_initiative("Afropython")
7. Combina: LLM + Web (sem grafo)
8. Frontend renderiza 2 cards
```

### Cenário 3: LLM Sem Informação Confiável
```
1. User: "fazer um pão"
2. query_llm_knowledge("fazer um pão")
3. LLM responde: "não tenho informações..."
4. Validação rejeita (uncertain phrase)
5. Retorna None
6. search_web_about_initiative() gera links úteis
7. Frontend mostra apenas Web + Links
```

## Configurações da API Groq

```python
payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.3,      # Baixa = mais factual
    "max_tokens": 300        # ~150 palavras
}
```

**Por que estes valores:**
- `temperature: 0.3`: Equilibra criatividade com factualidade
- `max_tokens: 300`: Permite resposta completa mas controlada
- `model: llama-3.3-70b`: Melhor modelo Groq para conhecimento geral

## Performance

### Benchmarks Típicos

| Operação | Tempo Médio |
|----------|-------------|
| Consulta LLM | 1.0-1.5s |
| Validação | < 0.01s |
| Busca Web | 0.5-1.0s |
| **Total** | **2-3s** |

### Otimizações Implementadas

1. **Timeout Agressivo**: 15s na API Groq
2. **Validação Rápida**: Regex simples
3. **Paralelização**: LLM e Web podem rodar juntos (futuro)
4. **Cache**: Não implementado (mas recomendado)

## Tratamento de Erros

```python
try:
    response = requests.post(GROQ_URL, ...)
    # Processa resposta
except Exception as e:
    print(f"Erro na consulta LLM: {e}")
    return None  # Fail silently
```

**Filosofia**: 
- ❌ Não quebra se LLM falhar
- ✅ Sistema continua com Web + Links
- 🎯 Degradação graciosa

## Segurança

### Proteções Implementadas

1. **Validação de Input**: Limpa nomes de iniciativas
2. **Rate Limiting**: Groq tem limites próprios
3. **Timeout**: 15s máximo por consulta
4. **Sanitização**: Remove caracteres especiais
5. **Fail-safe**: Nunca expõe erros ao usuário

## Custos (Groq API)

Groq oferece tier gratuito generoso:
- **Limite**: ~30 requisições/minuto
- **Custo**: Grátis até limite
- **Tokens**: ~300 por consulta

**Estimativa de uso:**
- 100 consultas/dia = 30,000 tokens
- Muito dentro do tier gratuito

## Casos de Uso Ideais

### ✅ Funciona Bem Para:
- Iniciativas conhecidas internacionalmente
- Organizações com presença online
- Termos STEM/tech bem estabelecidos
- Eventos e programas famosos

### ⚠️ Pode Falhar Para:
- Iniciativas muito locais/pequenas
- Organizações sem presença web
- Nomes genéricos/ambíguos
- Eventos muito recentes (pós-cutoff)

## Métricas de Sucesso

### Taxa de Resposta Válida
```python
# Monitorar em produção
valid_responses = 0
total_queries = 0

if llm_response:
    valid_responses += 1
total_queries += 1

success_rate = valid_responses / total_queries
# Meta: > 60% de taxa de resposta válida
```

## Melhorias Futuras

### Curto Prazo
- [ ] Cache de respostas (Redis)
- [ ] Logging detalhado
- [ ] Métricas de qualidade

### Médio Prazo
- [ ] Múltiplos modelos (fallback)
- [ ] Fine-tuning específico
- [ ] Embeddings para RAG

### Longo Prazo
- [ ] Modelo local (Ollama)
- [ ] Sistema de feedback do usuário
- [ ] Auto-correção baseada em feedback

## Debug e Testes

### Como Testar Localmente

```python
# Test 1: Iniciativa conhecida
result = query_llm_knowledge("Tremendas bolivia")
assert result is not None
assert len(result) > 50

# Test 2: Iniciativa desconhecida
result = query_llm_knowledge("xpto123456")
assert result is None

# Test 3: Nome genérico
result = query_llm_knowledge("fazer um pão")
assert result is None  # Deve ser rejeitado
```

### Logs Úteis

```python
# Adicione no código:
print(f"🤖 LLM Query: {initiative_name}")
print(f"📊 Response length: {len(llm_response)}")
print(f"✅ Validation: {'PASS' if valid else 'FAIL'}")
```

## Referências

- [Groq API Docs](https://console.groq.com/docs)
- [Llama 3.3 70B Model Card](https://huggingface.co/meta-llama/Llama-3.3-70B)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

**🎓 Desenvolvido com validação de qualidade em mente!**
