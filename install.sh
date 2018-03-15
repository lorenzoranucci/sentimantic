#!/bin/bash

git submodule update --init --recursive
#cd snorkel/
#pip install --requirement python-package-requirement.txt
#chmod +x set_env.sh
chmod +x install-parser.sh
source activate py2Env
source set_env.sh
source install-parser.sh
cd ..


#Download Wikipedia dump
mkdir ./data/wikipedia/dump/en
wget -q -O ./data/wikipedia/dump/en/dump.xml.bz2 https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles1.xml-p10p30302.bz2


