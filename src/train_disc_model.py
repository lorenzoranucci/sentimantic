import logging
from time import gmtime, strftime
from snorkel import SnorkelSession
from snorkel.annotations import load_marginals
from snorkel.learning.disc_models.rnn import reRNN
import shutil
from models import *



def train_disc_model(predicate_resume, parallelism=8):
    logging.info("Start training disc ")
    session = SnorkelSession()
    train_cids_query = get_train_cids_with_marginals_and_span(predicate_resume, session)
    logging.info("Loading marginals ")
    train_marginals = load_marginals(session, split=0, cids_query=train_cids_query)

    train_kwargs = {
        'lr':         0.01,
        'dim':        50,
        'n_epochs':   10,
        'dropout':    0.25,
        'print_freq': 1,
        'max_sentence_length': 100
    }

    logging.info("Querying train cands")
    candidate_subclass=predicate_resume["candidate_subclass"]
    train_cands = session.query(candidate_subclass).filter(candidate_subclass.split == 0).order_by(candidate_subclass.id).all()#get_train_cands_with_marginals_and_span(predicate_resume, session).all()
    logging.info("Querying dev cands")
    dev_cands = get_dev_cands_with_span(predicate_resume, session).all()
    logging.info("Querying gold labels")
    L_gold_dev = get_gold_dev_matrix(predicate_resume, session)
    logging.info("Training")
    lstm = reRNN(seed=1701, n_threads=int(parallelism))
    lstm.train(train_cands, train_marginals, **train_kwargs)
    logging.info("Saving")
    _save_model(predicate_resume, lstm)
    #test model
    candidate_subclass=predicate_resume["candidate_subclass"]
    test_cands  = session.query(candidate_subclass).filter(candidate_subclass.split == 2).order_by(candidate_subclass.id).all()
    L_gold_test = get_gold_test_matrix(predicate_resume,session)
    p, r, f1 = lstm.score(test_cands, L_gold_test)
    print("Prec: {0:.3f}, Recall: {1:.3f}, F1 Score: {2:.3f}".format(p, r, f1))
    logging.info("Prec: {0:.3f}, Recall: {1:.3f}, F1 Score: {2:.3f}".format(p, r, f1))
    lstm.save_marginals(session, test_cands)


def _save_model(predicate_resume,lstm):
    date_time=strftime("%d-%m-%Y_%H_%M_%S", gmtime())
    lstm.save("D"+predicate_resume["predicate_name"]+date_time)
    try:
        shutil.rmtree("./checkpoints/"+"D"+predicate_resume["predicate_name"]+"Latest")
    except:
        print("Latest model not found, not removed")
    lstm.save("D"+predicate_resume["predicate_name"]+"Latest")
    logging.info("End training disc ")

