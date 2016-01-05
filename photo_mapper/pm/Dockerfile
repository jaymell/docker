FROM debian
RUN apt-get update
#RUN apt-get upgrade
RUN apt-get install -y python-dev \
	python-setuptools \
	libtiff5-dev \
	libjpeg62-turbo-dev \
	zlib1g-dev \
	libfreetype6-dev \
	liblcms2-dev \
	libwebp-dev \
	tcl8.6-dev \
	tk8.6-dev \
	python-tk \
	python-pip \
	git \
	wget
WORKDIR /app 
RUN git clone https://github.com/jaymell/photo_mapper .
RUN mkdir ./public/img
RUN pip install -r requirements.txt 
RUN ./get_jpgps.sh
ADD config ./
VOLUME [ "/import", "./public/img" ]
CMD ["/usr/bin/python app.py"]
