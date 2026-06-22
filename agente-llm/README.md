# Agente Conversacional — Consulta ao Grafo de Conhecimento via LLM

Interface de consulta em linguagem natural para o grafo de conhecimento,
implementando a camada de "Saídas e Consumo" da arquitetura de referência
(veja o [README principal](../README.md)). Traduz perguntas em português para
consultas SPARQL usando um LLM, executa a consulta contra o triplestore
(GraphDB) e apresenta o resultado de forma estruturada — combinando grafo,
conhecimento do próprio LLM e busca web complementar quando necessário.

Implementado e validado na instância concreta da plataforma ELLAS, mas
desacoplado do domínio de dados específico: basta apontar para outro
repositório GraphDB e ontologia para reutilizar em outro projeto.

## Características

- Tradução automática de perguntas em linguagem natural para SPARQL.
- Suporte a três provedores de LLM intercambiáveis: Anthropic (Claude Haiku),
  Groq (Llama 3.3, nuvem) ou Ollama (modelo local, sem custo de API).
- Busca complementar na web para perguntas fora do escopo do grafo, com
  validação automática de qualidade da resposta do LLM (evita expor
  alucinações como se fossem fatos do grafo).
- Visualização da query SPARQL gerada, para transparência e depuração.
- Métricas de uso em tempo real (total de consultas, tempo médio de
  resposta, taxa de sucesso).

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Acesso a um repositório GraphDB (próprio ou o endpoint público do ELLAS)
- Uma chave de API (Anthropic ou Groq) **ou** uma instância local do
  [Ollama](https://ollama.com/)

### Passo 1 — Dependências

```bash
pip install -r requirements.txt
```

### Passo 2 — Configuração

```bash
cp .env.example .env
```

Edite `.env` e preencha:
- A chave de API do provedor de LLM escolhido (`ANTHROPIC_API_KEY` ou
  `GROQ_API_KEY`), **ou** configure `OLLAMA_URL`/`OLLAMA_MODEL` para usar um
  modelo local.
- `ELLAS_GRAPH_URL`, `ELLAS_GRAPH_USER` e `ELLAS_GRAPH_PASS` apontando para o
  seu repositório GraphDB. Não há valor padrão — essas três variáveis são
  obrigatórias.

### Passo 3 — Executar

```bash
python app.py
```

O servidor inicia em `http://localhost:5000`. Abra `index.html` no navegador
para usar a interface.

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | API Flask: endpoints de consulta e health-check |
| `agent.py` | *Matching* de perguntas contra o catálogo de competency questions |
| `config.py` | Carrega `.env` e centraliza o cliente de LLM (Anthropic/Groq/Ollama) |
| `schema_ellas.py` | Esquema da ontologia fornecido ao LLM como contexto |
| `Ellas.owl` | Ontologia de exemplo (instância validada: ELLAS) |
| `Query_SPARQL.txt` | Catálogo de competency questions com SPARQL de referência |
| `evaluate.py` | Script de avaliação do agente contra o catálogo |
| `index.html` | Interface web (SPA) |

## API

### `POST /api/query`
Processa uma pergunta consultando grafo + LLM + web.

```json
{
  "question": "Quantas iniciativas existem?",
  "web_search": true
}
```

### `POST /api/direct-search`
Busca apenas com LLM + web, sem consultar o grafo.

### `GET /api/health`
Verifica o status da API.

## Limitações conhecidas

- **Dependência de API externa**: a disponibilidade do provedor de LLM em
  nuvem (Anthropic/Groq) é necessária quando não se usa Ollama local.
- **Qualidade das respostas do LLM**: o modelo pode eventualmente "alucinar"
  informações fora do grafo; a validação por execução efetiva da query
  SPARQL mitiga esse risco para respostas baseadas no triplestore.
- **Suporte a idiomas**: o esquema e os exemplos fornecidos ao LLM estão em
  português/inglês; outros idiomas não foram validados.

## Documentação complementar

Veja a pasta [`docs/`](./docs) para guias adicionais sobre o funcionamento da
busca web e detalhamento técnico da integração com o LLM.

## Licença

Este componente segue a licença do repositório principal — veja
[LICENSE](../LICENSE).
