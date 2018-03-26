#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py  test parallelism 32

cd ../snorkel/snorkel/contrib/brat/brat-v1.3_Crunchy_Frog/data/
chown -R www-data:www-data ./*
