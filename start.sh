#!/bin/bash

. /opt/venv/bin/activate && exec python ./master.py &
p1=$!
. /opt/venv/bin/activate && exec python ./gui_app.py &
p2=$!
wait $p1 $p2