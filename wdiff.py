#!/usr/bin/python -ubb

# Script to add word-based colors to `diff -u` output.
# Use: `diff -u a b | wdiff.py` or `wdiff.py < patch.txt`.

import difflib, itertools, sys

curcol = -1
def colored_print(msg, col):
    global curcol
    if msg == b'':
        return

    if col != curcol:
        curcol = col
        if col == 0:
            sys.stdout.write('\x1b[0m')
        else:
            sys.stdout.write('\x1b[7;3%dm' % col)

    if msg == b'\n' and curcol:
        msg = b' \n' # just to have something visible
    (sys.stdout.buffer if 'buffer' in dir(sys.stdout) else sys.stdout).write(msg)


def canonicalize_doubles_blanks(diffs):
    # canonicalize double-X's and blank -/+'s
    i = 0
    while i < len(diffs)-2:
        if (diffs[i][0] == diffs[i+1][0]):
            diffs[i][1] += diffs[i+1][1]
            del diffs[i+1]
        elif (diffs[i][0] in ('d','a')) and (diffs[i][1] == b''):
            del diffs[i]
        elif (diffs[i][0] == 'a') and (diffs[i+1][0] == 'd'):
            t = diffs[i]
            diffs[i] = diffs[i+1]
            diffs[i+1] = t
        else:
            i += 1

def split_words(instr):
    breaks = b'|\n \t\"\';$%,<>@_:.[]()\'/!{}*-^+'
    out = []
    current_chunk = b''
    for char in instr:
        char = bytes([char]) # Hack due to missing PEP 467.
        if char in breaks:
            if current_chunk:
                out.append(current_chunk)
            current_chunk = b''
            out.append(char)
        else:
            current_chunk += char
    if current_chunk:
        out.append(current_chunk)
    return out

def dodifflib(old, new):
    diffs = []
    oldsplit = split_words(old)
    newsplit = split_words(new)
    #print oldsplit, '\n\n', newsplit
    for oc in difflib.SequenceMatcher(None, oldsplit, newsplit, autojunk=False).get_opcodes():
        if (oc[0] == 'equal'):
            diffs.append( [ 'u', b''.join(oldsplit[oc[1]:oc[2]]) ] )
        elif oc[0] == 'replace':
            diffs.append( [ 'd', b''.join(oldsplit[oc[1]:oc[2]]) ] )
            diffs.append( [ 'a', b''.join(newsplit[oc[3]:oc[4]]) ] )
            assert diffs[-1] != b'' or diffs[-2] != b''
        elif oc[0] == 'delete':
            diffs.append( [ 'd', b''.join(oldsplit[oc[1]:oc[2]]) ] )
        elif oc[0] == 'insert':
            diffs.append( [ 'a', b''.join(newsplit[oc[3]:oc[4]]) ] )
        else:
            raise
    return diffs

def printdiffs(diffs):
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
               and ((b'\n' not in diffs[i][1] and (len(diffs[i][1]) <= 2)) or all(bytes([i]) in [b' ',b'\t',b'\n'] for i in diffs[i][1]))
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
                all(j == 32 for j in diffs[i][1])
            ):
                oldlast = diffs[i-1][1]
                diffs[i-1][1] = diffs[i-1][1].rstrip(b' ')
                diffs[i+1][1] = (b' '*(len(oldlast)-len(diffs[i-1][1])))+diffs[i+1][1]

            def ending_spaces_count(s):
                for i, c in enumerate(reversed(s)):
                    if bytes([c]) != b' ':
                        return i
                return len(s)

            # consolidate added spaces to the beginning of an add/remove
            esci = ending_spaces_count(diffs[i][1])
            if (
                esci and (diffs[i-1][0] == 'u') and (diffs[i][0] in ('a','d')) and (diffs[i+1][0] == 'u') and
                esci == ending_spaces_count(diffs[i-1][1])
            ):
                diffs[i-1][1] =            diffs[i-1][1][:-esci]
                diffs[i  ][1] = b' '*esci + diffs[i  ][1][:-esci]
                diffs[i+1][1] = b' '*esci + diffs[i+1][1]

            # move linebreak to beginning of an add/remove
            lbspot = diffs[i][1].find(b'\n')
            if (
                lbspot != -1 and
                (diffs[i-1][0] == 'u') and (diffs[i][0] in ('a','d')) and (diffs[i+1][0] == 'u') and
                diffs[i][1][:lbspot] == diffs[i+1][1][:lbspot]
            ):
                diffs[i-1][1] += diffs[i+1][1][:lbspot]
                diffs[i  ][1] =  diffs[i  ][1][lbspot:]+diffs[i+1][1][:lbspot]
                diffs[i+1][1] =  diffs[i+1][1][lbspot:]

            # move linebreak to beginning of an add/remove - backwards
            lbspot = diffs[i][1].rfind(b'\n')
            if (
                lbspot > 0 and
                (diffs[i-1][0] == 'u') and (diffs[i][0] in ('a','d')) and (diffs[i+1][0] == 'u') and
                (diffs[i][1][lbspot:] == diffs[i-1][1][(lbspot-len(diffs[i][1])):])
            ):
                diffs[i-1][1] =  diffs[i-1][1][:(lbspot-len(diffs[i][1]))]   # truncate
                diffs[i+1][1] =  diffs[i][1][lbspot:] + diffs[i+1][1]        # prepend
                diffs[i  ][1] =  diffs[i][1][lbspot:] + diffs[i][1][:lbspot] # prepend/truncate


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
    (adds, dels) = (b'', b'')
    for sd in diffs:
        assert len(sd) == 2,(sd, diffs)
        assert isinstance(sd[1], bytes),(sd, diffs)
        if sd[0] == 'u':
            colored_print(dels, 1)
            colored_print(adds, 2)
            (adds, dels) = (b'', b'')
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
        # The "easy" mode can be dramatically faster when diffing a file with many lines, where a bit changed on each line.
        if len(old) == len(new) and len(sys.argv) == 2 and sys.argv[1] == 'easy':
            while old:
                printdiffs(dodifflib(old.pop(0), new.pop(0)))
            return

        if old or new:
            while len(old) > 2 and len(new) > 2:
                searchlen = min(len(old), len(new))-1
                for oldi, newi in itertools.product(range(searchlen), range(searchlen)):
                    linediffs = dodifflib(old[oldi], new[newi])
                    lu = b''
                    lc = b''
                    for i in linediffs:
                        if i[0] in ('a','d'):
                            lc += i[1]
                        elif i[0] == 'u':
                            lu += i[1]
                        else: assert 0
                    if not lc.strip() or len(lc+lu)/len(lc) > 5:
                        printdiffs(dodifflib(b''.join(old[:oldi+1]), b''.join(new[:newi+1])))
                        del old[:oldi+1]
                        del new[:newi+1]
                        break
                else: break
            printdiffs(dodifflib(b''.join(old), b''.join(new)))

    alines, dlines = [], []
    for line in (sys.stdin.buffer if 'buffer' in dir(sys.stdin) else sys.stdin).read().splitlines():
        line = line.replace(b'\r', b'')+b'\n'
        if   line[0:1] == b'+':
            alines.append(b' '+line[1:])
        elif line[0:1] == b'-':
            dlines.append(b' '+line[1:])
        else:
            if len(sys.argv) == 2 and sys.argv[1] == 'hard': # This can dramatically slow things down so make optional.
                alines.append(b' '+line[1:])
                dlines.append(b' '+line[1:])
            else:
                showdiffs(dlines, alines)
                alines, dlines = [], []
                colored_print(line, 0)

    if alines != [] or dlines != []:
        if dlines:
            assert dlines[-1][-1:] == b'\n'
            dlines[-1] = dlines[-1][:-1]
        if alines:
            assert alines[-1][-1:] == b'\n'
            alines[-1] = alines[-1][:-1]
        showdiffs(dlines, alines)
        colored_print(b'\n', 0) # always end wdiff output with a 0-color linefeed
