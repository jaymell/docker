#!/bin/bash 

REPO_URL=799617403160.dkr.ecr.us-east-1.amazonaws.com
TAG=$(basename $(pwd))
TAG_VER="latest"

docker build -t $REPO_URL/$TAG:$TAG_VER .

