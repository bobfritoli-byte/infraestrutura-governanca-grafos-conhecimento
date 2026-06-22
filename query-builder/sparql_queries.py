# sparql_queries.py

# Prefixos comuns para todas as consultas
PREFIXES = """
PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

# Em quais países a política foi aplicada?
def fetch_policies_applied_in_countries():
    return f"""
    {PREFIXES}
    SELECT ?policyName ?countryName WHERE {{
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
    }}
    """

# Quais tipos de políticas/processos/práticas de gênero existem na América Latina?
def fetch_policy_types_in_latin_america():
    return f"""
    {PREFIXES}
    SELECT ?policyName ?countryName ?policyType WHERE {{
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:policy_type ?policyType.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
    }}
    """

# Como as políticas identificadas/analisadas estão promovendo a participação das mulheres em STEM?
def fetch_policies_promoting_women_in_stem():
    return f"""
    {PREFIXES}
    SELECT ?policyName ?countryName ?policyResults WHERE {{
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:policy_description ?policyResults.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
    }}
    """

# Quais tipos de políticas/processos/práticas de gênero foram implementadas na Bolívia, Brasil e Peru desde 2015?
def fetch_policies_implemented_since_2015():
    return f"""
    {PREFIXES}
    SELECT ?policyName ?countryName ?start_date WHERE {{
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
      ?policy Ellas:start_date ?start_date.
      FILTER(xsd:integer(?start_date) > 2015)
      FILTER(
        regex(str(?countryName), "Peru", "i") || 
        regex(str(?countryName), "Brazil", "i") || 
        regex(str(?countryName), "Bolivia", "i")
      )
    }}
    """

# Quais e quantas iniciativas são realizadas no Brasil?
def fetch_initiatives_by_country():
    return f"""
    {PREFIXES}
    SELECT ?policyName ?countryName ?start_date WHERE {{
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
      ?policy Ellas:start_date ?start_date.
      FILTER(xsd:integer(?start_date) > 2015)
      FILTER(
        regex(str(?countryName), "Peru", "i") || 
        regex(str(?countryName), "Brazil", "i") || 
        regex(str(?countryName), "Bolivia", "i")
      )
    }}
    """

# Quais fontes de dados são usadas para a iniciativa?
def fetch_data_sources_for_initiatives():
    return f"""
    {PREFIXES}
    SELECT ?initiativeName ?countryName ?datasource WHERE {{
      ?initiative a Ellas:Initiative.
      ?initiative rdfs:label ?initiativeName.
      ?initiative Ellas:initiative_data_source ?datasource.
      ?initiative Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
    }}
    """

# Quais são as redes sociais da iniciativa?
def fetch_social_networks_for_initiatives():
    return f"""
    {PREFIXES}
    SELECT ?initiativeName ?countryName ?link WHERE {{
      ?initiative a Ellas:Initiative.
      ?initiative rdfs:label ?initiativeName.
      ?initiative Ellas:initiative_socialmedia_link ?link.
      ?initiative Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
    }}
    """

# Quantas iniciativas são de programa?
def fetch_program_initiatives():
    return f"""
    {PREFIXES}
    SELECT ?initiativeName ?countryName WHERE {{
      ?initiative a Ellas:Program.
      ?initiative rdfs:label ?initiativeName.
      ?initiative Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
    }}
    """

# As iniciativas são públicas ou privadas?
def fetch_public_private_initiatives():
    return f"""
    {PREFIXES}
    SELECT ?initiativeName ?countryName ?sector WHERE {{
      ?initiative a Ellas:Program.
      ?initiative rdfs:label ?initiativeName.
      ?initiative Ellas:initiative_organization_sector ?sector.
      ?initiative Ellas:created_in ?country.
      ?country rdfs:label ?countryName.
    }}
    """
