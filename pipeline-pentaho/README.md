# Pipeline Pentaho — Ingestão e Triplificação (camada 2)

Implementação de referência da camada **Pipeline de Dados e Processamento**
da arquitetura: orquestração via Pentaho Data Integration (Kettle), com a
limpeza/mapeamento semântico e a triplificação executados via linha de
comando do OntoRefine. Na instância validada (ELLAS), o pipeline foi mantido
deliberadamente simples — orientado a linha de comando, sem dependências
adicionais de infraestrutura.

## Estrutura

```
.
├── Orchestration of the KG Ellas Data Pipeline.kjb   # Job principal (Pentaho Kettle): orquestra as etapas abaixo
├── PrimaryData.kjb                                    # Job de carga/preparação dos dados primários (CSV)
├── Exe/
│   ├── GerarProjeto.bat        # 1. Cria um projeto OntoRefine a partir do CSV de origem
│   ├── AplicaMapeamento.bat    # 2. Aplica o mapeamento semântico (mapping.json) ao projeto
│   ├── GerarRDF.bat            # 3. Exporta o projeto mapeado como RDF/Turtle (.ttl)
│   ├── GravarRDF.bat           # 4. Aciona o script Python que grava o .ttl no GraphDB
│   └── mapping.json            # Mapeamento semântico OntoRefine (CSV -> RDF), exemplo da instância ELLAS
├── EnviarArquvosRDF.py         # Script chamado por GravarRDF.bat: grava o .ttl no GraphDB via API REST
├── config.py                   # Configuração (lê credenciais do .env, sem valores padrão)
├── .env.example                 # Modelo de variáveis de ambiente (sem segredos)
└── requirements.txt
```

## Como funciona

1. O job Pentaho (`Orchestration of the KG Ellas Data Pipeline.kjb`) orquestra
   a execução de `PrimaryData.kjb` e dos scripts em `Exe/`, na ordem abaixo.
2. **`GerarProjeto.bat`** — usa o `ontorefine-cli` para criar um projeto
   OntoRefine a partir do CSV de origem.
3. **`AplicaMapeamento.bat`** — aplica o mapeamento semântico definido em
   `Exe/mapping.json` (regras de transformação de colunas do CSV em
   triplas RDF, conforme a ontologia do domínio) ao projeto criado.
4. **`GerarRDF.bat`** — exporta o resultado mapeado como arquivo
   RDF/Turtle (`.ttl`).
5. **`GravarRDF.bat`** — executa `EnviarArquvosRDF.py`, que faz o `POST`
   do `.ttl` gerado para o endpoint de *statements* do GraphDB, completando
   a carga no triplestore.

> **Nota:** os caminhos dentro dos arquivos `.bat` (ex.
> `C:\Users\Administrator\AppData\Local\Ontotext Refine\...`,
> `C:\EllasIntegration\...`) refletem a instância EC2/Windows Server validada
> nesta pesquisa — ajuste-os para o seu ambiente. Nenhuma credencial está
> presente nesses arquivos; o OntoRefine CLI usado aqui não exige autenticação
> por padrão (acesso local à instância).

## Instalação e configuração do script de carga

### Passo 1 — Dependências

```bash
pip install -r requirements.txt
```

### Passo 2 — Configuração

```bash
cp .env.example .env
```

Edite `.env` com a URL do seu repositório GraphDB e as credenciais de um
usuário com acesso de **escrita** (necessário para gravar as triplas).

### Passo 3 — Executar

```bash
python EnviarArquvosRDF.py
```

## Licença

Este componente segue a licença do repositório principal — veja
[LICENSE](../LICENSE).
