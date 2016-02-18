#!/bin/bash
image_dir=/var/lib/photo_mapper
rm -f $image_dir/*
mongo photo_mapper --eval "db.photo_mapper.drop();"
