#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py infer download extract label train test clear parallelism 32

