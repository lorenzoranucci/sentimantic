FROM ubuntu:16.04

ENV PATH="/root/miniconda2/bin:${PATH}"
ENV SNORKELHOME="/home/Sentimantic/snorkel"
ENV PYTHONPATH="/home/Sentimantic/snorkel:/home/Sentimantic/snorkel/treedlib:/home/Sentimantic/snorkel/sentimantic:${PYTHONPATH}"

RUN mkdir /home/Sentimantic
WORKDIR /home/Sentimantic
COPY ./ /home/Sentimantic



RUN apt-get update && \
 apt-get install -y git  && \
 apt-get install -y bzip2 && \
 apt-get install gcc -y && \
 apt-get install build-essential python-dev python-virtualenv unzip -y


RUN curl https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
RUN chmod +x Miniconda2-latest-Linux-x86_64.sh
RUN ./Miniconda2-latest-Linux-x86_64.sh -b && \
	export PATH="/root/miniconda2/bin:${PATH}" && \
	conda create -n py2Env python=2.7 anaconda && \
	/bin/bash -c "source activate py2Env" && \
	conda install numba && \
	pip install --requirement /home/Sentimantic/python-package-requirement.txt
	
	


