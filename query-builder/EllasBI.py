import streamlit as st
import pandas as pd
import requests

from config import GRAPH_URL, GRAPH_USER, GRAPH_PASS

st.set_page_config(
    layout="wide",
    page_title="Explorador de Competency Questions"
)

st.title("Politicas")

# Definindo a query SPARQL
# Em quais países a política foi aplicada?
query = """
  PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?policyName ?countryName where {
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.}
"""

# Definindo os headers para a requisição
headers = {'Accept': 'application/sparql-results+json'}
auth = (GRAPH_USER, GRAPH_PASS)
params = {'query': query}

# Fazendo a requisição para o endpoint do GraphDB
response = requests.get(GRAPH_URL, headers=headers, auth=auth, params=params)

# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    data = response.json()

    results = data['results']['bindings']
    df = pd.DataFrame(results)

    # Convertendo os valores dos campos do DataFrame
    df = df.map(lambda x: x['value'] if isinstance(x, dict) else x)

    # Total de Policies por pais
    policy_count = df.groupby("countryName")["policyName"].count().reset_index()
    policy_count.columns = ["countryName", "policy_count"]

    df_total = policy_count['policy_count'].sum()

    col1, col2 = st.columns(2)
    col1.metric(label="Total de Politicas", value=df_total, border=True)
    col2.metric(label="Média por País", value=df_total, border=True)

    policy_count.set_index("countryName", inplace=True)

    pais = policy_count.index.unique()
    pais = st.selectbox("País", pais)
    df_filtered = policy_count[policy_count.index == pais]
    st.bar_chart(df_filtered)

    st.dataframe(df)
else:
    st.error(f"Erro na consulta SPARQL: {response.status_code} - {response.text}")
