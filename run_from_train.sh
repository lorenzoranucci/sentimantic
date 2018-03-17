#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py train test clear parallelism 32

