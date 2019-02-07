#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M%S") 
NAME="$DATE.jpg"

fswebcam -r 320x240 --fps 15 -S 2 --no-banner --jpeg 85 /home/pi/pictures/$NAME

echo $NAME
