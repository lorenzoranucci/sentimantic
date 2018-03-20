#!/bin/bash

source activate py2Env
cd snorkel/sentimantic/
#run pipeline
python gold_label_creator.py "http://dbpedia.org/ontology/birthPlace"
./run_brat.sh

