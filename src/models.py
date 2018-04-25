from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import re

from snorkel.annotations import load_gold_labels
from snorkel.contrib.brat import BratAnnotator
from brat_collection_creator import get_collection_name
from snorkel.models import Marginal, Span, Sentence, Document, LabelKey, Label

SentimanticBase = declarative_base(name='SentimanticBase', cls=object)

def get_sentimantic_engine():
    sentimantic_engine=create_engine('postgresql://sentimantic:sentimantic@postgres:5432/sentimantic')
    return sentimantic_engine

class Predicate(SentimanticBase):
    __tablename__ = 'predicate'
    id = Column(Integer, primary_key=True)
    uri = Column(String(2000), nullable=False, unique=True)


class Type(SentimanticBase):
    __tablename__ = 'type'
    uri = Column(String(2000), primary_key=True)


# class PredicateTypesAssoc(SentimanticBase):
#     __tablename__ = 'predicate_type_assoc'
#     id = Column(Integer, primary_key=True)
#     predicate_id= Column(Integer, ForeignKey('predicate.id', ondelete='CASCADE'), nullable=False)
#     subject_type = Column(Integer, ForeignKey('type.id', ondelete='CASCADE'), nullable=False)
#     object_type = Column(Integer, ForeignKey('type.id', ondelete='CASCADE'), nullable=False)
#     UniqueConstraint('subject_type', 'object_type')


class NamedEntity(SentimanticBase):
    __tablename__ = 'namedentity'
    name = Column(String,  primary_key=True)


class TypeNamedEntityAssoc(SentimanticBase):
    __tablename__ = 'type_namedentity_assoc'
    type =  Column(String, ForeignKey('type.uri', ondelete='CASCADE'), primary_key=True)
    namedentity = Column(String, ForeignKey('namedentity.name', ondelete='CASCADE'), primary_key=True)

#all candidates list
class BinaryCandidate(SentimanticBase):
    __tablename__ = 'binarycandidate'
    id = Column(Integer, primary_key=True)
    subject_namedentity = Column(String, ForeignKey('namedentity.name', ondelete='CASCADE'))
    object_namedentity = Column(String, ForeignKey('namedentity.name', ondelete='CASCADE'))
    UniqueConstraint('subject_namedentity', 'object_namedentity')


#binary candidate for each predicate
class PredicateCandidateAssoc(SentimanticBase):
    __tablename__ = 'predicate_candidate_assoc'
    id = Column(Integer, primary_key=True)
    predicate_id= Column(Integer, ForeignKey('predicate.id', ondelete='CASCADE'), nullable=False)
    candidate_id= Column(Integer, ForeignKey('binarycandidate.id', ondelete='CASCADE'), nullable=False)
    UniqueConstraint('predicate_id', 'candidate_id')

class Sample(SentimanticBase):
    __tablename__ = 'sample'
    id          = Column(Integer, primary_key=True)
    type        = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'sample',
        'polymorphic_on': type
    }




def get_sentimantic_session():
    return sessionmaker(bind=get_sentimantic_engine())

def create_database():
    engine=get_sentimantic_engine()
    try:
        SentimanticBase.metadata.create_all(engine)
        statement = text("""
            INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Person');
            INSERT INTO type (uri) VALUES ('http://www.w3.org/2001/XMLSchema#date');
            INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Place');
            INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Organisation');
            INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Event');
            INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Work');
            INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Language');
            INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Award');
            INSERT INTO namedentity (name) VALUES ('PERSON');
            INSERT INTO namedentity (name) VALUES ('DATE');
            INSERT INTO namedentity (name) VALUES ('GPE');
            INSERT INTO namedentity (name) VALUES ('ORG');
            INSERT INTO namedentity (name) VALUES ('EVENT');
            INSERT INTO namedentity (name) VALUES ('WORK_OF_ART');
            INSERT INTO namedentity (name) VALUES ('LANGUAGE');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Person', 'PERSON');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://www.w3.org/2001/XMLSchema#date', 'DATE');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Place', 'GPE');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Organisation', 'ORG');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Event', 'EVENT');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Work', 'WORK_OF_ART');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Language', 'LANGUAGE');
            INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Award', 'ORG');
        """)
        engine.execute(statement)

    except Exception:
        print("Skip database creation")


def get_predicate_candidate_samples_table(class_name):

    table_name = camel_to_under(class_name)


    args=[u'subject', u'object']
    class_attribs = {

        # Declares name for storage table
        '__tablename__' : table_name,

        # Connects candidate_subclass records to generic Candidate records
        'id' : Column(
            Integer,
            ForeignKey('sample.id', ondelete='CASCADE'),
            primary_key=True
        ),

        'subject':Column(String(500)),
        'object':Column(String(500)),
        # Polymorphism information for SQLAlchemy
        '__mapper_args__' : {'polymorphic_identity': table_name}

    }
    # Add unique constraints to the arguments
    class_attribs['__table_args__'] = (
        UniqueConstraint("subject","object"),
    )

    C = type(class_name.encode('ascii','ignore'), (Sample,),class_attribs)
    engine=get_sentimantic_engine()
    if not engine.dialect.has_table(engine, table_name):
        C.__table__.create(bind=engine)

    return C



def camel_to_under(name):
    """
    Converts camel-case string to lowercase string separated by underscores.

    Written by epost
    (http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case).

    :param name: String to be converted
    :return: new String with camel-case converted to lowercase, underscored
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_sentences_ids_by_title_not_extracted(predicate_resume, session, documents_titles):
    candidate_subclass=predicate_resume["candidate_subclass"]
    subquery_docs=session.query(Document.id).filter(Document.name.in_(documents_titles))
    subquery_span=session.query(Sentence.id). \
        join(Span, Span.sentence_id==Sentence.id). \
        join(candidate_subclass, candidate_subclass.subject_id==Span.id)
    return session.query(Sentence.id).\
        filter(Sentence.document_id.in_(subquery_docs)).\
        filter(~Sentence.id.in_(subquery_span))


def get_sentences_ids_not_extracted(predicate_resume, session):
    candidate_subclass=predicate_resume["candidate_subclass"]
    #case with already extracted cands
    subquery=session.query(Sentence.id).\
        join(Span, Span.sentence_id==Sentence.id).\
        join(candidate_subclass, candidate_subclass.subject_id==Span.id)
    sents_query_id= session.query(Sentence.id).filter(~Sentence.id.in_(subquery))
    return sents_query_id


def get_train_cids_not_labeled(predicate_resume,session):
    # TODO use simple max
    candidate_subclass=predicate_resume["candidate_subclass"]
    key_group=predicate_resume["label_group"]
    subquery=session.query(candidate_subclass.id). \
        join(Label, Label.candidate_id==candidate_subclass.id). \
        join(LabelKey,LabelKey.id==Label.key_id). \
        filter(LabelKey.group==key_group)

    cids_query= session.query(candidate_subclass.id). \
        filter(~candidate_subclass.id.in_(subquery)). \
        filter(candidate_subclass.split == 0)
    return cids_query

def get_train_cids_with_labels_and_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 0, only_id=True, with_marginals=False, with_label=True)

def get_train_cids_with_marginals_and_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 0, only_id=True, with_marginals=True)


def get_train_cands_with_marginals_and_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 0, only_id=False, with_marginals=True)


def get_train_cids_with_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 0, only_id=True, with_marginals=False)


def get_train_cands_with_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 0, only_id=False, with_marginals=False)


def get_dev_cands_with_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 1, only_id=False, with_marginals=False)


def get_dev_cids_with_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 1, only_id=True, with_marginals=False)


def get_test_cands_with_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 2, only_id=False, with_marginals=False)


def get_test_cids_with_span(predicate_resume,session):
    return get_cands_with_span(predicate_resume, session, 2, only_id=True, with_marginals=False)


def get_cands_with_span(predicate_resume,session, split,only_id=False, with_marginals=False, with_label=False):
    candidate_subclass=predicate_resume["candidate_subclass"]
    subquery=session.query(Span.id)
    if only_id:
        query=session.query(candidate_subclass.id)
    else:
        query=session.query(candidate_subclass)

    if with_label:
        query=query.join(Label,Label.candidate_id==candidate_subclass.id)
    if with_marginals:
        query=query. \
            join(Marginal, Marginal.candidate_id==candidate_subclass.id)
    query=query. \
        filter(candidate_subclass.split == split). \
        filter(candidate_subclass.subject_id.in_(subquery)). \
        filter(candidate_subclass.object_id.in_(subquery)). \
        order_by(candidate_subclass.id)
    return query


def get_gold_dev_matrix(predicate_resume, session):
    candidate_subclass=predicate_resume["candidate_subclass"]
    brat = BratAnnotator(session, candidate_subclass, encoding='utf-8')
    dev_cids_query = get_dev_cids_with_span(predicate_resume,session)
    dev_cands = get_dev_cands_with_span(predicate_resume,session).all()
    brat.import_gold_labels(session,get_collection_name(predicate_resume,1),dev_cands,annotator_name="brat")
    L_gold_dev = load_gold_labels(session, annotator_name="brat",
                                  cids_query=dev_cids_query,
                                  split=1)
    return L_gold_dev


def get_gold_test_matrix(predicate_resume, session):
    candidate_subclass=predicate_resume["candidate_subclass"]
    brat = BratAnnotator(session, candidate_subclass, encoding='utf-8')
    test_cids_query=get_test_cids_with_span(predicate_resume, session)
    test_cands = get_test_cands_with_span(predicate_resume, session).all()
    brat.import_gold_labels(session,get_collection_name(predicate_resume, 2),test_cands,annotator_name="brat")
    L_gold_test = load_gold_labels(session, annotator_name="brat",
                                   cids_query=test_cids_query,
                                   split=2)
    return L_gold_test

def delete_orphan_spans():
    stmt=text("""
delete
from context
where context."type"='span' 
and context.id not in(select span.id from span)
""")
    get_sentimantic_engine().execute(stmt)



def get_cands_to_delete_by_title(predicate_resume, session, documents_titles):
    candidate_subclass=predicate_resume["candidate_subclass"]
    #extract only sentences of documents listed
    subquery=session.query(Document.id).filter(Document.name.in_(documents_titles))
    #remove candidates already extracted for this documents
    candidates_to_delete_query=session.query(candidate_subclass). \
        join(Span,candidate_subclass.subject_id==Span.id). \
        join(Sentence, Span.sentence_id==Sentence.id). \
        filter(Sentence.document_id.in_(subquery))
    return candidates_to_delete_query


def update_candidates_by_page_titles(predicate_resume, documents_titles, split):
    candidate_subclass_name=predicate_resume["candidate_subclass"].__tablename__
    stmt="""
update candidate set split="""+str(split)+"""
where candidate.split != """+str(split)+""" 
and candidate.type='"""+candidate_subclass_name+"""' 
and candidate.id in(
select """+candidate_subclass_name+""".id
from """+candidate_subclass_name+"""
where """+candidate_subclass_name+""".subject_id in (

	select span.id 
	from span 
	join sentence on span.sentence_id=sentence.id
	where sentence.id in (
		select sentence.id 
		from sentence 
		join document on sentence.document_id=document.id
		where document.name in (
"""

    i=0
    for documents_title in documents_titles:
        stmt=stmt+""" '"""+documents_title+"""' """
        i=i+1
        if i<len(documents_titles):
            stmt=stmt+""" ,"""
    stmt=stmt+""" ))))"""

    get_sentimantic_engine().execute(text(stmt))

    # candidates_to_delete=get_cands_to_delete_by_title(predicate_resume,session,documents_titles).all()
    # for candidate_to_delete in candidates_to_delete:
    #     session.delete(candidate_to_delete)
    # session.commit()