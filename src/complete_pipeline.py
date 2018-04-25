from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
os.environ['SNORKELDB'] = 'postgresql://sentimantic:sentimantic@postgres:5432/sentimantic'
import logging
from models import create_database
from predicate_utils import save_predicate, get_predicate_resume, get_predicates_configs
from corpus_parser import parse_wikipedia_dump
from infer_predicate_types import infer_and_save_predicate_candidates_types
from download_predicate_candidates_samples import get_predicate_samples_from_KB
from candidate_extraction import extract_binary_candidates
from labelling import predicate_candidate_labelling
from train_gen_model import train_gen_model
from train_disc_model import train_disc_model
from test_model import test_model
from setup_dev_test import setup_dev, setup_test
from triples_extractor import extract_triples

logging.basicConfig(filename='sentimantic.log',level=logging.INFO, format='%(asctime)s %(message)s')
dump_file_dir="../data/wikipedia/dump/en/extracted_text/AA/"
dump_file_name="wiki_00.xml"
parallelism=32
limit=None
page_size=100000
is_to_parse_wikipedia_dump=False
is_to_infer_candidate_types=False
is_to_download_samples_from_kb=False
is_to_extract_candidates=False
is_to_label=False
is_to_train_gen_classifier=False
is_to_train_disc_classifier=False
is_to_test_classifier=False
is_to_setup=False
is_to_extract_triples=False
i=0
for arg in sys.argv:
    if arg.strip()=='parse':
        is_to_parse_wikipedia_dump=True
    elif arg.strip()=='infer':
        is_to_infer_candidate_types=True
    elif arg.strip()=='download':
        is_to_download_samples_from_kb=True
    elif arg.strip()=='extract':
        is_to_extract_candidates=True
    elif arg.strip()=='setup':
        is_to_setup=True
    elif arg.strip()=='label':
        is_to_label=True
    elif arg.strip()=='train_gen':
        is_to_train_gen_classifier=True
    elif arg.strip()=='train_disc':
        is_to_train_disc_classifier=True
    elif arg.strip()=='test':
        is_to_test_classifier=True
    elif arg.strip()=='triples':
        is_to_extract_triples=True
    elif arg.strip()=='parallelism':
        parallelism=sys.argv[i+1]
    elif arg.strip()=='limit':
        limit=int(sys.argv[i+1])
    elif arg.strip()=='page_size':
        page_size=int(sys.argv[i+1])
    i=i+1



def start_pipeline():
    create_database()
    logging.info("Pipeline start")
    if is_to_parse_wikipedia_dump:
        parse_wikipedia_dump(dump_file_dir, parallelism=parallelism)
    predicate_configs_list=get_predicates_configs()
    for predicate_configs in predicate_configs_list:
        start_predicate_pipeline(predicate_configs)

def start_predicate_pipeline(predicate_configs):
    #persist predicate
    save_predicate(predicate_configs['uri'])
    #retrieve predicate domain and range
    if is_to_infer_candidate_types:
        infer_and_save_predicate_candidates_types(predicate_configs['uri'])
    #get predicate with related objects from database
    predicate_resume_list=get_predicate_resume(predicate_configs)
    for predicate_resume in predicate_resume_list:
        start_predicate_domain_range_pipeline(predicate_resume)

def start_predicate_domain_range_pipeline(predicate_resume):
    #download samples from knowledge base
    if is_to_download_samples_from_kb:
        get_predicate_samples_from_KB(predicate_resume, parallelism=parallelism)
    #candidates extraction
    if is_to_extract_candidates:
        extract_binary_candidates(predicate_resume, parallelism=parallelism, limit=limit, page_size=page_size)
    if is_to_setup:
        setup_dev(predicate_resume)
        setup_test(predicate_resume)
    #candidates labeling with distant supervision
    if is_to_label:
        predicate_candidate_labelling(predicate_resume, parallelism=parallelism)
    #train model
    if is_to_train_gen_classifier:
        train_gen_model(predicate_resume, parallelism=parallelism)
    if is_to_train_disc_classifier:
        train_disc_model(predicate_resume, parallelism=parallelism)
    if is_to_extract_triples:
        extract_triples(predicate_resume)
    if is_to_test_classifier:
        test_model(predicate_resume)





start_pipeline()