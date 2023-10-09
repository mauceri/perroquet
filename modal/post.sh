#!/bin/zsh

curl -X 'POST' \
$1 \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d $2