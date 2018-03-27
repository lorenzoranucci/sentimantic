#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py extract label train_gen train_disc test parallelism 32 page_size 100000 limit 100000
