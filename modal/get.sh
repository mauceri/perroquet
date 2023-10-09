#!/bin/zsh

curl -X 'GET' \
  "$1?user_agent=$2" \
  -H 'accept: application/json'
