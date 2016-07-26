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

def diff(old, new, reg):
    diffs = []
    oldsplit = [i for i in re.split('(['+reg+'])', old) if i]
    newsplit = [i for i in re.split('(['+reg+'])', new) if i]
    #print oldsplit, '\n\n', newsplit
    for oc in difflib.SequenceMatcher(None, oldsplit, newsplit, autojunk=False).get_opcodes():
        #print "oc:  ", oc
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
        #print "dif: ", diffs

    while True:
        size = len(diffs)
        #print '\n\n', diffs

        canonicalize_doubles_blanks(diffs)
        #print '\n\n', diffs

        # weed out unreadable short u's
        i = 1
        while i < len(diffs)-1:
            if (
                   (diffs[i][0] == 'u')
               and (('\n' not in diffs[i][1] and (len(diffs[i][1]) <= 2)) or re.match('\s+$', diffs[i][1]))
            ):
                if diffs[i-1][0] != diffs[i+1][0]:
                    #print 'a'*30, i, (diffs[i][0] == 'u'), diffs[i][1]
                    diffs[i-1][1] += diffs[i][1]
                    diffs[i+1][1] =  diffs[i][1] + diffs[i+1][1]
                    del diffs[i]
                    break
                elif (i > 1) and (diffs[i-1][0] == diffs[i+1][0] and diffs[i-2][0] in ('a','d')) and (diffs[i-1][0] != diffs[i-2][0] ):
                    #print 'b'*30, i, diffs[i]
                    diffs[i-2][1] += diffs[i][1]
                    diffs[i-1][1] += diffs[i][1]
                    del diffs[i]
                    break
                elif (i + 2 < len(diffs)) and (diffs[i+1][0] != diffs[i+2][0] and diffs[i+2][0] in ('a','d')):
                    #print 'c'*30, i, diffs[i]
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

    while True:
        for i in range(1, len(diffs)-1):
            # move spaces to beginning of line
            if (
                (diffs[i-1][0] == 'u') and (diffs[i][0] in ('a','d')) and (diffs[i+1][0] == 'u') and
                all(j == ' ' for j in diffs[i][1])
            ):
                rx = re.match('^([\s\S]*?)('+diffs[i][1]+'\s+)$', diffs[i-1][1])
                if rx:
                    assert len(rx.groups()) == 2
                    diffs[i-1][1] = rx.groups()[0]
                    diffs[i+1][1] = rx.groups()[1]+diffs[i+1][1]

            def ending_spaces_count(s):
                for i, c in enumerate(reversed(s)):
                    if c != ' ':
                        return i
                return len(s)


            # consolidate added spaces to the beginning of an add/remove
            esci = ending_spaces_count(diffs[i][1])
            if (
                esci and (diffs[i-1][0] == 'u') and (diffs[i][0] in ('a','d')) and (diffs[i+1][0] == 'u') and
                esci == ending_spaces_count(diffs[i-1][1])
            ):
                diffs[i-1][1] =            diffs[i-1][1][:-esci]
                diffs[i  ][1] = ' '*esci + diffs[i  ][1][:-esci]
                diffs[i+1][1] = ' '*esci + diffs[i+1][1]

            # move linebreak to beginning of an add/remove
            lbspot = diffs[i][1].find('\n')
            if (
                (diffs[i-1][0] == 'u') and (diffs[i][0] in ('a','d')) and (diffs[i+1][0] == 'u') and
                lbspot != -1 and
                diffs[i][1][:lbspot] == diffs[i+1][1][:lbspot]
            ):
                diffs[i-1][1] += diffs[i+1][1][:lbspot]
                diffs[i  ][1] =  diffs[i  ][1][lbspot:]+diffs[i+1][1][:lbspot]
                diffs[i+1][1] =  diffs[i+1][1][lbspot:]

            # Consolidate remove/add, with large chunk of end of remove matching beginning of the add. Perhaps a later version of difflib (or some tweak to our use of it) would fix this?
            if (diffs[i][0] == 'd') and (diffs[i+1][0] == 'a'):
                try:
                    consolidate_len = max( j for j in range(min(len(diffs[i+1][1]), len(diffs[i][1]))) if diffs[i+1][1][:j] == diffs[i][1][-j:] )
                except ValueError: pass
                else:
                    diffs[i+1][1] = diffs[i+1][1][consolidate_len:]
                    diffs.insert(i+1, ['u', diffs[i][1][-consolidate_len:] ])
                    diffs[i][1] = diffs[i][1][:-consolidate_len]
                    break
        else: break


    # output
    (adds, dels) = ('', '')
    for sd in diffs:
        assert len(sd) == 2,(sd, diffs)
        assert isinstance(sd[1], str),(sd, diffs)
        if sd[0] == 'u':
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

    colored_print(dels, 1)
    colored_print(adds, 2)


if __name__ == '__main__':
    def showdiffs(old, new):
        if old or new:
            diff(old, new, '|\n\r \t\"\';\$\%,<>\@_:\.\[\]()\'\\\/!{}')

    (alines, dlines) = ('', '')
    for line in sys.stdin:
        line.replace('\t', '    ')
        if   line[0] == '+':
            alines += ' '+line[1:]
        elif line[0] == '-':
            dlines += ' '+line[1:]
        elif line[0] == ' ':
            alines += line
            dlines += line
        else:
            showdiffs(dlines, alines)
            (alines, dlines) = ('', '')
            colored_print(line, 0)

    showdiffs(dlines, alines)
    #colored_print(' ', 0)
