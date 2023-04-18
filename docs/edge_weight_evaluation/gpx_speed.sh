#!/bin/bash

# if required:
# chmod +x gpx_speed.sh
# sed -i -e 's/\r$//' gpx_speed.sh

read folder

rename -f 'y/A-Z/a-z/' ./$folder/*
rename -f 'y/( |\-)/_/' ./$folder/*

for f in ./$folder/*.gpx; do gpsbabel -t -i gpx -f $f -x track,speed -o gpx,gpxver=1.0 -F speed_${f##*/}; done