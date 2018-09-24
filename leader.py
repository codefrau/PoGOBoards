#!/usr/bin/env python

import sys
import re
import datetime

reData = re.compile('^([0-9:T-]+) +([0-9,]+) +([0-9,]+) +([0-9,]+) +([0-9,]+) +(.*)$')

trainers = {}
latest = None

for line in open('data.txt', 'r'):
    match = reData.match(line.decode("utf-8"))
    date   = datetime.datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
    catch  = int(match.group(2))
    walk   = int(match.group(3))
    battle = int(match.group(4))
    xp     = int(match.group(5))
    name   = match.group(6)

    #print date, catch, walk, battle, xp, name
    latest = date
    
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

    if len(trainer["entries"]) > 1:
        prev = trainer["entries"][-2]["stats"]
        this = trainer["entries"][-1]["stats"]
        for p, t in zip(prev, this):
            if p > t:
                trainer["error"] = True

reName = re.compile('^((.*)#[0-9]+) ?(.*)$')

for line in open('names.txt', 'r'):
    match = reName.match(line.decode("utf-8"))
    handle = match.group(1)
    name = (match.group(3) or match.group(2))
    if name in trainers:
        trainers[name]["handle"] = handle
    else:
        print line
        raise Exception("Name not in data: '%s'" % name.encode('utf-8'))

board = []

for name in trainers:
    entries = trainers[name]["entries"]
    if len(entries) < 2 or "error" in trainers[name]:
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

titles = [":badge_catch: Number of Pokemon caught", ":badge_walk: KM walked", ":badge_battle: Battles fought", ":badge_xp: XP gained"]
places = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]

TTY = sys.stdout.isatty()
for TOP10 in [TTY]:
    for U40 in [False, True]:
        if U40 and not TOP10:
            break
        for category, title in enumerate(titles):
            print "**%s per week%s:**" % (title, " (under Lvl 40)" if U40 else "")
            if not TOP10:
                print "```"
            board.sort(key=lambda trainer: trainer["scores"][category], reverse = True)
            formatted_numbers = ["{:,}".format(trainer["scores"][category]) for trainer in board]
            longest_number = max([len(str(n)) for n in formatted_numbers])
            place = 1
            for i, trainer in enumerate(board):
                name = trainer["name"]
                score = formatted_numbers[i]
                xp = trainers[name]["entries"][-1]["stats"][-1]
                if U40 and xp >= 20000000:
                    continue
                if TOP10:
                    try:
                        handle = trainers[name]["handle"]
                    except:
                        raise Exception("%s not found in names.txt" % name.encode('utf-8'))
                    print "%s **%s** @%s" % (places[place-1], score, handle.encode('utf-8'))
                else:
                    score = " " * (longest_number - len(score)) + score
                    print "%s %s" % (score, name.encode('utf-8'))
                place = place + 1
                if place > 10 and TOP10:
                    break
            if TOP10:
                print
            else:
                print "```*Updated: %s*\n" % latest.strftime("%b %d, %I:%M %p")
        if TOP10:
            print "*Updated: %s*\n" % latest.strftime("%b %d, %I:%M %p")


for name in trainers:
    trainer = trainers[name]
    if "error" in trainer:
        if "handle" in trainer:
            print "Stat got lower in submission from @%s:" % trainer["handle"].encode('utf-8')
        else:
            print "Stat got lower in submission from %s:" % trainer["name"].encode('utf-8')
        print "```"
        for entry in trainer["entries"]:
            print entry["date"].isoformat(), entry["stats"]
        print "```"
