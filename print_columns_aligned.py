#!/bin/python3 -ubb
import itertools, sys, re, textwrap

def plen(s):
    return len(re.sub('\033[\\[\\]]([0-9]{1,2}([;@][0-9]{0,2})*)*[mKP]?', '', s))

def print_columns_aligned(headers, lines, reprint_header=False, dict_from_headers=False, align_to_count=False, return_output=False, print=print):
    expand_headers = sum( ([None]*len(i[1]) if type(i) == tuple else [i] for i in headers), [] )
    maxlens =      [0    if type(i) != dict else i.get('w',0)    for i in expand_headers]
    maxwidth =     [None if type(i) != dict else i.get('m',None) for i in expand_headers]

    def auto_convert(cell):
        if type(cell) == tuple:
            assert len(cell) == 4
            cell = '\x1b[48;2;%03d;%03d;%03dm%s\x1b[0m'%cell
        cell = str(cell) # Auto-convert float etc to str, for convenience.
        return cell

    def get_wraps(gen):
        for line in gen:
            bonuslines = []
            for i, col in enumerate(line):
                if type(col) == tuple:
                    assert len(col) == 4, line
                    text = col[3]
                else: text = col
                if i >= len(maxwidth):
                    raise Exception('\n'+repr(headers)+'\n-- length mismatch -- \n'+repr(line))
                if maxwidth[i] != None and len(text) > maxwidth[i]:
                    wrap = textwrap.wrap(text, maxwidth[i], break_on_hyphens=False)
                    linew = wrap.pop(0)
                    line[i] = linew if (text == col) else (col[:3]+(linew,))
                    for iw, linew in enumerate(wrap):
                        if iw >= len(bonuslines):
                            bonuslines.append(['']*len(headers))
                        bonuslines[iw][i] = linew if (text == col) else (col[:3]+(linew,))
            yield line
            for b in bonuslines:
                yield b

    headers_strs = [i    if type(i) != dict else i['n']          for i in headers]
    headers_lines = [sum((( [i[0]]+['']*(len(i[1])-1) if type(i) == tuple else [i]) for i in headers_strs),[])]
    if any(type(i) == tuple for i in headers_strs):
        headers_lines.append( sum((( list(i[1]) if type(i) == tuple else ['']) for i in headers_strs),[]) )

    headers_strs = sum((( [i[0]+' '+j for j in i[1]] if type(i) == tuple else [i]) for i in headers_strs),[])

    if dict_from_headers:
        lines = [[line.get(h,'') for h in headers_strs] for line in lines]

    # Perform line wrapping with column max-width requirements.
    lines = [line for line in get_wraps(lines)]

    # Now determine column widths from the various text cells.
    for line in itertools.chain(lines,headers_lines):
        if len(line) != len(headers_strs):
            raise Exception('\n'+repr(headers)+'\n-- length mismatch -- \n'+repr(line)+'\n'+repr(headers_lines)+'\n'+repr(lines))
        for i, col in enumerate(line):
            maxlens[i] = max(maxlens[i], plen(auto_convert(col)))

    if align_to_count:
        maxlens = [i + ((-i)%align_to_count) for i in maxlens]

    output = []
    for line in itertools.chain(headers_lines,lines,(headers_lines if reprint_header else [])):
        pline = ''
        for i, col in enumerate(line):
            if type(col) == tuple: text = col[3]
            else: text = auto_convert(col)

            pad = ' '*(maxlens[i]-plen(text))
            if i > 0: pline += ' '
            if isinstance(expand_headers[i], dict) and expand_headers[i].get('a') == 'l':
                cell = text+pad
            else:
                cell = pad+text
            if type(col) == tuple: cell = auto_convert(col[:3]+(cell,))
            pline += cell
        if return_output:
            output.append(pline.rstrip())
        else:
            try: print(pline.rstrip())
            except IOError as e:
                import errno
                if e.errno != errno.EPIPE: raise
    if return_output:
        return output

def print_columns_aligned_auto_from_dict(lines, reprint_header=False, align_to_count=False, return_output=False):
    return print_columns_aligned(list(lines[0].keys()), lines, reprint_header, True, align_to_count, return_output)

def get_table(headers, rows, reprint_header=False, table_attrs=''):
    from htmlstr import htmlstr
    data_headers = []

    header_html = htmlstr('<tr>')
    for i in headers:
        if type(i) == dict: i = i['n']
        if isinstance(i, tuple):
            header_html += htmlstr('<th colspan="%d" style="text-align:center">%s</th>')**(len(i[1]), i[0])
            for dh in i[1]:
                data_headers.append(i[0]+' '+dh)
        else:
            header_html += htmlstr('<th>%s</th>')**i
            data_headers.append(i)
    if any(isinstance(i, tuple) for i in headers):
        header_html += htmlstr('</tr><tr>\n')
        for i in headers:
            if isinstance(i, tuple):
                for dh in i[1]:
                    header_html += htmlstr('<th>%s</th>')**dh
            else:
                header_html += htmlstr('<td></td>')
    header_html += htmlstr('</tr>\n')

    if table_attrs: table_attrs = ' '+table_attrs
    ret = htmlstr('<table'+table_attrs+'>')+header_html
    for row in rows:
        ret += htmlstr('<tr>')
        for enum,i in enumerate(data_headers):
            if isinstance(row,dict):
                cell = row.get(i,'')
            else:
                assert isinstance(row,list), row
                cell = row[enum]
            if type(cell) == tuple:
                if len(cell) == 2:
                    color, cell = cell
                else:
                    assert len(cell) == 4
                    color = '%02x%02x%02x'%tuple(int(i) for i in cell[0:3])
                    cell = cell[3]
            else: color = None
            ret += htmlstr('<td')+(htmlstr(' style="background-color:#%s"')**color if color else htmlstr(''))+htmlstr('>%s</td>')**str(cell)
        ret += htmlstr('</tr>\n')

    if reprint_header:
        ret += header_html

    ret += htmlstr('</table>\n')
    return ret

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('DELIMETER')
    parser.add_argument('ALIGN_TO_COUNT', type=int, default=0, nargs='?')
    parser.add_argument('ALIGN', type=str, default='r', choices=('l','r'), nargs='?')
    args = parser.parse_args()
    lines = [i.split(args.DELIMETER) for i in sys.stdin.readlines()]
    print_columns_aligned([{'n':i,'a':args.ALIGN} for i in lines[0]], lines[1:], align_to_count=args.ALIGN_TO_COUNT)
