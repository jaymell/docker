#!/bin/bash -e

login=$(aws ecr get-login --region us-east-1)
$login
