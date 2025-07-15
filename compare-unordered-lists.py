#!/bin/python -ttu

import cmdargs, difflib

cmdargs.parse('old','new')
datas = {k:[i.strip() for i in open(cmdargs[k]).readlines()] for k in ('old','new')}

for _,o,n in sorted((-difflib.SequenceMatcher(None, o, n).ratio(),o,n) for o in datas['old'] for n in datas['new']):
    if (o in datas['old']) and (n in datas['new']):
        if o != n:
            print('-'+o+'\n+'+n+'\n')
        datas['old'].remove(o)
        datas['new'].remove(n)
for i in datas['old']: print('-'+i)
for i in datas['new']: print('+'+i)
