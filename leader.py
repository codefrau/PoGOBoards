#!/usr/bin/env python

import re
import datetime

reData = re.compile('^([0-9:T-]+) +([0-9,]+) +([0-9,]+) +([0-9,]+) +([0-9,]+) +(.*)$')

trainers = {}

for line in open('data.txt', 'r'):
    match = reData.match(line)
    date   = datetime.datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
    catch  = int(match.group(2))
    walk   = int(match.group(3))
    battle = int(match.group(4))
    xp     = int(match.group(5))
    name   = match.group(6).decode("utf-8")

    #print date, catch, walk, battle, xp, name
    
    if name in trainers:
        trainer = trainers[name]
    else:
        trainer = {
            "name": name,
            "entries": []
        }
        trainers[name] = trainer

    trainer["entries"].append({
        "date": date,
        "stats": [catch, walk, battle, xp]
    })



SURROGATE_PAIR = re.compile(u'[\ud800-\udbff][\udc00-\udfff]', re.UNICODE)
def unicodeLen(s):
    return len(SURROGATE_PAIR.sub('.', s))

board = []
longest_name = 0

for name in trainers:
    entries = trainers[name]["entries"]
    if len(entries) > 1:
        first = entries[0]
        last = entries[-1]
        weeks = (last["date"] - first["date"]).total_seconds() / 24 / 60 / 60 / 7
        per_week = []
        for f, l in zip(first["stats"], last["stats"]):
            per_week.append(int((l - f) / weeks))
        board.append({
            "name":   name,
            "scores":  per_week,
        })
        length = unicodeLen(name)
        if length > longest_name:
            longest_name = length

titles = ["Pokemon caught", "km walked", "battles faught", "XP gained"]

for category, title in enumerate(titles):
    print "```"
    print "Top 10 %s / week" % title
    board.sort(key=lambda n: n["scores"][category], reverse = True)
    for i, trainer in enumerate(board):
        name = trainer["name"] 
        name = name + " " * (longest_name - unicodeLen(name))
        score = "{:,}".format(trainer["scores"][category])
        print "%2d. %s %10s" % (i + 1, name, score)
        if i == 9:
            break
    print "```"
    