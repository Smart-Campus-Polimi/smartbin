#!/bin/bash

inotifywait -m ~/pictures -e create -e moved_to |
    while read path action file; do
        echo "The file '$file' appeared in directory '$path' via '$action'"
        
        scp $path/$file drosdesd@192.168.1.245:/Users/drosdesd/rasp/	

    done

