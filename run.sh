#!/bin/bash


#Extract text with Wikiextractor
if [ ! -e "./data/wikipedia/dump/en/extracted_text/AA/wiki_00.xml" ]; then
	python ./wikiextractor/WikiExtractor.py -b 100G --processes 32 -o ./data/wikipedia/dump/en/extracted_text ./data/wikipedia/dump/en/dump.xml.bz2 
	mv ./data/wikipedia/dump/en/extracted_text/AA/wiki_00  ./data/wikipedia/dump/en/extracted_text/AA/wiki_00.xml 
	echo '<documents>' | cat - ./data/wikipedia/dump/en/extracted_text/AA/wiki_00.xml > temp && mv temp ./data/wikipedia/dump/en/extracted_text/AA/wiki_00.xml
	echo "</documents>" >> ./data/wikipedia/dump/en/extracted_text/AA/wiki_00.xml
fi

cd snorkel/sentimantic/
#run pipeline
python ./complete_pipeline.py parse infer download extract label train test parallelism 64

