import axios from "axios";

// Configure estas três variáveis no seu ambiente (.env / variáveis de build).
// Nunca commite valores reais — veja .env.example.
const BASE_URL = process.env.ELLAS_GRAPH_URL || "";
const GRAPH_USER = process.env.ELLAS_GRAPH_USER || "";
const GRAPH_PASS = process.env.ELLAS_GRAPH_PASS || "";

if (!BASE_URL || !GRAPH_USER || !GRAPH_PASS) {
  throw new Error(
    "ELLAS_GRAPH_URL, ELLAS_GRAPH_USER e ELLAS_GRAPH_PASS precisam estar definidas no ambiente (veja .env.example)."
  );
}

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/sparql-query",
    Accept: "application/sparql-results+json",
    Authorization: "Basic " + btoa(`${GRAPH_USER}:${GRAPH_PASS}`),
  },
  withCredentials: true, // Incluir credenciais
});

const fetchQuery = async (query: string) => {
  try {
    const response = await axiosInstance.post("", query);
    return response.data;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
};

// Consultas relacionadas às Políticas (Activity 2)

// Em quais países a política foi aplicada?
export const fetchPoliciesAppliedInCountries = async () => {
  const query = `
  PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?policyName ?countryName where {
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.}
`;
  return await fetchQuery(query);
};

// Quais tipos de políticas/processos/práticas de gênero existem na América Latina?
export const fetchPolicyTypesInLatinAmerica = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      select  ?policyName ?countryName ?policyType where {
      ?policy a Ellas:Policy.
      ?policy rdfs:label ?policyName.
      ?policy Ellas:policy_type ?policyType.
      ?policy Ellas:created_in ?country.
      ?country rdfs:label ?countryName.}
  `;
  return fetchQuery(query || defaultQuery);
};

// Como as políticas identificadas/analisadas estão promovendo a participação das mulheres em STEM?
export const fetchPoliciesPromotingWomenInSTEM = (query?: string) => {
  const defaultQuery = `
  PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?policyName ?countryName ?policyResults where {
    ?policy a Ellas:Policy.
    ?policy rdfs:label ?policyName.
    ?policy Ellas:policy_description ?policyResults.
    ?policy Ellas:created_in ?country.
    ?country rdfs:label ?countryName.}
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais tipos de políticas/processos/práticas de gênero foram implementadas na Bolívia, Brasil e Peru desde 2015?
export const fetchPoliciesImplementedInCountriesSince2015 = (
  query?: string
) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
select ?policyName ?countryName ?start_date  where {
?policy a Ellas:Policy.
?policy rdfs:label ?policyName.
?policy Ellas:created_in ?country.
?country rdfs:label ?countryName.
?policy Ellas:start_date ?start_date
filter(xsd:integer(?start_date) > 2015)
filter(regex(str(?countryName),"Peru") || regex(str(?countryName),"peru") ||
regex(str(?countryName),"Brazil") || regex(str(?countryName),"brazil") ||
regex(str(?countryName),"Bolivia") ||regex(str(?countryName),"bolivia"))}
  `;
  return fetchQuery(query || defaultQuery);
};

// Consultas relacionadas às Iniciativas (Activity 3)

// Quais e quantas iniciativas são realizadas no Brasil?
export const fetchInitiativesByCountry = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
select ?policyName ?countryName ?start_date  where {
?policy a Ellas:Policy.
?policy rdfs:label ?policyName.
?policy Ellas:created_in ?country.
?country rdfs:label ?countryName.
?policy Ellas:start_date ?start_date
filter(xsd:integer(?start_date) > 2015)
filter(regex(str(?countryName),"Peru") || regex(str(?countryName),"peru") ||
regex(str(?countryName),"Brazil") || regex(str(?countryName),"brazil") ||
regex(str(?countryName),"Bolivia") ||regex(str(?countryName),"bolivia"))}
  `;
  return fetchQuery(defaultQuery);
};

// Quais fontes de dados são usadas para a iniciativa?
export const fetchDataSourcesForInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?datasource where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_data_source ?datasource.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
 }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais são as redes sociais da iniciativa?
export const fetchSocialNetworksForInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?link where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_socialmedia_link ?link.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName. }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quantas iniciativas são de programa?
export const fetchProgramInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName where {
?initiative a Ellas:Program.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.}
  `;
  return fetchQuery(query || defaultQuery);
};

// As iniciativas são públicas ou privadas?
export const fetchPublicPrivateInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?sector where {
?initiative a Ellas:Program.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_organization_sector ?sector.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName. }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quantas iniciativas são coordenadas por indivíduos?
export const fetchIndividualCoordinatedInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?coordinatorType where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_coordinator_type ?coordinatorType.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter(?coordinatorType = "Personal"@en) }
  `;
  return fetchQuery(query || defaultQuery);
};

// Qual é o gênero social das pessoas que são responsáveis pelas iniciativas?
export const fetchCoordinatorGenderForInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?coordinatorGender where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_coordinator_gender ?coordinatorGender.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
 }
  `;
  return fetchQuery(query || defaultQuery);
};

// Qual é o objetivo da iniciativa?
export const fetchInitiativeObjectives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?objective where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_objective ?objective.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName. }
  `;
  return fetchQuery(query || defaultQuery);
};

// Qual modalidade de iniciativa é usada para as ações/atividades?
export const fetchInitiativeFormats = (query?: string) => {
  const defaultQuery = `
   PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?format where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_format ?format.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
 }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais iniciativas atendem meninas ou adolescentes?
export const fetchInitiativesForGirlsOrAdolescents = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?targetAudienceAge where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:focused_on ?targetAudience.
?targetAudience a Ellas:Target_Audience_Age.
?targetAudience rdfs:label ?targetAudienceAge.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
FILTER (regex(str(?targetAudienceAge), "teenagers")||regex(str(?targetAudienceAge), "Teenagers")
|| regex(str(?targetAudienceAge), "children") || regex(str(?targetAudienceAge), "Children")) }
  `;
  return fetchQuery(query || defaultQuery);
};

// Qual é o gênero social do público-alvo atendido pela iniciativa?
export const fetchTargetAudienceGenderForInitiatives = (query?: string) => {
  const defaultQuery = `
   PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?targetAudienceGender where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:focused_on ?targetAudience.
?targetAudience a Ellas:Target_Audience_Gender.
?targetAudience rdfs:label ?targetAudienceGender.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.}
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais iniciativas atendem mulheres negras?
export const fetchInitiativesForBlackWomen = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?targetAudienceRace ?targetAudienceGender where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:focused_on ?targetAudience.
?targetAudience a Ellas:Target_Audience_Race.
?targetAudience rdfs:label ?targetAudienceRace.
?initiative Ellas:focused_on ?targetAudienceG.
?targetAudienceG a Ellas:Target_Audience_Gender.
?targetAudienceG rdfs:label ?targetAudienceGender.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter( regex(str(?targetAudienceRace), "Black") || regex(str(?targetAudienceRace), "black")   )
filter( regex(str(?targetAudienceGender), "Feminine")) }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais iniciativas estão sendo desenvolvidas em um determinado nível escolar?
export const fetchInitiativesByEducationalLevel = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?targetAudienceEducationalLevel where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:focused_on ?targetAudience.
?targetAudience a Ellas:Target_Audience_EducationalLevel.
?targetAudience rdfs:label ?targetAudienceEducationalLevel.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter( regex(str(?targetAudienceEducationalLevel), "Undergraduate") || regex(str(?targetAudienceEducationalLevel), "undergraduate"))
}
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais iniciativas atendem a determinados grupos vulneráveis?
export const fetchInitiativesForVulnerableGroups = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?targetAudienceVulnerable where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:focused_on ?targetAudience.
?targetAudience a Ellas:Target_Audience_VulnerableGroups.
?targetAudience rdfs:label ?targetAudienceVulnerable.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter( regex(str(?targetAudienceVulnerable), "disabilities") )
}
  `;
  return fetchQuery(query || defaultQuery);
};

// As iniciativas envolvem a comunidade escolar?
export const fetchSchoolCommunityInvolvementInInitiatives = (
  query?: string
) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?targetAudienceStakeholders where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:focused_on ?targetAudience.
?targetAudience a Ellas:Target_Audience_Stakeholders.
?targetAudience rdfs:label ?targetAudienceStakeholders.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter( regex(str(?targetAudienceStakeholders), "School") )}
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais e quantas iniciativas são realizadas em uma determinada cidade?
export const fetchInitiativesByCity = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?cityName where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:located_in ?city.
?city a Ellas:City.
?city rdfs:label ?cityName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter( ?cityName= "Curitiba"@en ) }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais e quantas iniciativas são realizadas em um determinado estado?
export const fetchInitiativesByState = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?stateName where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:located_in ?state.
?state a Ellas:State.
?state rdfs:label ?stateName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter( ?stateName= "Paraná"@en ) }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais e quantas iniciativas são realizadas em uma determinada área?
export const fetchInitiativesByArea = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?areaName where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:located_in ?area.
?area a Ellas:Area.
?area rdfs:label ?areaName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter( ?areaName= "Urban"@en ) }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais e quantas iniciativas são realizadas em uma determinada região?
export const fetchInitiativesByRegion = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?regionName where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:located_in ?region.
?region a Ellas:Region.
?region rdfs:label ?regionName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter(regex (str(?regionName),"Coast") ) }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais e quantas iniciativas têm determinado alcance?
export const fetchInitiativesByReach = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?regionName where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:located_in ?region.
?region a Ellas:Region.
?region rdfs:label ?regionName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter(regex (str(?regionName),"Coast") ) }
  `;
  return fetchQuery(query || defaultQuery);
};

// As iniciativas são financiadas?
export const fetchFundedInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?organizationName where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:funded_by ?organization.
?organization rdfs:label ?organizationName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
}
  `;
  return fetchQuery(query || defaultQuery);
};

// Qual é o setor da(s) organização(ões) que financia(m) a iniciativa?
export const fetchInitiativeFundingSectors = (query?: string) => {
  const defaultQuery = `
   PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?sector where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:funded_by ?organization.
?organization Ellas:organization_sector ?sector.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
 }
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais iniciativas estão ativas?
export const fetchActiveInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryname ?status where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_status ?status.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
filter(?status="Active"@en) }
  `;
  return fetchQuery(query || defaultQuery);
};

// As iniciativas já foram implementadas ou ainda estão em fase de design?
export const fetchInitiativesByPhase = (query?: string) => {
  const defaultQuery = `
   PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?startDate where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:start_date ?startDate.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.}
  `;
  return fetchQuery(query || defaultQuery);
};

// Quais iniciativas já foram concluídas?
export const fetchFinishedInitiatives = (query?: string) => {
  const defaultQuery = `
   PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?finishDate where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:finish_date ?finishDate.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName. }
  `;
  return fetchQuery(query || defaultQuery);
};

// Qual é o site (URL) da iniciativa?
export const fetchInitiativeWebsites = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?website where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_website ?website.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
}
  `;
  return fetchQuery(query || defaultQuery);
};

// Quantas iniciativas fazem parte de comunidades?
export const fetchCommunityInitiatives = (query?: string) => {
  const defaultQuery = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?initiativeName ?countryName ?communityName where {
?initiative a Ellas:Initiative.
?initiative rdfs:label ?initiativeName.
?initiative Ellas:initiative_community_name ?communityName.
?initiative Ellas:created_in ?country.
?country rdfs:label ?countryName.
}
  `;
  return fetchQuery(query || defaultQuery);
};

// Fetch functions for Contextual Factors (Activity 4)

// Positive contextual factors in countries analyzed
export const fetchPositiveContextualFactors = async () => {
  const query = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?contextualFactorName  ?countryName ?impactType where {
?factor a Ellas:Factor.
?contextualFactor rdfs:subClassOf ?factor.
?contextualFactor rdfs:label ?contextualFactorName.
?contextualFactor Ellas:factors_impact_type ?impactType.
?contextualFactor Ellas:analyzed_in ?country.
?country rdfs:label ?countryName.
filter(?impactType ="Positive"@en)}
  `;
  return await fetchQuery(query);
};

// Negative contextual factors in institution activities
export const fetchNegativeContextualFactorsInInstitution = async () => {
  const query = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?contextualFactorName ?impactType ?countryName ?contextType where {
?factor a Ellas:Factor.
?contextualFactor rdfs:subClassOf ?factor.
?contextualFactor rdfs:label ?contextualFactorName.
?contextualFactor Ellas:factors_impact_type ?impactType.
?contextualFactor Ellas:analyzed_in ?country.
?country rdfs:label ?countryName.
?contextualFactor Ellas:factors_context_type ?contextType.
filter(?impactType ="Negative"@en)
filter(regex (str(?contextType),"University")) }
  `;
  return await fetchQuery(query);
};

// Contextual factors related to educational factors
export const fetchContextualFactorsByEducationType = async () => {
  const query = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?contextualFactorName ?countryName ?factorName where {
?factor a Ellas:Factor.
?contextualFactor rdfs:subClassOf ?factor.
?contextualFactor rdfs:label ?contextualFactorName.
?factor rdfs:label ?factorName.
?contextualFactor Ellas:analyzed_in ?country.
?country rdfs:label ?countryName.
filter(regex(str(?factorName),"educational")||regex(str(?factorName),"Educational"))}
  `;
  return await fetchQuery(query);
};

// Contextual factors impacting females positively/negatively
export const fetchContextualFactorsImpactingFemales = async () => {
  const query = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select ?contextualFactorName ?countryName ?impactType ?targetAudienceGender where {
?factor a Ellas:Factor.
?contextualFactor rdfs:subClassOf ?factor.
?contextualFactor rdfs:label ?contextualFactorName.
?contextualFactor Ellas:factors_impact_type ?impactType.
?contextualFactor Ellas:focused_on ?targetAudience.
?targetAudience a Ellas:Target_Audience_Gender.
?targetAudience rdfs:label ?targetAudienceGender.
?contextualFactor Ellas:analyzed_in ?country.
?country rdfs:label ?countryName.
filter(?impactType ="Positive"@en)
filter(?targetAudienceGender="Female"@en) }
  `;
  return await fetchQuery(query);
};

// Impacts of a specific contextual factor
export const fetchImpactsOfContextualFactor = async () => {
  const query = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select ?contextualFactorName ?countryName ?impact where {
?factor a Ellas:Factor.
?contextualFactor rdfs:subClassOf ?factor.
?contextualFactor rdfs:label ?contextualFactorName.
?contextualFactor Ellas:analyzed_in ?country.
?country rdfs:label ?countryName.
?contextualFactor Ellas:factors_impact ?impact.}
  `;
  return await fetchQuery(query);
};

// Impact types of contextual factor in Latin American institutions
export const fetchImpactTypesOfContextualFactors = async () => {
  const query = `
   PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?contextualFactorName ?impactType ?countryName ?contextType where {
?factor a Ellas:Factor.
?contextualFactor rdfs:subClassOf ?factor.
?contextualFactor rdfs:label ?contextualFactorName.
?contextualFactor Ellas:factors_impact_type ?impactType.
?contextualFactor Ellas:analyzed_in ?country.
?country rdfs:label ?countryName.
?contextualFactor Ellas:factors_context_type ?contextType.
filter(?contextualFactorName="Gender stereotypes"@en)
filter(?impactType ="Negative"@en)
filter(regex (str(?contextType),"University"))}
  `;
  return await fetchQuery(query);
};

// Contextual factors impacting specific impacts (e.g., leadership) in a country
export const fetchContextualFactorsImpactingSpecificImpacts = async () => {
  const query = `
    PREFIX Ellas: <https://ellas.ufmt.br/Ontology/Ellas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?contextualFactorName ?impactType ?impact ?countryName  where {
?factor a Ellas:Factor.
?contextualFactor rdfs:subClassOf ?factor.
?contextualFactor rdfs:label ?contextualFactorName.
?contextualFactor Ellas:factors_impact_type ?impactType.
?contextualFactor Ellas:factors_impact ?impact.
?contextualFactor Ellas:analyzed_in ?country.
?country rdfs:label ?countryName.
filter(?impactType ="Positive"@en)
filter(regex(str(?impact),"Leadership")||regex(str(?impact),"leadership")) }
  `;
  return await fetchQuery(query);
};

// Atualize o mapeamento de perguntas para funções de busca
export const questionFunctions: { [key: string]: any } = {
  "Which/How many initiatives are carried out by countries?":
    fetchInitiativesByCountry,
  "What data source are used for initiative?": fetchDataSourcesForInitiatives,
  "What is the initiative's social network(s)?":
    fetchSocialNetworksForInitiatives,
  "How many initiatives are of program?": fetchProgramInitiatives,
  "Are these initiatives public or private?": fetchPublicPrivateInitiatives,
  "How many initiatives are coordinated by individuals?":
    fetchIndividualCoordinatedInitiatives,
  "What is the social gender of the people who are responsible for the initiatives?":
    fetchCoordinatorGenderForInitiatives,
  "What is the OBJECTIVE of the initiative?": fetchInitiativeObjectives,
  "Which initiative modality are used for the actives/actions?":
    fetchInitiativeFormats,
  "What initiatives serve girls or adolescents?":
    fetchInitiativesForGirlsOrAdolescents,
  "What is the social gender of the target audience served by the initiative?":
    fetchTargetAudienceGenderForInitiatives,
  "What initiatives serve black women?": fetchInitiativesForBlackWomen,
  "What initiatives are being developed <at a given school level>?":
    fetchInitiativesByEducationalLevel,
  "What initiatives serve <a certain vulnerable group>?":
    fetchInitiativesForVulnerableGroups,
  "Do the initiatives involve the School community?":
    fetchSchoolCommunityInvolvementInInitiatives,
  "Which/How many initiatives are carried out <in a given city>?":
    fetchInitiativesByCity,
  "What/How many initiatives are carried out <in a given state>?":
    fetchInitiativesByState,
  "What/How many initiatives are carried out <in a given area>?":
    fetchInitiativesByArea,
  "What/How many initiatives are carried out <in a given region>?":
    fetchInitiativesByRegion,
  "Which/How many initiatives have <a given reach>?": fetchInitiativesByReach,
  "Are the initiatives funded?": fetchFundedInitiatives,
  "What is the sector of the organization(s) that finance(s) the initiative?":
    fetchInitiativeFundingSectors,
  "What initiatives are active?": fetchActiveInitiatives,
  "Have the initiatives already been implemented or are they still in the design phase?":
    fetchInitiativesByPhase,
  "Which initiatives are already finished?": fetchFinishedInitiatives,
  "What is the initiative's website (URL)?": fetchInitiativeWebsites,
  "How many initiatives are part of communities?": fetchCommunityInitiatives,
  "In which countries the policy was applied?": fetchPoliciesAppliedInCountries,
  "What types of gender policies/processes/practices exist in Latin America?":
    fetchPolicyTypesInLatinAmerica,
  "How policies identified/analyzed are promoting women's participation in STEM fields?":
    fetchPoliciesPromotingWomenInSTEM,
  "What types of gender policies/processes/practices have been implemented in Bolivia, Brazil and Peru since 2015?":
    fetchPoliciesImplementedInCountriesSince2015,
  "What are the positive CONTEXTUAL FACTORS in COUNTRIES ANALYZED?":
    fetchPositiveContextualFactors,
  "What are the negative CONTEXTUAL FACTORS in activities in Institution X in COUNTRIES ANALYZED?":
    fetchNegativeContextualFactorsInInstitution,
  "Which CONTEXTUAL FACTORS are related to the TYPE of Educational FACTOR?":
    fetchContextualFactorsByEducationType,
  "What are the CONTEXTUAL FACTORS that impact Positively/Negatively the GENDER Female?":
    fetchContextualFactorsImpactingFemales,
  "What are the IMPACTS of CONTEXTUAL FACTOR X?":
    fetchImpactsOfContextualFactor,
  "Which are the IMPACT TYPES of the CONTEXTUAL FACTOR Y in Latin American INSTITUTIONS?":
    fetchImpactTypesOfContextualFactors,
  "What are the CONTEXTUAL FACTORS that impact Positively/Negatively on IMPACT (IMPACT=Leadership, permanence, motivation, others) in the country X?":
    fetchContextualFactorsImpactingSpecificImpacts,
};
