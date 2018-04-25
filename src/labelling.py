from PyQt5 import QtCore, QtGui, QtWidgets
import logging
from xml.dom import minidom
import time
from snorkel import SnorkelSession
import requests
from snorkel.annotations import LabelAnnotator
from nltk.util import ngrams
import numpy as np
from textacy.similarity  import  levenshtein, jaccard, jaro_winkler, hamming, token_sort_ratio

from snorkel.learning import GenerativeModel
from snorkel.lf_helpers import (
    get_left_tokens, get_right_tokens, get_between_tokens,
    get_text_between, get_tagged_text, contains_token
)
from models import *

from snorkel.models import LabelKey


def predicate_candidate_labelling(predicate_resume,  parallelism=1,  limit=None, replace_key_set=False):
    logging.info("Starting labeling ")
    session = SnorkelSession()
    try:
        candidate_subclass=predicate_resume["candidate_subclass"]
        key_group=predicate_resume["label_group"]

        cids_query=session.query(candidate_subclass.id).filter(candidate_subclass.split == 0)

        ##skip cands already extracted
        #alreadyExistsGroup=session.query(LabelKey).filter(LabelKey.group==key_group).count()>0
        #if alreadyExistsGroup:
        #    cids_query= get_train_cids_not_labeled(predicate_resume,session)

        #if limit !=None:
        #    cids_query=cids_query.filter(candidate_subclass.id<limit)


        LFs = get_labelling_functions(predicate_resume)

        labeler = LabelAnnotator(lfs=LFs)
        np.random.seed(1701)

        ##if first run or adding a new labeling functionS is needed to set replace key set to True
        #if not replace_key_set:
        #    replace_key_set=not alreadyExistsGroup
        L_train=labeler.apply(parallelism=parallelism, cids_query=cids_query,
                                key_group=key_group, clear=True, replace_key_set=True)
        print(L_train.lf_stats(session))
        logging.info(L_train.lf_stats(session))



    finally:
        logging.info("Finished labeling ")





def get_labelling_functions(predicate_resume):
    subject_type=predicate_resume["subject_type"]
    object_type=predicate_resume["object_type"]
    subject_type_split = subject_type.split('/')
    object_type_split = object_type.split('/')
    subject_type_end=subject_type_split[len(subject_type_split)-1]
    object_type_end=object_type_split[len(object_type_split)-1]
    SentimanticSession = get_sentimantic_session()
    sentimantic_session = SentimanticSession()

    tmp_words=set([])
    for word in predicate_resume["configs"]["words"]:
        tmp_words.add(word)
        tmp_words.add(word.title())
    words=tmp_words

    tmp_words=set([])
    for word in predicate_resume["configs"]["not_words"]:
        tmp_words.add(word)
        tmp_words.add(word.title())
    not_words=tmp_words

    def LF_distant_supervision(c):
        try:
            subject_span=getattr(c,"subject").get_span()
            object_span=getattr(c,"object").get_span()
            if subject_span==object_span:
                return -1
            if is_in_known_samples(predicate_resume,sentimantic_session,subject_span,object_span):
                return 1

            sample_subject_span= getattr(c,"subject")
            sample_subjects=get_nouns(sample_subject_span,subject_type_end)
            sample_object_span = getattr(c,"object")
            sample_objects=get_nouns(sample_object_span,object_type_end)

            sample_subjects.append(subject_span)
            sample_objects.append(object_span)
            for sample_subject in sample_subjects:
                for sample_object in sample_objects:
                    # if (sample_subject, sample_object)in known_samples:
                    if is_in_known_samples(predicate_resume,sentimantic_session,sample_subject,sample_object):
                        return 1
            #todo implement date
            #return -1 if len(words.intersection(c.get_parent().words)) < 1 and np.random.rand() < 0.15 else 0
            #return -1 if len(words.intersection(c.get_parent().words)) < 1 else 0
            return 0
            return -1 if np.random.rand() < 0.15 else 0
        except Exception as e:
            print(e)
            print("Not found candidate"+str(c.id))
            return 0

    def LF_distant_supervision_and_words(c):
        try:
            subject_span=getattr(c,"subject").get_span()
            object_span=getattr(c,"object").get_span()
            if subject_span==object_span:
                return -1
            if (len(words.intersection(c.get_parent().words)) < 1 \
                    or len(not_words.intersection(get_between_tokens(c)))>0) :
                return 0

            if subject_span==object_span:
                return -1
            if is_in_known_samples(predicate_resume,sentimantic_session,subject_span,object_span):
                return 1

            sample_subject_span= getattr(c,"subject")
            sample_subjects=get_nouns(sample_subject_span,subject_type_end)
            sample_object_span = getattr(c,"object")
            sample_objects=get_nouns(sample_object_span,object_type_end)

            sample_subjects.append(subject_span)
            sample_objects.append(object_span)
            for sample_subject in sample_subjects:
                for sample_object in sample_objects:
                    # if (sample_subject, sample_object)in known_samples:
                    if is_in_known_samples(predicate_resume,sentimantic_session,sample_subject,sample_object):
                        return 1

            #todo implement date
            return 0
        except Exception as e:
            print(e)
            print("Not found candidate"+str(c.id))
            return 0

    def LF_distant_supervision2(c):
        try:
            subject_span=getattr(c,"subject").get_span()
            object_span=getattr(c,"object").get_span()
            if subject_span==object_span:
                return -1
            # if (subject_span, object_span)in known_samples:
            if is_in_known_samples(predicate_resume,sentimantic_session,subject_span,object_span):
                return 1
            subject_span=getattr(c,"subject")
            object_span=getattr(c,"object")
            if is_in_known_samples2(predicate_resume,sentimantic_session,subject_span,object_span):
                return 1

            return -1 if len(words.intersection(c.get_parent().words)) < 1 else 0
        except Exception as e:
            print(e)
            print("Not found candidate"+str(c.id))
            return 0

    def LF_not_words(c):
        return -1 if len(not_words.intersection(get_between_tokens(c))) > 0 else 0

    def LF_no_word_in_sentence(c):
        return -1 if np.random.rand() < 0.85 \
                     and len(words.intersection(c.get_parent().words)) == 0 else 0

    def LF_not_words_between(c):
        if len(not_words.intersection(get_between_tokens(c))) > 0:
            return 1
        return 0
    def LF_not_words_left(c):
        if len(not_words.intersection(get_left_tokens(c))) > 0:
            return 1
        return 0
    def LF_not_words_right(c):
        if len(not_words.intersection(get_right_tokens(c))) > 0:
            return 1
        return 0


    def LF_words_between(c):
        if len(words.intersection(get_between_tokens(c))) > 0:
            return 1
        return 0
    def LF_words_left(c):
        if len(words.intersection(get_left_tokens(c))) > 0:
            return 1
        return 0
    def LF_words_right(c):
        if len(words.intersection(get_right_tokens(c))) > 0:
            return 1
        return 0

    Lfs=[
        LF_distant_supervision,
        #LF_distant_supervision_and_words,
        LF_words_between,
        LF_words_left,
        LF_words_right,
        LF_not_words,
        LF_no_word_in_sentence
    ]
    return Lfs


def get_nouns(span, type):
    clean_noun=get_clean_noun(span)
    ngrams=get_ngrams(clean_noun)
    if len(ngrams)<1:
        return span.get_span()
    return get_dbpedia_noun(ngrams,type)

def get_dbpedia_noun(ngrams, type):
    result=None
    for ngram in ngrams:
        noun=' '.join(ngram)
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
                if are_nouns_similar(label,noun):
                    if result==None:
                        result=[]
                    # try:
                    #     label=label.decode("utf-8", errors='ignore').replace(",", "").encode("utf-8")
                    # except:
                    #     label=label
                    result.append(label)
        finally:
            if result != None:
                break
    if result == None:
        result=[]
    return result

def get_clean_noun(span):
    start_word=span.get_word_start()
    end_word=span.get_word_end()
    sentence_pos_tags=span.sentence.pos_tags
    sentence_words=span.sentence.words
    result=[]
    for i in range(start_word,end_word+1):
        if 'NN' in sentence_pos_tags[i]:
            result.append(sentence_words[i])
    return ' '.join(result)

def get_ngrams(string_):
    string_list=string_.split(" ")
    result=[]
    for i in range(len(string_list),0,-1):
        for j in ngrams(string_list,i):
            result.append(j)
    return result



def is_in_known_samples(predicate_resume,session,subject,object):
    sample_class=predicate_resume["sample_class"]
    return session.query(sample_class). \
        filter(sample_class.subject==subject). \
        filter(sample_class.object==object).\
               count()>0

def is_in_known_samples2(predicate_resume,session,subject_span, object_span):
    subject_span=get_clean_noun(subject_span)
    object_span=get_clean_noun(object_span)

    if subject_span==object_span:
        return False

    #search subject in subject sample
    good_samples_by_subject=get_like_known_sample_by_subject(predicate_resume,session,subject_span)
    for good_sample in good_samples_by_subject:
        if are_nouns_similar(subject_span,good_sample.subject) \
        and are_nouns_similar(object_span,good_sample.object):
            return True

    #search object in object sample
    good_samples_by_object=get_like_known_sample_by_object(predicate_resume,session,object_span)
    for good_sample in good_samples_by_object:
        if are_nouns_similar(subject_span,good_sample.subject) \
        and are_nouns_similar(object_span,good_sample.object):
            return True

    return False

def are_nouns_similar(noun1, noun2):
    # jaccard, jaro_winkler, hamming, token_sort_ratio
    jaccardD=jaccard(noun1, noun2)
    jaro=jaro_winkler(noun1, noun2)
    lev=levenshtein(noun1, noun2)
    hammingD=hamming(noun1, noun2)
    tsr=token_sort_ratio(noun1, noun2)
    dice=dice_coefficient(noun1,noun2)
    if lev > 0.42:
        return True


def get_like_known_sample_by_subject(predicate_resume,session,noun):
    sample_class=predicate_resume["sample_class"]
    return session.query(sample_class). \
               filter(sample_class.subject.like("%"+noun+"%")). \
               all()

def get_like_known_sample_by_object(predicate_resume,session,noun):
    sample_class=predicate_resume["sample_class"]
    return session.query(sample_class). \
        filter(sample_class.object.like("%"+noun+"%")). \
        all()

def dice_coefficient(a, b):
    """dice coefficient 2nt/na + nb."""
    if not len(a) or not len(b): return 0.0
    if len(a) == 1:  a=a+u'.'
    if len(b) == 1:  b=b+u'.'

    a_bigram_list=[]
    for i in range(len(a)-1):
        a_bigram_list.append(a[i:i+2])
    b_bigram_list=[]
    for i in range(len(b)-1):
        b_bigram_list.append(b[i:i+2])

    a_bigrams = set(a_bigram_list)
    b_bigrams = set(b_bigram_list)
    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0/(len(a_bigrams) + len(b_bigrams))
    return dice_coeff