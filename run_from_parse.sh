#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py parse infer download extract label train test  parallelism 64

