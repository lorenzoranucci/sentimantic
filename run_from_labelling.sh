#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py label train_gen train_disc test parallelism 32


