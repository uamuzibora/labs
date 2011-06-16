#!/bin/bash

path=`dirname $0`

filename=$path/webroot/index.py

if [ $1 = start ]
then 
    if [ -f $path/labs/pid ]
    then
	sudo kill -9 `cat $path/pid`
	sudo rm $path/pid
    fi

    sudo -u www-data python $filename &
    ps a | grep "python $filename" -m 2|awk '{print $1}'>$path/pid
fi
if [ $1 = stop ]
then
    if [ -f $path/pid ]
    then
	sudo kill -9 `cat $path/pid`
	sudo rm $path/pid
    fi
fi