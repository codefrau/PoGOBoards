#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from sys import stdout, stderr
from math import ceil, floor
from datetime import datetime, timedelta
from calendar import monthrange

reData = re.compile('^([0-9:T-]+) +([0-9,]+) +([0-9,]+) +([0-9,]+) +([0-9,]+) +(.*)$')

trainers = {}
latest = None

for line in open('data.txt', 'r'):
    match = reData.match(line.decode("utf-8"))
    date   = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
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
            "entries": [],
            "ranks": {},
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

begin_of_this_month = latest.replace(day=1, hour=0, minute=0)
begin_of_last_month = (begin_of_this_month - timedelta(days=1)).replace(day=1)
is_last_day_of_month = latest.month != (latest + timedelta(days=1)).month

reName = re.compile('^((.*)#[0-9]+) ?(.*)$')

for line in open('names.txt', 'r'):
    match = reName.match(line.decode("utf-8"))
    handle = match.group(1)
    name = match.group(3) or match.group(2)
    if name == "-":
        name = match.group(2)
        del trainers[name]
        print "removing", name.encode('utf-8')
        continue
    if name in trainers:
        trainers[name]["handle"] = handle
    else:
        stderr.write(line)
        raise Exception("Name not in data: '%s'" % name.encode('utf-8'))

board = []

for is_last_month in [True, False] if is_last_day_of_month else [False]:
    begin_date = begin_of_last_month if is_last_month else begin_of_this_month
    end_date = (begin_date + timedelta(days=31)).replace(day=1)
    if end_date > latest:
        end_date = latest.replace(hour=0, minute=0) + timedelta(days=1)
    days_so_far = (end_date - begin_date).days
    print "```\nFinding submissions for calculating gain"
    for name in sorted(trainers.iterkeys(), key=lambda s: s.lower()):
        entries = trainers[name]["entries"]
        if len(entries) < 2 or "error" in trainers[name]:
            continue
        first = entries[0]
        last = entries[-1]
        if last["date"] < begin_date:
            continue
        n = len(entries) - 1
        while last["date"] > end_date and n > 0:
            n -= 1
            last = entries[n]
        days = 0
        for i in range(0, n):
            start = entries[i]["date"].replace(hour=0, minute=0)
            end = last["date"].replace(hour=0, minute=0)
            d = (end - start).days
            if days == 0 or start < begin_date and d >= 6:
                first = entries[i]
                days = d
        trainers[name]["days"] = days
        if days < 6:
            continue
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
        print "%2d days from %s to %s: %s" % (days, first["date"].strftime("%b %d"), last["date"].strftime("%b %d"), name.encode('utf-8'))
        this_month = []
        for f, l in zip(first["stats"], last["stats"]):
            this_month.append((float(l - f) * days_so_far / days))
        board.append({
            "name":   name,
            "scores":  this_month,
            "totals":  last["stats"],
        })
    # sort and assign rank for last month
    if is_last_month:
        for MONTHLY in [False, True]:
            for U40 in [False, True]:
                for category in range(0, 4):
                    board.sort(key=lambda trainer: trainer["scores" if MONTHLY else "totals"][category], reverse = True)
                    place = 1
                    for line in board:
                        trainer = trainers[line["name"]]
                        xp = trainer["entries"][-1]["stats"][-1]
                        if U40 and xp >= 20000000:
                            continue
                        key = "TM"[MONTHLY] + "AU"[U40] + "CJBX"[category]
                        trainer["ranks"][key] = place
                        place += 1
        board = []
    else:
        print "Normalizing to %d days in %s\n```" % (days_so_far, begin_date.strftime("%B"))

titles = [":badge_catch: Number of Pokemon caught", ":badge_walk: KM walked", ":badge_battle: Battles fought", ":badge_xp: XP gained"]
places = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]
month = latest.strftime("%b")
latest = latest.strftime("%b %d, %I:%M %p")

TOP10 = stdout.isatty() and is_last_day_of_month

for MONTHLY in [False, True]:
    if not TOP10 and not MONTHLY:
        continue
    for U40 in [False, True]:
        if U40 and (not TOP10 or not MONTHLY):
            continue
        for category, title in enumerate(titles):
            print "_ _"
            if TOP10:
                if U40:
                    print "**%s in %s (under Lvl 40):**" % (title, month)
                else:
                    if MONTHLY:
                        print "**%s in %s:**" % (title, month)
                    else:
                        print "**%s (All Time):**" % title
            else:
                if is_last_day_of_month:
                    print "**%s (%s):**" % (title, month)
                else:
                    print "**%s (%d %s):**" % (title, days_so_far, "day" if days_so_far == 1 else "days")
                print "```"
            board.sort(key=lambda trainer: trainer["scores" if MONTHLY else "totals"][category], reverse = True)
            template = "{:,.1f}" if MONTHLY and not TOP10 and not is_last_day_of_month else "{:,.0f}"
            formatted_scores = [template.format(trainer["scores"][category]) for trainer in board]
            formatted_totals = [template.format(trainer["totals"][category]) for trainer in board]
            longest_score = max(4, max([len(str(n)) for n in formatted_scores]))
            longest_total = max(5, max([len(str(n)) for n in formatted_totals]))
            #if not TOP10:
            #    print "%sGain %sTotal" % (" " * (longest_score - 3), " " * (longest_total - 5 - max(0, 3-longest_score)))
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
                    try:
                        old_place = trainers[name]["ranks"]["TM"[MONTHLY] + "AU"[U40] + "CJBX"[category]]
                        updown = ":more:" if old_place > place else (":less:" if old_place < place else ":same:")
                    except:
                        updown = ":new:"                        
                    print "%s%s **%s** @%s" % (places[place-1], updown.encode('utf-8'), score if MONTHLY else total, handle.encode('utf-8'))
                else:
                    score_pad = " " * (longest_score - len(score))
                    total_pad = " " * (longest_total - len(total))
                    if is_last_day_of_month:
                        print "%s%s %s%s %s" % (score_pad, score, total_pad, total, name.encode('utf-8'))
                    else:
                        print "%s%s %s" % (score_pad, score, name.encode('utf-8'))
                if place == 10:
                    if TOP10:
                        break
                    else:
                        print "%s----- Top 10 -----" % score_pad
                place = place + 1
            print "" if TOP10 else "```" if is_last_day_of_month else "```*Last entry: %s*\n" % latest
        if TOP10:
            print "\n"

for name in trainers:
    trainer = trainers[name]
    if "error" in trainer:
        if "handle" in trainer:
            stderr.write("Stat got lower in submission from @%s:\n" % trainer["handle"].encode('utf-8'))
        else:
            stderr.write("Stat got lower in submission from %s:\n" % trainer["name"].encode('utf-8'))
        stderr.write("```\n")
        for entry in trainer["entries"]:
            stderr.write("%s %s\n" % (entry["date"].isoformat(), entry["stats"]))
        stderr.write("```\n")
