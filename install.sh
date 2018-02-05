#!/bin/bash

#Download Wikipedia dump
mkdir ./data/wikipedia/dump/en
wget -q -O ./data/wikipedia/dump/en/dump.xml.bz2 https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles1.xml-p10p30302.bz2


