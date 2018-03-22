#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py extract label train_gen train_disc test parallelism 64

