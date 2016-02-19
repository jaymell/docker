#!/bin/bash

#####
# build:
#####
cd ~/src/docker/photo_mapper/dev-pm-flask-2
sudo docker build --no-cache=true -t dev-pm-flask .

#####
# stop and restart:
#####
docker_interface_ip=$(ip addr | grep docker0 | grep inet  | awk '{print $2}' | awk -F/ '{print $1}')
echo "Stopping existing containers... "
sudo docker stop pm-flask 
sudo docker stop pm-nginx

echo "Deleting existing containers... "
sudo docker rm pm-flask 
sudo docker rm pm-nginx

echo "Starting containers... "
sudo docker run -d \
	--name pm-flask \
	-e MONGODB_HOST=$docker_interface_ip \
	-e USE_S3=False \
    -v /var/lib/photo_mapper:/app/static/img \
	dev-pm-flask

sudo docker run -d \
	--name pm-nginx \
	--link pm-flask \
	-p 80:80 \
	pm-nginx
