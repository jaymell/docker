#http://docs.opencv.org/2.4/doc/tutorials/introduction/linux_install/linux_install.html
FROM ubuntu
RUN apt-get update 
RUN apt-get install -y build-essential && \
	apt-get clean
RUN apt-get install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev && \
	apt-get clean
RUN apt-get install -y python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev && \
	apt-get clean
RUN git clone --depth 1 https://github.com/Itseez/opencv.git

