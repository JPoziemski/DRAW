#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
input_path="$SCRIPTPATH/input"

google-chrome --disable-gpu http://0.0.0.0:2000/index 
sleep 1
google-chrome --disable-gpu http://0.0.0.0:5000/bkapp 


docker run -v $SCRIPTPATH/input:/app/input \
-v $SCRIPTPATH/config_files:/app/config_files \
-v $SCRIPTPATH/output:/app/output \
-p 2000:2000 -p 5000:5000 \
-it draw
