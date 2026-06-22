import streamlit as st
from pyvis.network import Network
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from config import GRAPH_URL, GRAPH_USER, GRAPH_PASS
from sparql_queries import (
    fetch_policies_applied_in_countries,
    fetch_policy_types_in_latin_america,
    fetch_policies_promoting_women_in_stem,
    fetch_policies_implemented_since_2015,
    fetch_initiatives_by_country,
    fetch_data_sources_for_initiatives,
    fetch_social_networks_for_initiatives,
    fetch_program_initiatives,
    fetch_public_private_initiatives,
)

st.set_page_config(
    layout="wide",
    page_title="Explorador de Competency Questions"
)

# Função para executar consultas SPARQL com autenticação
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
st.title("Exploração Interativa do Grafo de Conhecimento")
st.sidebar.title("Selecione uma Consulta")

# Opções de consultas SPARQL (catálogo de competency questions)
queries = {
    "Em quais países a política foi aplicada?": fetch_policies_applied_in_countries,
    "Quais tipos de políticas existem na América Latina?": fetch_policy_types_in_latin_america,
    "Como as políticas promovem a participação das mulheres em STEM?": fetch_policies_promoting_women_in_stem,
    "Quais políticas foram implementadas desde 2015?": fetch_policies_implemented_since_2015,
    "Quais iniciativas são realizadas no Brasil?": fetch_initiatives_by_country,
    "Quais fontes de dados são usadas nas iniciativas?": fetch_data_sources_for_initiatives,
    "Quais são as redes sociais das iniciativas?": fetch_social_networks_for_initiatives,
    "Quantas iniciativas são de programa?": fetch_program_initiatives,
    "As iniciativas são públicas ou privadas?": fetch_public_private_initiatives,
}

# Seleção da consulta no sidebar
query_name = st.sidebar.selectbox("Escolha uma consulta:", list(queries.keys()))
selected_query = queries[query_name]()

# Botão para executar a consulta
if st.sidebar.button("Executar Consulta"):
    # Executa a consulta selecionada
    result = execute_sparql(selected_query)

    if result:
        # Processa os resultados
        bindings = result["results"]["bindings"]
        df = pd.DataFrame([
            {key: value["value"] for key, value in binding.items()}
            for binding in bindings
        ])

        # Exibe a tabela com os resultados
        st.write("### Resultados da Consulta")
        st.dataframe(df)

        # Cria o grafo
        st.write("### Visualização do Grafo")
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

        # Adiciona nós e arestas ao grafo
        for _, row in df.iterrows():
            source = row.get("Source", "")
            target = row.get("Target", "")
            relationship = row.get("Relationship", "")

            if source and target:  # Certifica-se de que há um relacionamento
                net.add_node(source, label=source, color="#03DAC6")
                net.add_node(target, label=target, color="#BB86FC")
                net.add_edge(source, target, title=relationship)

        # Gera o arquivo HTML do grafo
        net.show_buttons(filter_=["physics"])  # Controles interativos
        net.save_graph("graph.html")

        # Renderiza o grafo no Streamlit
        with open("graph.html", "r") as f:
            html = f.read()
        st.components.v1.html(html, height=800)
    else:
        st.warning("Nenhum resultado encontrado para a consulta selecionada.")
