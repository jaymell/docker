FROM ubuntu:latest

RUN apt-get update && \
	apt-get install -y \
		python \
		python-pip \
		vim-common \
        less

RUN pip install \
	awscli \
	boto \
	boto3 
	
RUN mkdir /root/.aws/
ADD credentials.template /root/.aws/credentials

#VOLUME /root/.aws/
