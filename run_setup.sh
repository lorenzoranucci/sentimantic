#!/bin/bash

cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py setup parallelism 8

cd ./snorkel/snorkel/contrib/brat/brat-v1.3_Crunchy_Frog/data/
sudo chown -R www-data:www-data ./*

