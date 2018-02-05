#!/bin/bash

#Extract text with Wikiextractor
./wikiextractor/WikiExtractor.py -cb 250K -o ./data/wikipedia/dump/en/extracted_text ./data/wikipedia/dump/en/dump.xml.bz2 

#Merge extracted chunks into one file
find ./data/wikipedia/dump/en/extracted_text -name '*bz2' -exec bzip2 -dc {} \; > ./data/wikipedia/dump/en/extracted_text/complete.xml

