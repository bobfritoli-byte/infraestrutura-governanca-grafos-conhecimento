"""Cartão de schema do grafo ELLAS (ancoragem do LLM).

Descrição precisa e concisa, construída a partir de sondagem direta do endpoint
ao vivo (não da OWL de design, que diverge da produção). É injetada no prompt
de geração de SPARQL para evitar alucinação de propriedades.
"""

SCHEMA_CARD = """\
# GRAFO DE CONHECIMENTO ELLAS — ESQUEMA (validado no endpoint)

PREFIXOS:
PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX EllasD: <https://ellas.ufmt.br/Ontology/Ellas/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

## REGRAS DE OURO (obrigatórias)
1. O NOME de QUALQUER entidade (iniciativa, política, país, cidade, estado,
   organização, público-alvo, fator) está SEMPRE em `rdfs:label`. Nunca invente
   outra propriedade de nome. Sempre traga o rdfs:label das entidades ligadas
   (ex.: o nome do país), nunca o URI.
2. Muitos literais têm tag de idioma @en. Para igualdade use `?x = "Valor"@en`;
   para busca textual/parcial prefira `FILTER(regex(str(?x), "termo", "i"))`.
3. Para "quantos/quantas", você pode usar `SELECT (COUNT(DISTINCT ?x) AS ?total)`.
4. Em listagens amplas, adicione `LIMIT 100`.

## ONTOLOGIA CURADA — namespace Ellas:  (use # / prefixo Ellas:)
CLASSES:
- Ellas:Initiative (247)  — subclasses: Ellas:Project, Ellas:Program,
  Ellas:Community, Ellas:Conference, Ellas:Training
- Ellas:Policy (63)
- Ellas:Factor / Ellas:ContextualFactor  (fatores contextuais)
- Ellas:Organization (organizações, ex.: financiadoras)
- Ellas:Location -> subclasses: Ellas:Country, Ellas:State, Ellas:City,
  Ellas:Area, Ellas:Region
- Ellas:Target_Audience -> subclasses: Ellas:Target_Audience_Age,
  Ellas:Target_Audience_Gender, Ellas:Target_Audience_Race,
  Ellas:Target_Audience_EducationalLevel, Ellas:Target_Audience_VulnerableGroups,
  Ellas:Target_Audience_Stakeholders, Ellas:Target_Audience_JobPosition

PROPRIEDADES DE OBJETO:
- Ellas:created_in   (Initiative/Policy -> Country)
- Ellas:located_in   (Initiative -> City/State/Area/Region)
- Ellas:focused_on   (Initiative/Factor -> Target_Audience_*)
- Ellas:funded_by    (Initiative -> Organization)
- Ellas:analyzed_in  (Factor/ContextualFactor -> Country)

PROPRIEDADES DE DADOS (Initiative):
- Ellas:initiative_status  (valores: "Active"@en, "Inactive"@en)
- Ellas:start_date, Ellas:finish_date, Ellas:start_year, Ellas:end_year
- Ellas:initiative_objective, Ellas:initiative_format, Ellas:initiative_reach
- Ellas:initiative_website, Ellas:initiative_socialmedia_link
- Ellas:initiative_data_source, Ellas:initiative_other_links
- Ellas:initiative_coordinator_type ("Personal"@en, ...), Ellas:initiative_coordinator_gender
- Ellas:initiative_organization_sector, Ellas:initiative_number_of_participants
- Ellas:initiative_community_name

PROPRIEDADES (Policy):
- Ellas:policy_type, Ellas:policy_description, Ellas:policy_goals,
  Ellas:policy_status, Ellas:policy_stem_subarea, Ellas:created_in, Ellas:start_date

PROPRIEDADES (Factor / ContextualFactor):
- O fator específico é uma SUBCLASSE de um Factor:
    ?cf rdfs:subClassOf ?factor . ?cf rdfs:label ?nomeDoFator .
- Ellas:factors_impact_type ("Positive"@en / "Negative"@en)
- Ellas:factors_impact, Ellas:factors_context_type
- Ellas:analyzed_in (-> Country), Ellas:focused_on (-> Target_Audience_*)

PROPRIEDADES (Organization): Ellas:organization_sector

## DADOS SECUNDÁRIOS (estatísticas) — namespace EllasD:  (use / barra, NÃO #)
ATENÇÃO: namespace com BARRA e nomes camelCase. Não misture com a ontologia curada.
- EllasD:Course (108k), EllasD:TechnologicalCourse, EllasD:BachelorCourse
- EllasD:HigherEducationInstitution
Propriedades de Course:
- EllasD:enrolled_female, EllasD:enrolled_male
- EllasD:completed_female, EllasD:completed_male
- EllasD:fresher_female, EllasD:fresher_male
- EllasD:vacancy, EllasD:registered, EllasD:course_ISCED_label
- EllasD:hasDetailedArea, EllasD:is_course_online, EllasD:is_course_in_person
- EllasD:is_free_of_fees, EllasD:locatedInCity, EllasD:locatedInState
- EllasD:offeredBy (-> HigherEducationInstitution)
Propriedades de HigherEducationInstitution:
- EllasD:HEI_acronym, EllasD:hasAdministrativeCategory, EllasD:hasLocation,
  EllasD:offersCourses
"""
