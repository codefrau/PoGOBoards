#!/bin/bash
file=raw/`date +'%Y-%m-%dT%H:%M:%S%z'`.txt
echo "Pasting to $file"
pbpaste > "$file"
exec ./raw-to-data.py > data.txt 
