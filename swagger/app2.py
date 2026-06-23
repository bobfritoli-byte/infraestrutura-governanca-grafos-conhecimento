from flask import Flask, render_template, request, jsonify
from flask_restx import Api, Resource, fields
import requests

from config import GRAPH_URL, GRAPH_USER, GRAPH_PASS

app = Flask(__name__)
api = Api(app, version='1.0', title='ELLAS SPARQL API', description='SPARQL API - Competence Questions')

# Configuração do diretório estático
app.static_folder = 'static'

# Rota para os arquivos estáticos (CSS, JS, imagens)
@app.route('/static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

@app.route('/')
def index():
    return render_template('index.html')

ns = api.namespace('sparql', description='SPARQL operations')

query_parser = ns.parser()
query_parser.add_argument('countryName', type=str, required=True, help='Name of the country')

username = GRAPH_USER
password = GRAPH_PASS
url = GRAPH_URL

@ns.route('/query_initiatives')
@ns.expect(query_parser)
class SPARQLInitiativesQuery(Resource):
    @ns.response(200, 'Success')
    @ns.response(400, 'Validation Error')
    def get(self):
        '''Execute a SPARQL query to fetch initiatives'''
        args = query_parser.parse_args()
        country_name = args.get('countryName')
        if not country_name:
            ns.abort(400, 'countryName parameter is required')

        query = f"""
        PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?initiativeName ?countryName WHERE {{
            ?initiative a Ellas:Initiative.
            ?initiative rdfs:label ?initiativeName.
            ?initiative Ellas:created_in ?country.
            ?country rdfs:label ?countryName.
            FILTER(?countryName="{country_name}"@en).
        }}
        """

        headers = {'Accept': 'application/sparql-results+json'}
        auth = (username, password)
        params = {'query': query}

        response = requests.get(url, headers=headers, auth=auth, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': 'Failed to execute query'}, response.status_code

@ns.route('/query_policies')
class SPARQLPoliciesQuery(Resource):
    @ns.response(200, 'Success')
    @ns.response(400, 'Validation Error')
    def get(self):
        '''Execute a SPARQL query to fetch policies'''
        query = """
        PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?policyName ?countryName WHERE {
            ?policy a Ellas:Policy.
            ?policy rdfs:label ?policyName.
            ?policy Ellas:created_in ?country.
            ?country rdfs:label ?countryName.
        }
        """

        headers = {'Accept': 'application/sparql-results+json'}
        auth = (username, password)
        params = {'query': query}

        response = requests.get(url, headers=headers, auth=auth, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': 'Failed to execute query'}, response.status_code

api.add_namespace(ns)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
