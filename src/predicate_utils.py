import logging
from SPARQLWrapper import SPARQLWrapper, JSON


from models import  Type, TypeNamedEntityAssoc
from sqlalchemy.exc import IntegrityError
from models import get_sentimantic_engine,get_sentimantic_session, Predicate, BinaryCandidate, PredicateCandidateAssoc, get_predicate_candidate_samples_table
from snorkel.models import candidate_subclass
from sqlalchemy.sql import text
import yaml


def save_predicate(predicate_URI):
    logging.info('Saving predicate "%s"', predicate_URI)
    SentimanticSession=get_sentimantic_session()
    sentimantic_session=SentimanticSession()
    predicate_URI=predicate_URI.strip()
    try:
        new_predicate=Predicate(uri=predicate_URI)
        sentimantic_session.add(new_predicate)
        sentimantic_session.commit()
    except IntegrityError:
        logging.warn('Predicate "%s" already existing', predicate_URI )
        sentimantic_session.rollback()
    logging.info('Predicate "%s" saved', predicate_URI)


def get_predicate_resume(predicate_configs):
    predicate_URI=predicate_configs['uri']
    result=[]
    SentimanticSession = get_sentimantic_session()
    sentimantic_session = SentimanticSession()
    predicate=sentimantic_session.query(Predicate).filter(Predicate.uri==predicate_URI).first()
    if predicate != None:
        predicate_URI=predicate_URI.strip()
        pca_list=sentimantic_session.query(PredicateCandidateAssoc) \
            .filter(PredicateCandidateAssoc.predicate_id == predicate.id).all()
        for pca in pca_list:
            candidate=sentimantic_session.query(BinaryCandidate) \
                .filter(BinaryCandidate.id==pca.candidate_id).first()
            subject_ne=candidate.subject_namedentity.strip()
            object_ne=candidate.object_namedentity.strip()
            candidate_name=(subject_ne+object_ne).encode("utf-8")
            CandidateSubclass = candidate_subclass(candidate_name,
                                                   ["subject",
                                                    "object"
                                                    ])
            try:
                statement = text("""
        CREATE OR REPLACE VIEW """+ candidate_name.lower() +"""_view AS
            SELECT document.id AS docid,
        document.name AS docname,
        """+ candidate_name.lower() +""".id AS candid,
        candidate.split,
        sentence.id as sent_id,
        sentence.text,
        predicate.uri as predicate_URI,
        label.value AS label_value,
        marginal.probability
       FROM """+ candidate_name.lower() +"""
         JOIN candidate ON candidate.id = """+ candidate_name.lower() +""".id
         JOIN span ON """+ candidate_name.lower() +""".subject_person_id = span.id
         JOIN sentence ON span.sentence_id = sentence.id
         JOIN document ON sentence.document_id = document.id
         LEFT JOIN label ON candidate.id = label.candidate_id
         LEFT JOIN label_key ON label.key_id = label_key.id
         LEFT JOIN predicate_candidate_assoc ON label_key."group" = predicate_candidate_assoc.id
         left join predicate on predicate_candidate_assoc.predicate_id=predicate.id 
         LEFT JOIN marginal ON marginal.candidate_id = candidate.id;
         
         """)
                get_sentimantic_engine().execute(statement)
            except Exception :
                print("Skip view creation")
            subject_type=sentimantic_session.query(TypeNamedEntityAssoc) \
                .filter(TypeNamedEntityAssoc.namedentity == subject_ne).first().type
            object_type=sentimantic_session.query(TypeNamedEntityAssoc) \
                .filter(TypeNamedEntityAssoc.namedentity == object_ne).first().type

            predicate_name = predicate_configs['name']
            words=predicate_configs["words"]
            sample_class=get_predicate_candidate_samples_table("Sample"+predicate_name.title()+subject_ne.title()+object_ne.title())
            result.append({"predicate_name": predicate_name,
                            "predicate_URI": predicate_URI,
                            "candidate_subclass": CandidateSubclass,
                            "subject_ne":subject_ne, "object_ne":object_ne,
                            "subject_type":subject_type, "object_type":object_type,
                            "label_group":pca.id, "sample_class": sample_class,
                            "words":words, "configs":predicate_configs
                           })
    return result




def count_predicate_samples(predicate_URI, kb_SPARQL_endpoint="https://dbpedia.org/sparql",
                            defaultGraph="http://dbpedia.org"):
    sparql = SPARQLWrapper(kb_SPARQL_endpoint, defaultGraph=defaultGraph)
    rangeQuery = """SELECT  COUNT  (?o) AS ?count
        WHERE{
        ?s <""" + predicate_URI + """> ?o.
        }"""
    sparql.setQuery(rangeQuery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    count_triples = 0
    for result in results["results"]["bindings"]:
        count_triples = int(result["count"]["value"].encode('utf-8').strip())
    return count_triples




def get_predicates_configs(path="./config.yaml"):
    stream = open(path, "r")
    return  yaml.load(stream)["predicates"]
