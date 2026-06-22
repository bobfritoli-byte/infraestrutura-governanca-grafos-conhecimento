import streamlit as st
from pyvis.network import Network
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from config import GRAPH_URL, GRAPH_USER, GRAPH_PASS

# Função para executar consultas SPARQL
def execute_sparql(query):
    headers = {"Accept": "application/sparql-results+json"}
    auth = HTTPBasicAuth(GRAPH_USER, GRAPH_PASS)
    response = requests.post(GRAPH_URL, data={"query": query}, headers=headers, auth=auth)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro na consulta SPARQL: {response.status_code} - {response.text}")
        return None

# Interface principal
st.set_page_config(layout="wide", page_title="Exploração SPARQL")
st.title("Plataforma Interativa de Consultas SPARQL")

# Entrada de texto para consulta SPARQL
st.sidebar.header("Consulta SPARQL")
query_input = st.sidebar.text_area("Digite sua consulta SPARQL aqui:", height=200)

# Botão para executar a consulta
if st.sidebar.button("Executar Consulta"):
    if query_input.strip():
        # Executa a consulta
        result = execute_sparql(query_input)

        if result:
            # Processa os resultados
            bindings = result["results"]["bindings"]
            if bindings:
                df = pd.DataFrame([
                    {key: value["value"] for key, value in binding.items()}
                    for binding in bindings
                ])

                # Exibe os resultados como tabela
                st.write("### Resultados da Consulta")
                st.dataframe(df)

                # Criação de grafo interativo (se houver colunas relevantes)
                if "Source" in df.columns and "Target" in df.columns:
                    st.write("### Visualização do Grafo")
                    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

                    # Adiciona nós e arestas ao grafo
                    for _, row in df.iterrows():
                        source = row.get("Source", "")
                        target = row.get("Target", "")
                        relationship = row.get("Relationship", "")

                        if source and target:  # Certifica-se de que há conexões
                            net.add_node(source, label=source, color="#03DAC6")
                            net.add_node(target, label=target, color="#BB86FC")
                            net.add_edge(source, target, title=relationship)

                    # Gera e renderiza o grafo
                    net.show_buttons(filter_=["physics"])
                    net.save_graph("graph.html")
                    with open("graph.html", "r") as f:
                        html = f.read()
                    st.components.v1.html(html, height=800)
                else:
                    st.info("A consulta não retornou colunas 'Source' e 'Target' para visualização do grafo.")
            else:
                st.warning("A consulta não retornou resultados.")
        else:
            st.error("Erro ao executar a consulta. Verifique o SPARQL.")
    else:
        st.warning("Por favor, insira uma consulta SPARQL válida.")
