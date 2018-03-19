FROM continuumio/anaconda


ENV SNORKELHOME="/home/Sentimantic/snorkel"
ENV PYTHONPATH="/home/Sentimantic/snorkel:/home/Sentimantic/snorkel/treedlib:${PYTHONPATH}"

RUN apt-get update
RUN apt-get install -y wget  && \
 apt-get install -y git  && \
 apt-get install -y bzip2 && \
 apt-get install gcc -y && \
 apt-get install build-essential python-dev python-virtualenv unzip -y && \
 apt-get install libgl1-mesa-glx -y


RUN mkdir /home/Sentimantic
WORKDIR /home/Sentimantic
COPY ./ /home/Sentimantic

RUN /bin/bash -c 'conda install numba &&  cd /home/Sentimantic && pip install --requirement python-package-requirement.txt'





	
	


