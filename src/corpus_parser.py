from os import listdir, mkdir
from os.path import isfile, join

from sqlalchemy.exc import IntegrityError

from snorkel import SnorkelSession
from snorkel.parser import XMLMultiDocPreprocessor
from snorkel.parser.spacy_parser import Spacy
from snorkel.parser import CorpusParser
from snorkel.models import Document, Sentence
import logging
import shutil

def parse_wikipedia_dump(
    dumps_folder_path='../../data/wikipedia/dump/en/extracted_text/AA/', clear=False, parallelism=8):

    logging.info("Corpus parsing start")
    session = SnorkelSession()



    corpus_parser = CorpusParser(parser=Spacy())
    onlyfiles = [f for f in listdir(dumps_folder_path) if isfile(join(dumps_folder_path, f))]

    i=0
    for file in onlyfiles:
        if  file.endswith(".xml"):
            print file
            doc_preprocessor = XMLMultiDocPreprocessor(
                path=dumps_folder_path+file,
                doc='.//doc',
                text='./text()',
                id='./@title'
            )
            if i > 0:
                clear = False
            try:
                corpus_parser.apply(doc_preprocessor, clear=clear, parallelism=parallelism)
            except IntegrityError as e:
                print("Already parsed "+file)
                logging.error("Already parsed "+file)
            i=i+1
    #logging.debug("Documents: %d", session.query(Document).count())
    #logging.debug("Sentences: %d", session.query(Sentence).count())
    logging.info("Corpus parsing end")

