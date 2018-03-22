#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py train_disc test  parallelism 64

