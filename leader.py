#!/usr/bin/env python

import re
import dateparser

reAuthorDate = re.compile('^(.*)((Last )?[A-Z][a-z]+day at [1-9][0-9]?:[0-9][0-9] (AM|PM))$') 

def parseAuthorDate(line):
    match = reAuthorDate.match(line)
    author = match.group(1)
    date = dateparser.parse(match.group(2))
    return (author, date.isoformat())


reCJBX = re.compile('^![cjbx]{4} +([0-9,]+) +([0-9,]+) +([0-9,]+) +([0-9,]+)$') 

def parseCJBX(line):
    match = reCJBX.match(line)
    catch = int(match.group(1).replace(',', ''))
    walk = int(match.group(2).replace(',', ''))
    battle = int(match.group(3).replace(',', ''))
    xp = int(match.group(4).replace(',', ''))
    return (catch, walk, battle, xp)
    
    
prev_line = ''
for line in open('raw.txt', 'r'):
    if line.startswith('!'):
        trainer, date = parseAuthorDate(prev_line)
        catch, walk, battle, xp = parseCJBX(line)
        print '%s %6d %6d %6d %9d %s' % (date, catch, walk, battle, xp, trainer)
    prev_line = line
