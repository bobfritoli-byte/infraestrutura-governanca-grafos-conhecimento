# 🚀 GUIA DE INÍCIO RÁPIDO

## Instalação em 3 Passos

### 1️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Iniciar o Servidor Backend
```bash
python app.py
```

Você verá:
```
🚀 ELLAS Agent API iniciada!
📍 Endpoint: http://localhost:5000
🤖 Busca LLM habilitada!
```

### 3️⃣ Abrir a Interface
- Abra o arquivo `index.html` no navegador
- Ou arraste para uma janela do navegador

## 🎯 Como Testar a Nova Feature de IA

### Teste 1: Busca com IA + Grafo
```
Digite: "Tremendas bolivia"
Clique: ENVIAR (com toggle ativado)

Resultado:
🤖 Conhecimento da IA: [Explicação contextualizada]
📊 Dados do Grafo: [Se houver]
🌐 Info da Web: [Complementar]
```

### Teste 2: Busca Apenas com IA
```
Digite: "Afropython"
Clique: 🤖 IA (botão verde)

Resultado:
🤖 O que a IA sabe sobre Afropython
🌐 Links úteis para pesquisar
```

### Teste 3: Comparação
```
Teste A: "Tremendas bolivia" → Grafo vazio
Resultado: IA fornece contexto rico!

Teste B: "Quantas iniciativas existem?"
Resultado: Apenas grafo (mais rápido)
```

## 🎨 Interface

### 2 Botões Principais:
- **ENVIAR** (azul): Grafo + IA + Web
- **🤖 IA** (verde): Apenas IA + Web

### Toggle:
- 🟢 **Ativado**: Sempre busca IA + Web
- 🔴 **Desativado**: Apenas com palavras-chave

## 🤖 O que a IA Pode Fazer

✅ **Explicar iniciativas conhecidas**
✅ **Contextualizar resultados do grafo**
✅ **Fornecer informações complementares**
✅ **Validar automaticamente a qualidade**

❌ **Não faz:**
- Alucinar informações
- Responder sem certeza
- Substituir o grafo (complementa!)

## ⚡ Performance

- **Só Grafo**: ~1s
- **Grafo + IA**: ~2-3s
- **Só IA + Web**: ~2-4s

## 🎯 Exemplos de Perguntas

**Para usar IA:**
- "Tremendas bolivia"
- "Women Techmakers"
- "Afropython"
- "Chicas Waskiris"

**Para usar só Grafo:**
- "Quantas iniciativas?"
- "Liste países"
- "Status das iniciativas"

## 🐛 Problemas?

**IA não responde?**
→ Normal! Validação está funcionando (LLM não tem certeza)

**Muito lento?**
→ Desative o toggle para consultas rápidas

**Backend não inicia?**
→ Verifique se instalou as dependências

---

## 🎉 Pronto!

Agora você tem **Grafo + IA + Web** trabalhando juntos!

Teste com "**Tremendas bolivia**" para ver a mágica acontecer! ✨
