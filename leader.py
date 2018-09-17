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
    if len(entries) < 2:
        continue
    first = entries[0]
    last = entries[-1]
    days = (last["date"] - first["date"]).total_seconds() / 24 / 60 / 60
    if days < 6.5:
        continue
    per_week = []
    for f, l in zip(first["stats"], last["stats"]):
        per_week.append(int((l - f) / days * 7))
    board.append({
        "name":   name,
        "scores":  per_week,
    })
    length = unicodeLen(name)
    if length > longest_name:
        longest_name = length

titles = [":badge_catch: Number of Pokemon caught", ":badge_walk: KM walked", ":badge_battle: Battles fought", ":badge_xp: XP gained"]

for category, title in enumerate(titles):
    print "**%s per week:**" % title
    print "```"
    board.sort(key=lambda trainer: trainer["scores"][category], reverse = True)
    formatted_numbers = ["{:,}".format(trainer["scores"][category]) for trainer in board]
    longest_number = max([len(str(n)) for n in formatted_numbers])
    for i, trainer in enumerate(board):
        name = trainer["name"]
        name = name + " " * (longest_name - unicodeLen(name))
        score = formatted_numbers[i]
        score = " " * (longest_number - len(score)) + score
        print "%2d   %s   %s" % (i + 1, score, name)
        if i == 9:
            break
    print "```"
