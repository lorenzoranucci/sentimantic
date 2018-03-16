#!/bin/bash


source activate py2Env
pip install --requirement python-package-requirement.txt
git submodule update --init --recursive



#Download Wikipedia dump
mkdir ./data/wikipedia/dump/en -p
wget -q -O ./data/wikipedia/dump/en/dump.xml.bz2 https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles1.xml-p10p30302.bz2


