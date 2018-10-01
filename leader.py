#!/usr/bin/env python

import sys
import re
import math
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

month = latest.strftime("%B")
latest = latest.strftime("%b %d, %I:%M %p")

reName = re.compile('^((.*)#[0-9]+) ?(.*)$')

for line in open('names.txt', 'r'):
    match = reName.match(line.decode("utf-8"))
    handle = match.group(1)
    name = (match.group(3) or match.group(2))
    if name in trainers:
        trainers[name]["handle"] = handle
    else:
        sys.stderr.write(line)
        raise Exception("Name not in data: '%s'" % name.encode('utf-8'))

board = []

for name in trainers:
    entries = trainers[name]["entries"]
    if len(entries) < 2 or "error" in trainers[name]:
        continue
    first = entries[0]
    last = entries[-1]
    days = 0
    for i in range(0, len(entries) - 1):
        d = math.ceil((last["date"] - entries[i]["date"]).total_seconds() / 24 / 60 / 60)
        if d >= 28 or days == 0:
            if days > 0:
                print "was %s now %s days, skipping %s, using %s" % (days, d, first["date"], entries[i]["date"])
            first = entries[i]
            days = d
    trainers[name]["days"] = days
    if days < 6:
        continue
    per_month = []
    for f, l in zip(first["stats"], last["stats"]):
        per_month.append(int((l - f) / days * 30))
    board.append({
        "name":   name,
        "scores":  per_month,
        "totals":  last["stats"],
    })

titles = [":badge_catch: Number of Pokemon caught", ":badge_walk: KM walked", ":badge_battle: Battles fought", ":badge_xp: XP gained"]
places = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]

TTY = sys.stdout.isatty()
for TOP10 in [TTY]:
    for U40 in [False, True]:
        if U40 and not TOP10:
            break
        for category, title in enumerate(titles):
            if TOP10:
                if U40:
                    print "**%s in 30 days (under Lvl 40):**" % title
                else:
                    print "**%s in 30 days:**" % title
            else:
                print "**%s:**" % title
                print "```"
            board.sort(key=lambda trainer: trainer["scores"][category], reverse = True)
            formatted_scores = ["{:,}".format(trainer["scores"][category]) for trainer in board]
            formatted_totals = ["{:,}".format(trainer["totals"][category]) for trainer in board]
            longest_score = max(6, max([len(str(n)) for n in formatted_scores]))
            longest_total = max(5, max([len(str(n)) for n in formatted_totals]))
            if not TOP10:
                print "%sMonth %sTotal" % (" " * (longest_score - 5), " " * (longest_total - 5 - max(0, 5-longest_score)))
            place = 1
            for i, trainer in enumerate(board):
                name = trainer["name"]
                score = formatted_scores[i]
                total = formatted_totals[i]
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
                    score_pad = " " * (longest_score - len(score))
                    total_pad = " " * (longest_total - len(total))
                    print "%s%s %s%s %s" % (score_pad, score, total_pad, total, name.encode('utf-8'))
                if place == 10:
                    if TOP10:
                        break
                    else:
                        print "%s----- Top 10 -----" % score_pad
                place = place + 1
            print "" if TOP10 else "```*Updated: %s*\n" % latest
        if TOP10:
            print "*Updated: %s*\n" % latest

for name in trainers:
    trainer = trainers[name]
    if "error" in trainer:
        if "handle" in trainer:
            sys.stderr.write("Stat got lower in submission from @%s:\n" % trainer["handle"].encode('utf-8'))
        else:
            sys.stderr.write("Stat got lower in submission from %sn" % trainer["name"].encode('utf-8'))
        sys.stderr.write("```\n")
        for entry in trainer["entries"]:
            sys.stderr.write("%s %s\n" % (entry["date"].isoformat(), entry["stats"]))
        sys.stderr.write("```\n")
