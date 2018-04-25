import logging
from SPARQLWrapper import SPARQLWrapper, JSON
from models import get_sentimantic_session, Predicate, BinaryCandidate, PredicateCandidateAssoc, get_predicate_candidate_samples_table
from type_utils import get_namedentity
from models import  Type

def infer_and_save_predicate_candidates_types(predicate_URI, sample_files_base_path="./data/samples/"):
    logging.info('Starting infering predicate "%s" domain, range and candidates types ', predicate_URI)
    SentimanticSession=get_sentimantic_session()
    sentimantic_session=SentimanticSession()
    predicate_URI=predicate_URI.strip()
    #retrieve predicate domain
    domains=get_predicate_domains(predicate_URI)
    #retrieve predicate range
    ranges=get_predicate_ranges(predicate_URI)
    predicate=sentimantic_session.query(Predicate).filter(Predicate.uri==predicate_URI).first()
    if predicate != None:
        for domain in domains:
            subject_ne=domain["ne"]
            for range in ranges:
                object_ne=range["ne"]
                candidate=sentimantic_session.query(BinaryCandidate) \
                    .filter(BinaryCandidate.subject_namedentity == subject_ne,
                            BinaryCandidate.object_namedentity == object_ne
                            ).first()
                if candidate == None :
                    candidate = BinaryCandidate(subject_namedentity=subject_ne,
                                                object_namedentity=object_ne)
                    sentimantic_session.add(candidate)
                    sentimantic_session.commit()
                    candidate=sentimantic_session.query(BinaryCandidate) \
                        .filter(BinaryCandidate.subject_namedentity == subject_ne,
                                BinaryCandidate.object_namedentity == object_ne
                                ).first()


                pca=sentimantic_session.query(PredicateCandidateAssoc) \
                    .filter(PredicateCandidateAssoc.predicate_id == predicate.id,
                            PredicateCandidateAssoc.candidate_id == candidate.id
                            ).first()
                if pca == None:
                    predicate_split = predicate_URI.split('/')
                    predicate_split_len = len(predicate_split)
                    predicate_name = predicate_split[predicate_split_len - 1].strip()
                    pca = PredicateCandidateAssoc(predicate_id=predicate.id,
                                                  candidate_id=candidate.id)
                    sentimantic_session.add(pca)
                    sentimantic_session.commit()
    logging.info('Finished infering predicate "%s" domain, range and candidates types ', predicate_URI)



def get_predicate_ranges(predicate_URI, kb_SPARQL_endpoint="https://dbpedia.org/sparql", defaultGraph="http://dbpedia.org"):
    sparql = SPARQLWrapper(kb_SPARQL_endpoint, defaultGraph=defaultGraph)
    rangeQuery = """
        SELECT DISTINCT ?range
        WHERE {
            <""" + predicate_URI + """> <http://www.w3.org/2000/01/rdf-schema#range> ?range.
        }"""
    sparql.setQuery(rangeQuery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    ranges = []
    for result in results["results"]["bindings"]:
        type_URI = result["range"]["value"].encode('utf-8').strip()
        ne = get_namedentity(type_URI, kb_SPARQL_endpoint, defaultGraph=defaultGraph)
        if ne != None:
            range = {'URI': type_URI, 'ne': ne}
            ranges.append(range)

    # retrieve types from results
    if (len(ranges) == 0):
        rangeQueryTotal="""
        SELECT ?type COUNT  (?type) AS ?typeCount
        WHERE{
        {   SELECT ?type
            WHERE{
            ?s <"""+predicate_URI+"""> ?o.
            ?o a ?type.
            }
            LIMIT 100000
        }
           FILTER(  regex(?type, "http://www.w3.org/2002/07/owl#Thing", "i")  )
        }
        GROUP BY (?type)
        ORDER BY DESC(?typeCount)"""
        sparql.setQuery(rangeQueryTotal)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        totalCount=0
        for result in results["results"]["bindings"]:
            totalCount = int(result["typeCount"]["value"].encode('utf-8').strip())
            break

        if totalCount>0:
            rangeQuery = """
            SELECT ?type COUNT  (?type) AS ?typeCount
            WHERE{
            {   SELECT ?type
                WHERE{
                ?s <"""+predicate_URI+"""> ?o.
                ?o a ?type.
                }
                LIMIT 100000
            }
                """+get_types_filter_regex()+"""
            }
            GROUP BY (?type)
            ORDER BY DESC(?typeCount)"""
            sparql.setQuery(rangeQuery)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                type_URI = result["type"]["value"].encode('utf-8').strip()
                typeCount = int(result["typeCount"]["value"].encode('utf-8').strip())
                if typeCount > (totalCount / 100)*3:
                    ne = get_namedentity(type_URI, kb_SPARQL_endpoint, defaultGraph=defaultGraph)
                    if ne != None:
                        range = {'URI': type_URI, 'ne': ne}
                        ranges.append(range)
    return ranges


def get_predicate_domains(predicate_URI, kb_SPARQL_endpoint="https://dbpedia.org/sparql",
                          defaultGraph="http://dbpedia.org"):
    sparql = SPARQLWrapper(kb_SPARQL_endpoint, defaultGraph=defaultGraph)
    domainQuery = """
        SELECT DISTINCT ?domain
        WHERE {
            <""" + predicate_URI + """> <http://www.w3.org/2000/01/rdf-schema#domain> ?domain.
        }"""
    sparql.setQuery(domainQuery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    domains = []
    for result in results["results"]["bindings"]:
        type_URI = result["domain"]["value"].encode('utf-8').strip()
        ne = get_namedentity(type_URI, kb_SPARQL_endpoint, defaultGraph=defaultGraph)
        if ne != None:
            domain = {'URI': type_URI, 'ne': ne}
            domains.append(domain)

    # retrieve types from results
    if (len(domains) == 0):
        domainQueryTotal="""
        SELECT ?type COUNT  (?type) AS ?typeCount
        WHERE{
        {   SELECT ?type
            WHERE{
            ?s <"""+predicate_URI+"""> ?o.
            ?s a ?type.
            }
            LIMIT 100000
        }
           FILTER(  regex(?type, "http://www.w3.org/2002/07/owl#Thing", "i")  )
        }
        GROUP BY (?type)
        ORDER BY DESC(?typeCount)"""
        sparql.setQuery(domainQueryTotal)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        totalCount=0
        for result in results["results"]["bindings"]:
            totalCount = int(result["typeCount"]["value"].encode('utf-8').strip())
            break

        if totalCount>0:
            domainQuery = """
            SELECT ?type COUNT  (?type) AS ?typeCount
            WHERE{
            {   SELECT ?type
                WHERE{
                ?s <"""+predicate_URI+"""> ?o.
                ?s a ?type.
                }
                LIMIT 100000
            }
                """+get_types_filter_regex()+"""
            }
            GROUP BY (?type)
            ORDER BY DESC(?typeCount)"""
            sparql.setQuery(domainQuery)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                type_URI = result["type"]["value"].encode('utf-8').strip()
                typeCount = int(result["typeCount"]["value"].encode('utf-8').strip())
                if typeCount > (totalCount / 100)*3:
                    ne = get_namedentity(type_URI, kb_SPARQL_endpoint, defaultGraph=defaultGraph)
                    if ne != None:
                        domain = {'URI': type_URI, 'ne': ne}
                        domains.append(domain)
    return domains

def get_types_filter_regex():
    SentimanticSession=get_sentimantic_session()
    sentimantic_session=SentimanticSession()
    types=sentimantic_session.query(Type).all()
    i=0
    filter="FILTER( "
    for type in types:
        if i!=0:
            filter=filter+" || "
        filter=filter+""" regex(?type, \""""+type.uri+"""\", "i") """
        i=i+1
    filter=filter+" ) "

    return filter