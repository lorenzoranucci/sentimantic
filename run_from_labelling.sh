#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py label train_gen train_disc test parallelism 32

cd ../snorkel/snorkel/contrib/brat/brat-v1.3_Crunchy_Frog/data/
chown -R www-data:www-data ./*
