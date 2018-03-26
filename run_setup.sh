#!/bin/bash

cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py setup parallelism 1

cd ../snorkel/contrib/brat/brat-v1.3_Crunchy_Frog/data/
chown -R www-data:www-data ./*

