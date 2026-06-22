# Infraestrutura para a Governança de Grafos de Conhecimento

Produto técnico-científico da dissertação de mestrado **"Infraestrutura para a
Governança de Grafos de Conhecimento: o Caso da Plataforma ELLAS"**
(PPGCA/UTFPR). Este repositório documenta e disponibiliza, de forma
generalizável, a arquitetura de referência proposta para a governança técnica
de grafos de conhecimento (RDF/SPARQL) em projetos de médio porte com
restrições orçamentárias — validada na prática por meio da instanciação
concreta na plataforma [ELLAS](https://ellas.ufmt.br) (dados abertos sobre
liderança feminina em STEM na América Latina).

## Visão geral da arquitetura

A arquitetura organiza-se em cinco componentes principais, dispostos segundo o
padrão *Onion Architecture* (domínio no núcleo, infraestrutura e interfaces
nas camadas externas):

1. **Origem e Infraestrutura** — dados de entrada (planilhas CSV) e ambiente
   computacional que sustenta a execução (instância de nuvem ou servidor
   físico).
2. **Pipeline de Dados e Processamento** — ingestão, limpeza/mapeamento
   semântico e triplificação dos dados em RDF.
3. **Triplestore** — armazenamento e consulta dos dados em grafo via SPARQL
   (GraphDB).
4. **Exposição por API** — camada de API REST documentada (Swagger),
   tornando o grafo consultável por aplicações externas.
5. **Saídas e Consumo** — interfaces de consulta para o usuário final,
   incluindo o agente conversacional baseado em LLM deste repositório.

Cada componente é desacoplado dos demais: a camada de ingestão pode ser
adaptada a outras fontes/domínios de dados sem alterar a triplificação, a
persistência ou a exposição via API — é isso que torna a arquitetura
reutilizável além do caso ELLAS.

## Estrutura deste repositório

```
.
├── docs/                    # Guia de implantação passo a passo (este README resume; docs/ detalha)
├── agente-llm/              # Agente conversacional (NL -> SPARQL) via LLM
│   ├── app.py                  # API Flask
│   ├── agent.py                # Lógica de busca/matching de competency questions
│   ├── config.py               # Configuração (lê credenciais do .env, sem valores padrão)
│   ├── schema_ellas.py         # Esquema da ontologia usado para orientar o LLM
│   ├── Ellas.owl               # Ontologia de exemplo (instância validada: ELLAS)
│   ├── Query_SPARQL.txt        # Catálogo de competency questions (gabarito)
│   ├── evaluate.py             # Script de avaliação do agente
│   ├── evaluation_report.*     # Resultados de avaliação (instância ELLAS)
│   ├── index.html              # Interface web (SPA)
│   ├── .env.example            # Modelo de variáveis de ambiente (sem segredos)
│   └── docs/                   # Documentação técnica complementar do agente
├── query-builder/           # Apps de consulta/exploração direta via SPARQL
│   ├── ConsultaSparql.py        # Editor livre de consultas SPARQL (Streamlit)
│   ├── Teste.py                 # Explorador por catálogo de competency questions
│   ├── EllasBI.py               # Painel simples de indicadores (políticas por país)
│   ├── sparql_queries.py        # Catálogo de competency questions (Python)
│   ├── apiService.ts            # Mesmo catálogo, em TypeScript (para frontend)
│   ├── config.py                # Configuração (lê credenciais do .env, sem valores padrão)
│   └── .env.example             # Modelo de variáveis de ambiente (sem segredos)
└── LICENSE
```

> **Nota sobre os dados de exemplo:** `Ellas.owl`, `Query_SPARQL.txt` e os
> relatórios de avaliação refletem a instanciação concreta validada no
> projeto ELLAS, uma **plataforma de dados abertos**. Nenhuma credencial ou
> dado pessoal está incluído neste repositório — veja `.env.example` para a
> configuração necessária.

## Guia de implantação (passo a passo)

A instanciação validada nesta pesquisa segue a sequência abaixo. Cada etapa é
independente de fornecedor específico — a arquitetura também pode ser
implantada em servidor físico/on-premises substituindo apenas a etapa 1–2.

### 1. Provisionamento da infraestrutura (nuvem)

- Criar uma conta na AWS (ou provedor de nuvem equivalente).
- Provisionar uma instância EC2 com Windows Server. Para o volume de dados de
  um projeto de médio porte (dezenas de milhares de triplas), uma instância
  de baixo custo é suficiente — a prototipação original operou com custo
  médio em torno de US\$ 15/mês.
- Liberar as portas necessárias (RDP para administração; HTTP/HTTPS para a
  API e o GraphDB Workbench) no *security group* da instância.

### 2. Triplestore (GraphDB)

- Instalar o [GraphDB Desktop](https://www.ontotext.com/products/graphdb/) na
  instância.
- Criar um repositório RDF dedicado ao projeto.
- Carregar a ontologia do domínio (ver `agente-llm/Ellas.owl` como exemplo de
  estrutura) no repositório.
- Criar um usuário de acesso de leitura para a API/agente consultarem o
  repositório (nunca usar o usuário administrador para isso).

### 3. Pipeline de ingestão e triplificação (Pentaho)

- Instalar o [Pentaho Data Integration Community
  Edition](https://www.hitachivantara.com/en-us/products/pentaho-platform/data-integration-analytics/pentaho-community-edition.html).
- Instalar o [OntoRefine](https://graphdb.ontotext.com/documentation/) (módulo
  do GraphDB para limpeza e mapeamento semântico de dados tabulares para RDF).
- Construir as transformações (*jobs*/*transformations* do Pentaho) que leem
  os arquivos CSV de origem, acionam o mapeamento OntoRefine e carregam o
  resultado triplificado no GraphDB.
- Instalar Python no servidor para os scripts auxiliares de pré-processamento
  que complementam o pipeline.

> **Status:** os arquivos de transformação do Pentaho (`.ktr`/`.kjb`) usados
> na instância ELLAS ainda não foram adicionados a este repositório —
> pendência a resolver em uma próxima atualização.

### 4. Exposição por API

- Implementar uma API REST (Flask ou framework equivalente) que execute
  consultas SPARQL contra o GraphDB e retorne os resultados em JSON.
- Documentar os endpoints via Swagger/OpenAPI, expondo uma interface de
  consulta autodescritiva para consumidores externos.

### 5. Interface de consulta e agente conversacional (LLM)

- A pasta [`agente-llm/`](./agente-llm) deste repositório contém uma
  implementação completa desta camada: uma interface web que traduz
  perguntas em linguagem natural para consultas SPARQL via LLM, executa a
  consulta contra o GraphDB e apresenta o resultado de forma estruturada.
  Veja [`agente-llm/README.md`](./agente-llm/README.md) para instruções de
  instalação e configuração.
- A pasta [`query-builder/`](./query-builder) complementa essa camada com
  apps de consulta e exploração direta do grafo (editor SPARQL livre,
  explorador por catálogo de *competency questions* e um painel simples de
  indicadores) — úteis para validação manual de queries e exploração técnica
  dos dados. Veja [`query-builder/README.md`](./query-builder/README.md).

## Citação

Se este trabalho for útil em sua pesquisa, por favor cite a dissertação:

```
FRITOLI, Rodgers. Infraestrutura para a Governança de Grafos de Conhecimento:
o Caso da Plataforma ELLAS. Dissertação (Mestrado em Computação Aplicada) —
Universidade Tecnológica Federal do Paraná, Curitiba, 2026.
```

## Licença

Distribuído sob a licença MIT — veja [LICENSE](./LICENSE).
