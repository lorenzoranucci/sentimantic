FROM ubuntu:16.04

ENV PATH="/root/anaconda2/bin:${PATH}"
ENV SNORKELHOME="/home/Sentimantic/snorkel"
ENV PYTHONPATH="/home/Sentimantic/snorkel:/home/Sentimantic/snorkel/treedlib:/home/Sentimantic/snorkel/sentimantic:${PYTHONPATH}"

RUN mkdir /home/Sentimantic
WORKDIR /home/Sentimantic
COPY ./ /home/Sentimantic



RUN apt-get update && \
 apt-get install -y wget  && \
 apt-get install -y git  && \
 apt-get install -y bzip2 && \
 apt-get install gcc -y && \
 apt-get install build-essential python-dev python-virtualenv unzip -y


RUN wget https://repo.continuum.io/archive/Anaconda2-5.1.0-Linux-x86_64.sh
RUN chmod +x Anaconda2-5.1.0-Linux-x86_64.sh
RUN ./Anaconda2-5.1.0-Linux-x86_64.sh -b && \
	 && \
	conda create -n py2Env python=2.7 anaconda && \
	/bin/bash -c "source activate py2Env" && \
	conda install numba # &&	pip install --requirement /home/Sentimantic/python-package-requirement.txt
	
	


