#!/bin/bash
git add data.txt names.txt raw/*
git commit -m "new data"
git log -1 --stat

