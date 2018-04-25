import logging
import time
from Queue import Empty
from SPARQLWrapper import SPARQLWrapper, JSON
from multiprocessing import JoinableQueue, Process
from models import get_sentimantic_session

def get_predicate_samples_from_KB(predicate_resume, kb_SPARQL_endpoint="https://dbpedia.org/sparql",
                                  defaultGraph="http://dbpedia.org", language="en",page_size=10000, parallelism=32):


    logging.info('Starting downloading samples for predicate "%s" domain "%s", range "%s"',
                 predicate_resume["predicate_URI"], predicate_resume["subject_type"], predicate_resume["object_type"])
    is_to_download=predicate_resume["configs"]["samples_download"]
    if is_to_download==False:
        logging.info("Samples download config is false, skipping....")
        return
    count=count_samples(predicate_resume, language=language,
                  kb_SPARQL_endpoint=kb_SPARQL_endpoint, defaultGraph=defaultGraph)
    pages=count/page_size+1
    workers = []
    count_workers=int(parallelism)


    in_queue = JoinableQueue()
    for i in range(0,pages):
        in_queue.put(i*page_size)
    for i in range(count_workers):
        worker = SampleDownloadWorker(predicate_resume,in_queue=in_queue, out_queue=None,
                                                   page_size=page_size, language=language,
                                                   kb_SPARQL_endpoint=kb_SPARQL_endpoint,
                                                   defaultGraph=defaultGraph)
        workers.append(worker)

    for worker in workers:
        worker.start()

    for i, worker in enumerate(workers):
        worker.join()

    for worker in workers:
        worker.terminate()

    logging.info('Finished downloading samples for predicate "%s" domain "%s", range "%s"',
                 predicate_resume["predicate_URI"], predicate_resume["subject_type"], predicate_resume["object_type"])

QUEUE_TIMEOUT = 3
class SampleDownloadWorker(Process):
    def __init__(self,predicate_resume,in_queue=None, out_queue=None, page_size=10000, language='en',
                 kb_SPARQL_endpoint="https://dbpedia.org/sparql",
                 defaultGraph="http://dbpedia.org"):
        """
        in_queue: A Queue of input objects to process; primarily for running in parallel
        """
        Process.__init__(self)
        self.daemon       = True
        self.in_queue     = in_queue
        self.out_queue    = out_queue

        # Each UDF starts its own Engine
        # See http://docs.sqlalchemy.org/en/latest/core/pooling.html#using-connection-pools-with-multiprocessing
        SentimanticSession=get_sentimantic_session()
        self.sentimantic_session   = SentimanticSession()
        self.predicate_resume=predicate_resume
        self.page_size=page_size
        self.language=language
        self.kb_SPARQL_endpoint=kb_SPARQL_endpoint
        self.defaultGraph=defaultGraph

    def run(self):
        while True:
            try:
                offset = self.in_queue.get(True, QUEUE_TIMEOUT)
                sample_class=self.predicate_resume["sample_class"]
                query_offset = "OFFSET "
                query_limit = "LIMIT "+str(self.page_size)
                query=get_query(self.predicate_resume, self.language)
                query = query + query_offset + str(offset) + " \n" + query_limit
                print(query)
                sparql = SPARQLWrapper(self.kb_SPARQL_endpoint, defaultGraph=self.defaultGraph)
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                try:
                    results = sparql.query().convert()
                    for result in results["results"]["bindings"]:
                        try:
                            subject = result["subjectLabel"]["value"].encode('utf-8').strip().replace("\"", "")
                            object = result["objectLabel"]["value"].encode('utf-8').strip().replace("\"", "")
                            already_exist=self.sentimantic_session.query(sample_class).filter(sample_class.subject==subject, sample_class.object==object).count()>0
                            if not already_exist:
                                self.sentimantic_session.add(sample_class(subject=subject, object=object))
                                self.sentimantic_session.commit()
                        except Exception as e:
                            print("Error on sample save "+str(offset))
                            print(e)
                            True
                    self.sentimantic_session.close()
                except Exception as http_error:
                    print("Error http "+str(offset))
                    print(http_error)
                    self.in_queue.put(offset)
                    time.sleep(5)
            except Empty as empty:
                print("Error empty ")
                print(empty)
                break
            except Exception as ex:
                print("Error ex ")
                print(ex)



def get_query(predicate_resume, language='en'):
    query_select = """
    SELECT  ?subjectLabel ?objectLabel
    WHERE 
    {
        SELECT DISTINCT ?subjectLabel ?objectLabel
    """
    query=query_select+ get_query_where(predicate_resume, language=language)
    query=query+"""  ORDER BY ASC (?subjectLabel) 
    
    }
    
    """
    return query




def get_query_where(predicate_resume, language='en'):
    domain=predicate_resume["subject_type"]
    range_=predicate_resume["object_type"]
    object_type_filter=""
    object_variable="objectLabel"
    if (predicate_resume["object_ne"]!="DATE"):
        object_type_filter=""" 
            #?o a <""" + range_ + """>. 
            ?o <http://www.w3.org/2000/01/rdf-schema#label> ?objectLabel .
            #FILTER (lang(?objectLabel) = '"""+language+"""'). 
            """
        object_variable="o"


    query_where = """
        WHERE{
            ?s <""" + predicate_resume["predicate_URI"] + """> ?"""+object_variable+""" .
            #?s a <""" + domain + """>.
            """+object_type_filter+"""
            ?s <http://www.w3.org/2000/01/rdf-schema#label> ?subjectLabel .
            #FILTER (lang(?subjectLabel) = '"""+language+"""')
        }\n
        """
    return query_where

def count_samples(predicate_resume,
                  language='en',
                  kb_SPARQL_endpoint="https://dbpedia.org/sparql",
                  defaultGraph="http://dbpedia.org"):
    query=get_count(predicate_resume,language)
    sparql = SPARQLWrapper(kb_SPARQL_endpoint, defaultGraph=defaultGraph)
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    result = results["results"]["bindings"][0]['callret-0']["value"]
    return int(result)

def get_count(predicate_resume, language='en'):
    query_select = """
        SELECT COUNT DISTINCT ?subjectLabel ?objectLabel
        """
    return query_select+ get_query_where(predicate_resume,language=language)