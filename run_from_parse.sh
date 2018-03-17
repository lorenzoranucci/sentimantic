#!/bin/bash

source activate py2Env
cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py parse infer download extract label train test clear parallelism 32
