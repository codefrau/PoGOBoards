#!/usr/bin/env python

import os
import re
import dateparser

reAuthorDate = re.compile('^(.*)([A-Z][a-z]+day at [1-9][0-9]?:[0-9][0-9] (AM|PM))$')

def parseAuthorDate(line, file_date):
    match = reAuthorDate.match(line)
    author_str = match.group(1)
    date_str = match.group(2)
    if author_str.endswith('Last '):
        author_str = author_str[:-5]
    date = dateparser.parse(date_str, settings={'RELATIVE_BASE': file_date})
    return (author_str, date.isoformat())


reCJBX = re.compile('^![cjbx]{4} +([0-9,]+) +([0-9,]+) +([0-9,]+) +([0-9,]+)(\(edited\))?$')

def parseCJBX(line):
    match = reCJBX.match(line)
    catch  = int(match.group(1).replace(',', ''))
    walk   = int(match.group(2).replace(',', ''))
    battle = int(match.group(3).replace(',', ''))
    xp     = int(match.group(4).replace(',', ''))
    return (catch, walk, battle, xp)
    

raw_files = os.listdir('raw')
raw_files.sort()
for raw_file in raw_files:
    file_date = dateparser.parse(raw_file.replace('.txt', ''))
    prev_line = ''
    for line in open('raw/' + raw_file, 'r'):
        if line.startswith('!'):
            trainer, date = parseAuthorDate(prev_line, file_date)
            catch, walk, battle, xp = parseCJBX(line)
            print '%s %6d %6d %6d %9d %s' % (date, catch, walk, battle, xp, trainer)
        prev_line = line
