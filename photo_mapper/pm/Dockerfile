# https://github.com/CentOS/sig-cloud-instance-images

#FROM scratch
FROM centos
MAINTAINER The CentOS Project <cloud-ops@centos.org>
#ADD c7-docker.tar.xz /
LABEL Vendor="CentOS"
LABEL License=GPLv2
RUN yum update -y
RUN yum install -y epel-release
RUN yum install -y python-pip
RUN yum install -y git
RUN yum install -y nodejs
RUN yum install -y npm
RUN yum install -y python-pillow-devel
RUN yum install -y wget
RUN cd / && git clone https://github.com/jaymell/photo_mapper /app
WORKDIR /app 
RUN ls -la
RUN pip install -r requirements.txt 
RUN npm install
RUN ./get_jpgps.sh
VOLUME [ "./cfg", "/import" ]
CMD ["/bin/bash"]
