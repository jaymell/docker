FROM ubuntu:latest

RUN apt-get update && \
	apt-get install -y \
		python \
		python-pip

RUN pip install \
	awscli \
	boto \
	boto3 
	
VOLUME /root/.aws/
