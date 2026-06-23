"""Carrega o arquivo RDF/Turtle gerado pelo OntoRefine (etapa GerarRDF.bat)
no repositório GraphDB, via a API REST de statements do RDF4J/GraphDB.

Último passo da pipeline de ingestão, executado após GravarRDF.bat.
"""
import requests

from config import GRAPH_URL, GRAPH_USER, GRAPH_PASS, RDF_FILE_PATH

url = f"{GRAPH_URL}/statements"

headers = {
    "Content-Type": "text/turtle",
}

data = open(RDF_FILE_PATH, "rb").read()

response = requests.post(url, headers=headers, data=data, auth=(GRAPH_USER, GRAPH_PASS))

if response.status_code == 204:
    print("Arquivo Turtle importado com sucesso!")
else:
    print("Erro ao importar o arquivo Turtle:", response.text)

