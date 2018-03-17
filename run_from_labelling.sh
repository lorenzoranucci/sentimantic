#!/bin/bash

source activate py2Env
cd snorkel/sentimantic/
#run pipeline
python snorkel/sentimantic/complete_pipeline.py label train test clear parallelism 32

