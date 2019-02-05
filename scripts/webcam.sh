#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M") 
NAME="$DATE.jpg"

fswebcam -r 320x240 --no-banner /home/pi/pictures/$NAME

#echo $NAME
