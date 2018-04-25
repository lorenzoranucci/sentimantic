import logging
from time import gmtime, strftime
from snorkel import SnorkelSession
from snorkel.annotations import  LabelAnnotator
from snorkel.learning import GenerativeModel
from labelling import get_labelling_functions
from snorkel.annotations import save_marginals
import shutil
from models import *



def train_gen_model(predicate_resume, parallelism=8):
    logging.info("Start train gen")
    session = SnorkelSession()

    labeler=_get_labeler(predicate_resume)
    logging.info("Load matrix")
    L_train=_load_matrix(predicate_resume, session, labeler)
    gen_model = GenerativeModel()
    logging.info("Train model")
    gen_model.train(L_train, epochs=100,
                    decay=0.95, step_size=0.1 / L_train.shape[0],
                    reg_param=1e-6, threads=int(parallelism))
    logging.info("Save model")
    _save_model(predicate_resume,gen_model)
    #Save marginals
    logging.info("Get marginals")
    train_marginals = gen_model.marginals(L_train)
    logging.info("Save marginals")
    save_marginals(session, L_train, train_marginals)



def _get_labeler(predicate_resume):
    LFs = get_labelling_functions(predicate_resume)
    labeler = LabelAnnotator(lfs=LFs)
    return labeler


def _load_matrix(predicate_resume, session, labeler):
    cids_query = get_train_cids_with_span(predicate_resume, session)
    key_group = predicate_resume["label_group"]
    L_train = labeler.load_matrix(session,  cids_query=cids_query, key_group=key_group)
    return L_train

def _save_model(predicate_resume, gen_model):
    date_time=strftime("%d-%m-%Y_%H_%M_%S", gmtime())
    gen_model.save("G"+predicate_resume["predicate_name"]+date_time)
    try:
        shutil.rmtree("./checkpoints/"+"D"+predicate_resume["predicate_name"]+"Latest")
    except:
        print("Latest model not found, not removed")
    gen_model.save("G"+predicate_resume["predicate_name"]+"Latest")