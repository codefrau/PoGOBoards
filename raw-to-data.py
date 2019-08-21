#!/usr/bin/env python

import os
import sys
import re
import dateparser

reAuthorDate = re.compile('^(.*)([A-Z][a-z]+day at [1-9][0-9]?:[0-9][0-9] (AM|PM)|[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9])$')

def parseAuthorDate(line, file_date):
    match = reAuthorDate.match(line)
    author_str = match.group(1)
    date_str = match.group(2)
    if author_str.endswith('Last '):
        author_str = author_str[:-5]
    date = dateparser.parse(date_str, settings={'RELATIVE_BASE': file_date})
    return (author_str, date)


reCJBX = re.compile('^![cjbx]{4} +([0-9,]+) +([0-9,]+)[.0-9,]* +([0-9,]+) +([0-9,]+)(\(edited\))?$')

def parseCJBX(line):
    match = reCJBX.match(line)
    catch  = int(match.group(1).replace(',', ''))
    walk   = int(match.group(2).replace(',', ''))
    battle = int(match.group(3).replace(',', ''))
    xp     = int(match.group(4).replace(',', ''))
    return (catch, walk, battle, xp)


raw_files = os.listdir('raw')
raw_files.sort()
prev_line = ''
prev_date = None
for raw_file in raw_files:
    sys.stderr.write("raw/%s\n" % raw_file)
    file_date = dateparser.parse(raw_file.replace('.txt', ''))
    for line in open('raw/' + raw_file, 'r'):
        line = line.strip()
        if line.startswith('!'):
            try:
                trainer, date = parseAuthorDate(prev_line, file_date)
                catch, walk, battle, xp = parseCJBX(line)
                if prev_date:
                    delta = (date - prev_date).total_seconds()
                    if delta < 0:
                        raise Exception("Dates not monotonous: %s seconds delta" % delta)
                    if delta == 0 and prev_trainer == trainer:
                        raise Exception("duplicate line")
                print '%s %6d %6d %6d %9d %s' % (date.isoformat(), catch, walk, battle, xp, trainer)
                prev_date = date
                prev_trainer = trainer
            except Exception as e:
                sys.stderr.write('ERROR: malformed submission\n***** %s\n***** %s\n' % (prev_line, line))
                raise e
                sys.exit(1);
        prev_line = line
