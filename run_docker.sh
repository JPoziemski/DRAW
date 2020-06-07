#!/bin/bash

echo "Hello, "$USER". This script runs Docker container \
after validating path to directory containig input files in your local machine, \
which will be shared with Docker container."

echo -n "Enter absolute path to directory containg input files to analysis (annotation, reference, sample, control):"
read input_path


if [ -d "$input_path" ]; then
    :
elif [ ! -d "$input_path" ]; then
    echo "Given path to input_files does not exist."
    exit 1
elif [ "$input_path"=""]; then
    echo "Path to input was not given, quitting."
fi

(sleep 2 && python -m webbrowser http://0.0.0.0:2000/index) &
(sleep 5 && python -m webbrowser http://0.0.0.0:5000) &

docker run -v $input_path:/app/input \
-v $SCRIPTPATH/config_files:/app/config_files \
-v $SCRIPTPATH/output:/app/output \
-p 2000:2000 -p 5000:5000 \
-it draw