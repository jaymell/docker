#!/bin/bash

project_name=photo_mapper

image_dir="/var/lib/${project_name}"
db=$project_name
collection=$project_name

rm -f $image_dir/*
mongo $db  --eval "db.${collection}.drop();"
