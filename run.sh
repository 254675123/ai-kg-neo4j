#!/bin/bash

PID_FILE="pid_file"

if [ "$1" = "stop" ]; then
    pid=$(cat $PID_FILE)
    kill -9 $pid
else
    if [ -f "/usr/local/python-2.7/bin/python2.7" ]; then
        nohup /usr/local/python-2.7/bin/python2.7 service.py --port=8888 --log_file_prefix=tornado_8888.log "$@" > nohup.log 2>&1 &
    else
        nohup python2 service.py --port=8888 --log_file_prefix=tornado_8888.log "$@" > nohup.log 2>&1 &
    fi
    echo $! > $PID_FILE
fi
