# 🌐 Guia de Uso da Busca Web

## Como Funciona

A busca web é uma funcionalidade poderosa que complementa os dados do banco ELLAS com informações da internet.

## 4 Formas de Ativar a Busca Web

### 1️⃣ Botão 🌐 WEB (NOVO!)

**O jeito mais fácil!** Use o botão verde "🌐 WEB" ao lado do botão "ENVIAR":

```
Digite: "Tremendas bolivia"
Clique: 🌐 WEB
Resultado: Busca APENAS na web, não consulta o grafo!
```

**Quando usar:**
- Quando o grafo não tem a informação que você procura
- Para buscar iniciativas que podem não estar cadastradas
- Para obter informações complementares rapidamente

### 2️⃣ Palavras-Chave Automáticas

O sistema detecta automaticamente quando você usa certas palavras:

**Palavras que ativam busca:**
- buscar, pesquisar, procurar
- informação, informacao
- mais sobre, detalhe, detalhes
- web, internet, google, site

**Exemplos:**
```
"Buscar informações sobre Tremendas bolivia"
"Pesquisar mais sobre iniciativas da Argentina"
"Quero mais detalhes sobre chicas por un cambio"
```

### 3️⃣ Toggle na Interface

Use o switch "Busca Web Automática" na parte inferior da tela:
- 🟢 **Ativado**: Todas as consultas que retornam iniciativas farão busca web
- 🔴 **Desativado**: Apenas consultas com palavras-chave farão busca web

### 4️⃣ Via API Diretamente

```bash
# Busca normal (grafo + web)
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Cite duas iniciativas da Bolivia",
    "web_search": true
  }'

# Busca apenas na web
curl -X POST http://localhost:5000/api/direct-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tremendas bolivia"
  }'
```

## Exemplos Práticos

### Cenário 1: Busca Web Direta (RECOMENDADO!)
```
Você: "Tremendas bolivia"
Botão: 🌐 WEB

Resultado:
🌐 Busca apenas na web (sem consultar grafo)
📄 Abstract, links e tópicos relacionados
⚡ Resposta rápida
```

### Cenário 2: Descobrir Iniciativas + Informações Web
```
Você: "Cite duas iniciativas da Bolivia"
Botão: ENVIAR [Toggle ativado]

Resultado:
✅ Dados do GraphDB (nomes, países)
🌐 Busca web automática sobre cada iniciativa
📊 Query SPARQL gerada
```

### Cenário 3: Busca Direcionada com Palavra-Chave
```
Você: "Buscar mais sobre Tremendas bolivia"
Botão: ENVIAR

Resultado:
✅ Tenta consultar GraphDB primeiro
🌐 Busca web (mesmo se não encontrar no grafo)
📄 Informações complementares
```

### Cenário 4: Consulta Simples (sem web)
```
Você: "Quantas iniciativas existem?"
Botão: ENVIAR [Toggle desativado, sem palavras-chave]

Resultado:
✅ Apenas dados do GraphDB
⚡ Resposta mais rápida
```

## O que a Busca Web Retorna

Para cada iniciativa encontrada:

1. **Abstract**: Resumo ou descrição da iniciativa
2. **URL**: Link para fonte de informação
3. **Tópicos Relacionados**: Links e textos relacionados
4. **Contexto Adicional**: Informações complementares

## Dicas de Uso

✅ **Quando usar busca web:**
- Quer saber mais sobre uma iniciativa específica
- Precisa de contexto além dos dados estruturados
- Está explorando iniciativas que não conhece

❌ **Quando NÃO usar busca web:**
- Consultas rápidas de contagem
- Já conhece as iniciativas
- Quer apenas dados estruturados
- Precisa de resposta mais rápida

## Performance

- **Sem busca web**: ~1-2 segundos
- **Com busca web**: ~3-5 segundos (depende do número de iniciativas)

## Fonte de Dados Web

A busca utiliza **DuckDuckGo API**, que:
- ✅ Não requer chave de API
- ✅ Respeita privacidade
- ✅ Retorna resultados relevantes
- ✅ É gratuita

## Limitações

- Máximo de 5 iniciativas por consulta
- Timeout de 5 segundos por busca
- Depende da disponibilidade da DuckDuckGo API
- Resultados podem variar conforme disponibilidade online

## Troubleshooting

**Busca não retorna resultados?**
→ Nem todas as iniciativas têm informações disponíveis publicamente

**Erro na busca web?**
→ O sistema continua funcionando, apenas sem informações adicionais

**Busca muito lenta?**
→ Desative o toggle para consultas rápidas

---

💡 **Dica Pro**: Combine consultas específicas com busca web para obter o máximo de informação!
