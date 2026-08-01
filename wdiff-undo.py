#!/usr/bin/python -ttu

import itertools, sys
old, new = '', ''
lastcol = 0

def print_diff():
    global old, new
    if old:
        for oldl in old.split('\n'):
            if oldl != '':
                assert oldl[0] == ' '
                sys.stdout.write('-'+oldl[1:]+'\n')
    if new:
        for newl in new.split('\n'):
            if newl != '':
                assert newl[0] == ' '
                sys.stdout.write('+'+newl[1:]+'\n')
    old, new = '', ''

lines = sys.stdin.readlines()
while lines:
    line = lines.pop(0)

    seg = line.split("\x1b[")
    thisold = ( (seg[0] if lastcol in (0,1) else '') + (''.join(i[i.find('m')+1:] for i in seg[1:] if i[:5] == '7;31m' or i[:2] == '0m')))
    thisnew = ( (seg[0] if lastcol in (0,2) else '') + (''.join(i[i.find('m')+1:] for i in seg[1:] if i[:5] == '7;32m' or i[:2] == '0m')))
    if thisold.replace('\n','') == thisnew.replace('\n',''):
        print_diff()
        if '\n' in thisnew:
            sys.stdout.write(thisnew)
        else:
            assert '\n' in thisold
            sys.stdout.write(thisold)
    else:
        old += thisold
        new += thisnew
    if len(seg) > 1:
        lastcol = int(seg[-1][seg[-1].find('m')-1])

print_diff()
