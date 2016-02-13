#!/usr/bin/python

# Script to add word-based colors to `diff -u` output.
# Use: `diff -u a b | wdiff.py` or `wdiff.py < patch.txt`.

import difflib, re, sys

curcol = -1
def colored_print(msg, col):
    global curcol
    if msg == '':
        return

    if col != curcol:
        curcol = col
        if col == 0:
            sys.stdout.write("\x1b[0m")
        else:
            sys.stdout.write("\x1b[7;3%dm" % col)

    if msg == "\n":
        msg = " \n" # just to have something visible
    sys.stdout.write(msg)


def canonicalize_doubles_blanks(diffs):
    # canonicalize double-X's and blank -/+'s
    i = 0
    while i < len(diffs)-2:
        if (diffs[i][0] == diffs[i+1][0]):
            diffs[i][1] += diffs[i+1][1]
            del diffs[i+1]
        elif (diffs[i][0] in ('d','a')) and (diffs[i][1] == ''):
            del diffs[i]
        elif (diffs[i][0] == 'a') and (diffs[i+1][0] == 'd'):
            t = diffs[i]
            diffs[i] = diffs[i+1]
            diffs[i+1] = t
        else:
            i += 1

def diff(old, new, inregs):
    regs = list(inregs)
    reg = regs.pop(0)
    if regs:
        regs[0] += reg

    diffs = []
    oldsplit = [i for i in re.split('(['+reg+'])', old) if i]
    newsplit = [i for i in re.split('(['+reg+'])', new) if i]
    #print oldsplit, newsplit
    for oc in difflib.SequenceMatcher(None, oldsplit, newsplit).get_opcodes():
        #print oc
        if (oc[0] == 'equal'):
            diffs.append( [ 'u', ''.join(oldsplit[oc[1]:oc[2]]) ] )
        elif oc[0] == 'replace':
            diffs.append( [ 'd', ''.join(oldsplit[oc[1]:oc[2]]) ] )
            diffs.append( [ 'a', ''.join(newsplit[oc[3]:oc[4]]) ] )
            assert diffs[-1] != '' or diffs[-2] != ''
        elif oc[0] == 'delete':
            diffs.append( [ 'd', ''.join(oldsplit[oc[1]:oc[2]]) ] )
        elif oc[0] == 'insert':
            diffs.append( [ 'a', ''.join(newsplit[oc[3]:oc[4]]) ] )
        else:
            raise

    while True:
        size = len(diffs)

        canonicalize_doubles_blanks(diffs)

        # weed out unreadable short u's
        i = 1
        while i < len(diffs)-1:
            if (
                   (diffs[i][0] == 'u')
               and (('\n' not in diffs[i][1] and (len(diffs[i][1]) <= 2)) or re.match('\s+', diffs[i][1]))
            ):
                if diffs[i-1][0] != diffs[i+1][0]:
                    diffs[i-1][1] += diffs[i][1]
                    diffs[i+1][1] =  diffs[i][1] + diffs[i+1][1]
                    del diffs[i]
                    break
                elif (i > 1) and (diffs[i-1][0] == diffs[i+1][0] and diffs[i-2][0] in ('a','d')) and (diffs[i-1][0] != diffs[i-2][0] ):
                    diffs[i-2][1] += diffs[i][1]
                    diffs[i-1][1] += diffs[i][1]
                    del diffs[i]
                    break
                elif (i + 2 < len(diffs)) and (diffs[i+1][0] != diffs[i+2][0] and diffs[i+2][0] in ('a','d')):
                    diffs[i+1][1] = diffs[i][1] + diffs[i+1][1]
                    diffs[i+2][1] = diffs[i][1] + diffs[i+2][1]
                    del diffs[i]
                    break
                else:
                    i += 1
            else:
                i += 1

        if size == len(diffs):
            break

    for i in range(1, len(diffs)-1):
        # move spaces to beginning of line
        if (
            (diffs[i-1][0] == 'u') and (diffs[i][0] == 'a') and (diffs[i+1][0] == 'u') and
            all(j == ' ' for j in diffs[i][1])
        ):
            rx = re.match('^([\s\S]*?)('+diffs[i][1]+'\s+)$', diffs[i-1][1])
            if rx:
                assert len(rx.groups()) == 2
                diffs[i-1][1] = rx.groups()[0]
                diffs[i+1][1] = rx.groups()[1]+diffs[i+1][1]



    # output
    (adds, dels) = ('', '')
    for sd in diffs:
        assert len(sd) == 2,(sd, diffs)
        assert isinstance(sd[1], str),(sd, diffs)
        if sd[0] == 'u':
            if regs:
                diff(dels, adds, regs)
            else:
                colored_print(dels, 1)
                colored_print(adds, 2)
            (adds, dels) = ('', '')
            colored_print(sd[1], 0)
        elif sd[0] == 'd':
            dels += sd[1]
        elif sd[0] == 'a':
            adds += sd[1]
        else:
            raise

    if regs:
        diff(dels, adds, regs)
    else:
        colored_print(dels, 1)
        colored_print(adds, 2)


if __name__ == '__main__':
    def showdiffs(old, new):
        if old or new:
            diff(old, new, ['|\n\r \t\"\';\$\%', ',<>\@_:\.\[\]()\'\\\/!{}'])

    (alines, dlines) = ('', '')
    for line in sys.stdin:
        line.replace('\t', '    ')
        if   line[0] == '+':
            alines += ' '+line[1:]
        elif line[0] == '-':
            dlines += ' '+line[1:]
        else:
            showdiffs(dlines, alines)
            (alines, dlines) = ('', '')
            colored_print(line, 0)

    showdiffs(dlines, alines)
    #colored_print(' ', 0)
