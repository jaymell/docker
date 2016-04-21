#!/bin/bash

TAG=latest
TAG_URL=799617403160.dkr.ecr.us-east-1.amazonaws.com
[[ -z $1 ]] && echo "No Image specified. Building all of them"
image_list=$(find . -maxdepth 1 -type d)
login=$(aws ecr get-login --region us-east-1)
$login
for IMAGE in $image_list
do
	IMAGE=$(basename $IMAGE)
	echo "Building $IMAGE... "
	URL=$TAG_URL/$IMAGE
	docker build -t $URL:$TAG .
	# background this since it won't affect subsequent builds:
	docker push $URL:$TAG &
done

