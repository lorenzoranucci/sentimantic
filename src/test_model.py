import logging
from snorkel import SnorkelSession
from snorkel.learning.disc_models.rnn import reRNN
from snorkel.annotations import  LabelAnnotator
from snorkel.learning import GenerativeModel
from labelling import get_labelling_functions
from models import *
import matplotlib.pyplot as plt
from os import mkdir
import csv
from time import gmtime, strftime

from textacy.similarity  import  levenshtein
from xml.dom import minidom
import time
import requests


def test_model(predicate_resume,gen_model_name=None, disc_model_name=None, parallelism=1):
    try:
        mkdir("./results")
    except:
        print("Dir not created")

    date_time=strftime("%Y-%m-%d_%H_%M_%S", gmtime())

    session = SnorkelSession()
    L_gold_test = get_gold_test_matrix(predicate_resume,session)
    score_disc_model(predicate_resume, L_gold_test,session, date_time,disc_model_name)

    score_lfs(predicate_resume, L_gold_test,session,date_time, parallelism=parallelism)

    #score_gen_model(predicate_resume,session,date_time,gen_model_name)






def score_disc_model(predicate_resume, L_gold_test, session, date_time, disc_model_name=None):





    if disc_model_name is None:
        disc_model_name="D"+predicate_resume["predicate_name"]+"Latest"
    candidate_subclass=predicate_resume["candidate_subclass"]
    test_cands_query  = session.query(candidate_subclass).filter(candidate_subclass.split == 2).order_by(candidate_subclass.id)

    test_cands=test_cands_query.all()
    lstm = reRNN()
    logging.info("Loading marginals ")
    lstm.load(disc_model_name)
    #lstm.save_marginals(session, test_cands)




    p, r, f1 = lstm.score(test_cands, L_gold_test)
    print("Prec: {0:.3f}, Recall: {1:.3f}, F1 Score: {2:.3f}".format(p, r, f1))
    logging.info("Prec: {0:.3f}, Recall: {1:.3f}, F1 Score: {2:.3f}".format(p, r, f1))
    dump_file_path1="./results/"+"test_disc_1_"+predicate_resume["predicate_name"]+date_time+".csv"
    with open(dump_file_path1, 'w+b') as f:
        writer = csv.writer(f, delimiter=',',
                             quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Precision","Recall","F1"])
        writer.writerow(["{0:.3f}".format(p),"{0:.3f}".format(r),"{0:.3f}".format(f1)])







    tp, fp, tn, fn = lstm.error_analysis(session, test_cands, L_gold_test)
    logging.info("TP: {}, FP: {}, TN: {}, FN: {}".format(str(len(tp)),
                                                         str(len(fp)),
                                                         str(len(tn)),
                                                         str(len(fn))))
    dump_file_path2="./results/"+"test_disc_2_"+predicate_resume["predicate_name"]+date_time+".csv"
    with open(dump_file_path2, 'w+b') as f:
        writer = csv.writer(f, delimiter=',',
                             quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["TP","FP","TN","FN"])
        writer.writerow([str(len(tp)),
                         str(len(fp)),
                         str(len(tn)),
                         str(len(fn))])





    predictions=lstm.predictions(test_cands)
    marginals=lstm.marginals(test_cands)
    dump_file_path3="./results/"+"test_disc_3_"+predicate_resume["predicate_name"]+date_time+".csv"
    with open(dump_file_path3, 'w+b') as f:
        writer = csv.writer(f, delimiter=',',
                             quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["text","marginal","prediction"])
        i=0
        for candidate in test_cands:
            start=candidate.subject.char_start
            end=candidate.object.char_end+1
            if candidate.object.char_start < candidate.subject.char_start:
                start=candidate.object.char_start
                end=candidate.subject.char_end+1
            text="\""+candidate.get_parent().text[start:end].encode('ascii','ignore')+"\""
            row=[text,str(marginals[i]),str(predictions[i])]
            writer.writerow(row)
            i=i+1


    dump_file_path4="./results/"+"triples_"+predicate_resume["predicate_name"]+date_time+".csv"


    subject_type=predicate_resume["subject_type"]
    object_type=predicate_resume["object_type"]
    subject_type_split = subject_type.split('/')
    object_type_split = object_type.split('/')
    subject_type_end=subject_type_split[len(subject_type_split)-1]
    object_type_end=object_type_split[len(object_type_split)-1]
    with open(dump_file_path4, 'w+b') as f:
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







def score_lfs(predicate_resume, L_gold_test,  session, date_time,parallelism=8):
    dump_file_path="./results/"+"lfs_1_"+predicate_resume["predicate_name"]+date_time+".csv"


    key_group=predicate_resume["label_group"]
    LFs = get_labelling_functions(predicate_resume)
    labeler = LabelAnnotator(lfs=LFs)
    test_cids_query=get_test_cids_with_span(predicate_resume,session)
    L_test=labeler.apply(parallelism=parallelism, cids_query=test_cids_query,
                         key_group=key_group, clear=True, replace_key_set=False)

    data_frame=L_test.lf_stats(session)
    print(data_frame)
    logging.info(data_frame)
    data_frame.to_csv(dump_file_path)


    gen_model = GenerativeModel()
    gen_model.train(L_test, epochs=100, decay=0.95, step_size=0.1 / L_test.shape[0], reg_param=1e-6)


    p, r, f1 = gen_model.score(L_test, L_gold_test)
    print("Prec: {0:.3f}, Recall: {1:.3f}, F1 Score: {2:.3f}".format(p, r, f1))
    logging.info("Prec: {0:.3f}, Recall: {1:.3f}, F1 Score: {2:.3f}".format(p, r, f1))
    dump_file_path1="./results/"+"test_gen_1_"+predicate_resume["predicate_name"]+date_time+".csv"
    with open(dump_file_path1, 'w+b') as f:
        writer = csv.writer(f, delimiter=',',
                             quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Precision","Recall","F1"])
        writer.writerow(["{0:.3f}".format(p),"{0:.3f}".format(r),"{0:.3f}".format(f1)])


    test_marginals = gen_model.marginals(L_test)

    dump_file_path2="./results/"+"plt_1_"+predicate_resume["predicate_name"]+date_time+".csv"
    #plt.hist(test_marginals, bins=20)
    #plt.savefig(dump_file_path2)
    #plt.show()


    dump_file_path3="./results/"+"gen_2_"+predicate_resume["predicate_name"]+date_time+".csv"
    data_frame3=gen_model.learned_lf_stats()
    data_frame3.to_csv(dump_file_path3)

    dump_file_path4="./results/"+"gen_3_"+predicate_resume["predicate_name"]+date_time+".csv"
    tp, fp, tn, fn = gen_model.error_analysis(session, L_test, L_gold_test)
    with open(dump_file_path4, 'w+b') as f:
        writer = csv.writer(f, delimiter=',',
                             quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["TP","FP","TN","FN"])
        writer.writerow([str(len(tp)),
                         str(len(fp)),
                         str(len(tn)),
                         str(len(fn))])

    dump_file_path5="./results/"+"gen_4_"+predicate_resume["predicate_name"]+date_time+".csv"
    data_frame4=L_test.lf_stats(session, L_gold_test, gen_model.learned_lf_stats()['Accuracy'])
    data_frame4.to_csv(dump_file_path5)



def score_gen_model(predicate_resume, session, gen_model_name=None, parallelism=16):
    if gen_model_name is None:
        model_name="G"+predicate_resume["predicate_name"]+"Latest"
    logging.info("Stats logging")
    key_group=predicate_resume["label_group"]
    train_cids_query=get_train_cids_with_span(predicate_resume,session)
    L_train = load_ltrain(predicate_resume,session)
    gen_model = GenerativeModel()
    gen_model.load(model_name)
    gen_model.train(L_train, epochs=100, decay=0.95, step_size=0.1 / L_train.shape[0], reg_param=1e-6)
    logging.info(gen_model.weights.lf_accuracy)
    print(gen_model.weights.lf_accuracy)
    train_marginals = gen_model.marginals(L_train)
    fig=plt.figure()
    #hist=plt.hist(train_marginals, bins=20)
    #plt.savefig("plt"+strftime("%d-%m-%Y_%H_%M_%S", gmtime())+".png", dpi=fig.dpi)
    gen_model.learned_lf_stats()



    # LFs = get_labelling_functions(predicate_resume)
    # labeler = LabelAnnotator(lfs=LFs)
    # L_dev = labeler.apply_existing(cids_query=get_dev_cids_with_span(predicate_resume,session), parallelism=parallelism, clear=False)
    # L_gold_dev = get_gold_dev_matrix(predicate_resume,session)
    # tp, fp, tn, fn = gen_model.error_analysis(session, L_dev, L_gold_dev)
    # logging.info("TP: {}, FP: {}, TN: {}, FN: {}".format(str(len(tp)),
    #                                                      str(len(fp)),
    #                                                      str(len(tn)),
    #                                                      str(len(fn))))




def load_ltrain(predicate_resume, session):
    key_group=predicate_resume["label_group"]
    LFs = get_labelling_functions(predicate_resume)
    labeler = LabelAnnotator(lfs=LFs)
    train_cids_query=get_train_cids_with_span(predicate_resume,session)
    L_train = labeler.load_matrix(session,  cids_query=train_cids_query, key_group=key_group)
    return L_train



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

def are_nouns_similar(noun1, noun2):
    # jaccard, jaro_winkler, hamming, token_sort_ratio
    lev=levenshtein(noun1, noun2)
    if lev > 0.72:
        return True