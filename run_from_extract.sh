#!/bin/bash

source activate py2Env
cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py extract label train test clear parallelism 32

