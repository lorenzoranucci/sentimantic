import os
os.environ['SNORKELDB'] = 'postgresql://sentimantic:sentimantic@postgres:5432/sentimantic'
from snorkel import SnorkelSession
from snorkel.contrib.brat import BratAnnotator
from time import gmtime, strftime
import logging



def create_collection(predicate_resume, split):
    session = SnorkelSession()
    CandidateSubclass=predicate_resume["candidate_subclass"]
    if split == None or (split!=1 and split!=2):
        print("No split selected")
        logging.error("No split selected")
    cids_query=session.query(CandidateSubclass.id).filter(CandidateSubclass.split==split)
    brat = BratAnnotator(session, CandidateSubclass, encoding='utf-8')
    collection_name=get_collection_name(predicate_resume,split)
    brat.init_collection(collection_name, cid_query=cids_query)
    return collection_name


def get_collection_name(predicate_resume,split):
    if split==1:
        name="/dev"
    elif split==2:
        name="/test"
    else:
        print("No split selected")
        logging.error("No split selected")
    CandidateSubclass=predicate_resume["candidate_subclass"]
    predicate_name = predicate_resume["predicate_name"]
    date_time=strftime("%d-%m-%Y_%H_%M_%S", gmtime())
    return predicate_name+CandidateSubclass.__name__+name#+date_time