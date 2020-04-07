#!/bin/bash
[ "$USER" == "vanessa" ] && rm -f `git ls-files --others --exclude-standard | grep ^raw/`
file=raw/`date +'%Y-%m-%dT%H:%M:%S%z'`.txt
echo "Pasting to $file"
pbpaste > "$file"
./raw-to-data.py > data.txt && git diff data.txt
