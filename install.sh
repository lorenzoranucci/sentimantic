#!/bin/bash

git submodule update --init --recursive

#Download Wikipedia dump
if [ ! -e "./data/wikipedia/dump/en/dump.xml.bz2" ]; then
    mkdir ./data/wikipedia/dump/en -p
    wget  -O ./data/wikipedia/dump/en/dump.xml.bz2 https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles1.xml-p10p30302.bz2
fi

