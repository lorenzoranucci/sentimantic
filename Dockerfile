FROM ubuntu:16.04

ENV PATH="~/miniconda2/bin:${PATH}"
WORKDIR /home


RUN mkdir Sentimantic
COPY ./ /home/Sentimantic



RUN apt-get update && \
 apt-get install -y wget  && \
 apt-get install -y git  && \
 apt-get install -y bzip2

RUN wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
RUN chmod +x Miniconda2-latest-Linux-x86_64.sh
RUN ./Miniconda2-latest-Linux-x86_64.sh -b
RUN conda create -n py2Env python=2.7 anaconda

RUN cd Sentimantic
RUN git submodule --init --recursive

RUN cd snorkel
RUN chmod +x set_env.sh && chmod +x install-parser.sh
RUN source activate py2Env && conda install numba && pip install --requirement python-package-requirement.txt && source ./set_env.sh && ./install-parser.sh

