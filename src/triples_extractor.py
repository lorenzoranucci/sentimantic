import logging
from snorkel import SnorkelSession
from snorkel.learning.disc_models.rnn import reRNN
from xml.dom import minidom
import requests
import csv
from time import gmtime, strftime
import time
from labelling import are_nouns_similar
from models import *

def extract_triples(predicate_resume, disc_model_name=None):
    date_time=strftime("%Y-%m-%d_%H_%M_%S", gmtime())
    session = SnorkelSession()
    if disc_model_name is None:
        disc_model_name="D"+predicate_resume["predicate_name"]+"Latest"
    test_cands_query  = get_test_cids_with_span(predicate_resume,session)

    test_cands=test_cands_query.all()
    lstm = reRNN()
    logging.info("Loading marginals ")
    lstm.load(disc_model_name)

    predictions=lstm.predictions(test_cands)
    dump_file_path3="./results/"+"triples_"+predicate_resume["predicate_name"]+date_time+".csv"


    subject_type=predicate_resume["subject_type"]
    object_type=predicate_resume["object_type"]
    subject_type_split = subject_type.split('/')
    object_type_split = object_type.split('/')
    subject_type_end=subject_type_split[len(subject_type_split)-1]
    object_type_end=object_type_split[len(object_type_split)-1]
    with open(dump_file_path3, 'w+b') as f:
        writer = csv.writer(f, delimiter=',',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["text","marginal","prediction"])
        i=0
        for c in test_cands:
            if predictions[i]==1:
                subject_span=getattr(c,"subject").get_span()
                object_span=getattr(c,"object").get_span()
                subject_uri = get_dbpedia_node(subject_span,subject_type_end)
                object_uri = get_dbpedia_node(object_span,object_type_end)
                predicate_uri=predicate_resume["predicate_URI"]
                if subject_uri is not None and object_uri is not None:
                    row=[str(subject_uri),str(predicate_uri),str(object_uri)]
                    writer.writerow(row)
            i=i+1



def get_dbpedia_node(noun,type):
    response_ok=False
    while response_ok==False:
        try:
            response_subject=requests.get("http://lookup:1111/api/search/KeywordSearch",{"MaxHits":4,"QueryClass":type,"QueryString":noun})
            response_ok=response_subject.ok
        except Exception:
            time.sleep(0.3)

        try:
            max_refcount=-1
            xml=response_subject.content
            xml=minidom.parseString(xml)
            result_elements=xml.getElementsByTagName('Result')
            for result_element in result_elements:
                #check refcount
                current_refcount=int(result_element.getElementsByTagName('Refcount')[0].firstChild.nodeValue)
                if max_refcount==-1:
                    max_refcount= current_refcount
                if current_refcount < (max_refcount/10):
                    break
                label =result_element.getElementsByTagName('Label')[0].firstChild.nodeValue
                uri =result_element.getElementsByTagName('URI')[0].firstChild.nodeValue
                if are_nouns_similar(label,noun):
                    return uri
        except:
            print("error")

    return None