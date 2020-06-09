#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
input_path="$SCRIPTPATH/input"


# if [ -z "$(ls -A $input_path)" ]; then
#    echo "Input directory is empty. Place input files in directory: $input_path"
#    exit 1
# else
#    :
# fi

x-www-browser http://0.0.0.0:2000/index 
sleep 1
x-www-browser http://0.0.0.0:5000/bkapp 
sleep 1

docker run -v $SCRIPTPATH/input:/app/input \
-v $SCRIPTPATH/config_files:/app/config_files \
-v $SCRIPTPATH/output:/app/output \
-p 2000:2000 -p 5000:5000 \
-it draw
