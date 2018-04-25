import logging
from os import mkdir
import shutil
from wikipedia_client import download_articles
from corpus_parser import parse_wikipedia_dump
from candidate_extraction import extract_binary_candidates
from brat_collection_creator import create_collection

def setup_dev(predicate_resume,dump_folder_path="./data/dev/", lang="en", parallelism=1):
    logging.info("Starting dev setup")
    if predicate_resume["configs"]["dev_pages"] is not None:
        return setup(predicate_resume ,dump_folder_path,lang,1,parallelism=parallelism)

def setup_test(predicate_resume, dump_folder_path="./data/test/", lang="en", parallelism=1):
    logging.info("Starting test setup")
    if predicate_resume["configs"]["test_pages"] is not None:
        return setup(predicate_resume ,dump_folder_path,lang,2,parallelism=parallelism)

def setup(predicate_resume,  dump_folder_path, lang, split, parallelism=1):
    if split==1:
        pages_titles=predicate_resume["configs"]["dev_pages"]
    else:
        pages_titles=predicate_resume["configs"]["test_pages"]

    try:
        shutil.rmtree(dump_folder_path)
    except:
        print("Dir not deleted at start")
    try:
        mkdir(dump_folder_path)
    except:
        print("Dir not created")

    logging.info("Downloading articles")
    extracted_pages_titles=download_articles(pages_titles,dump_folder_path,lang=lang)
    logging.info("Parsing")
    parse_wikipedia_dump(dump_folder_path,parallelism=parallelism)
    logging.info("Extracting")
    extract_binary_candidates(predicate_resume, parallelism=parallelism,split=split,documents_titles=extracted_pages_titles)
    collection_name=create_collection(predicate_resume,split)

    logging.info("Deleting dump files")
    try:
        shutil.rmtree(dump_folder_path)
    except:
        print("Dir not deleted at the end")

    logging.info("Finish")
    return collection_name



