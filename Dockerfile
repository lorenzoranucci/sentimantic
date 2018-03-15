FROM continuumio/anaconda


ENV SNORKELHOME="/home/Sentimantic/snorkel"
ENV PYTHONPATH="/home/Sentimantic/snorkel:/home/Sentimantic/snorkel/treedlib:${PYTHONPATH}"

RUN mkdir /home/Sentimantic
WORKDIR /home/Sentimantic
COPY ./ /home/Sentimantic







	
	


