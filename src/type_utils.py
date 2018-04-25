'''
    spaCy
    https://spacy.io/

    Models for each target language needs to be downloaded using the
    following command:

    python -m spacy download en

    Default named entity types

    PERSON	    People, including fictional.
    NORP	    Nationalities or religious or political groups.
    FACILITY	Buildings, airports, highways, bridges, etc.
    ORG	        Companies, agencies, institutions, etc.
    GPE	        Countries, cities, states.
    LOC	        Non-GPE locations, mountain ranges, bodies of water.
    PRODUCT	    Objects, vehicles, foods, etc. (Not services.)
    EVENT	    Named hurricanes, battles, wars, sports events, etc.
    WORK_OF_ART	Titles of books, songs, etc.
    LANGUAGE	Any named language.

    DATE	    Absolute or relative dates or periods.
    TIME	    Times smaller than a day.
    PERCENT	    Percentage, including "%".
    MONEY	    Monetary values, including unit.
    QUANTITY	Measurements, as of weight or distance.
    ORDINAL	    "first", "second", etc.
    CARDINAL	Numerals that do not fall under another type.

    '''
from models import  get_sentimantic_session, TypeNamedEntityAssoc


def get_namedentity(type_URI, kb_sparql_endpoint="https://dbpedia.org/sparql", defaultGraph="http://dbpedia.org"):
    result = get_named_entity_type_base(type_URI)
    class_type = type_URI
    while (result == None and class_type != None):
        class_type = get_superclass_type(class_type, kb_sparql_endpoint)
        result = get_named_entity_type_base(class_type)
    return result


def get_named_entity_type_base(type_URI):
    SentimanticSession = get_sentimantic_session()
    sentimantic_session = SentimanticSession()
    type_ne = sentimantic_session.query(TypeNamedEntityAssoc).filter(TypeNamedEntityAssoc.type == type_URI).first()
    if type_ne != None:
        return type_ne.namedentity


def get_superclass_type(type_URI, kb_sparql_endpoint="https://dbpedia.org/sparql", defaultGraph="http://dbpedia.org"):
    from SPARQLWrapper import SPARQLWrapper, JSON
    sparql = SPARQLWrapper(kb_sparql_endpoint, defaultGraph=defaultGraph)
    query = """
    select ?superClass
    where{
    <"""+ type_URI + """> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?superClass.}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    super_type = None
    for result in results["results"]["bindings"]:
        super_type = result["superClass"]["value"].encode('utf-8').strip()
    return super_type
