#!/bin/bash


cd snorkel/sentimantic/
#run pipeline
python complete_pipeline.py label train test parallelism 64

