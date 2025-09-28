#!/bin/python -ttu

import cmdargs, difflib, bs4

cmdargs.parse('old','new')
#datas = {k:[i.strip() for i in open(cmdargs[k]).readlines()] for k in ('old','new')}
datas = {k:[str(i) for i in bs4.BeautifulSoup(open(cmdargs[k]),'html.parser').find_all('div',recursive=False)] for k in ('old','new')}

for _,o,n in sorted((-difflib.SequenceMatcher(None, o, n, autojunk=False).ratio(),o,n) for o in datas['old'] for n in datas['new']):
    if (o in datas['old']) and (n in datas['new']):
        if o != n:
            print('-'+o.replace('\n','\n-')+'\n+'+n.replace('\n','\n+')+'\n')
        datas['old'].remove(o)
        datas['new'].remove(n)
for i in datas['old']: print('-'+i.replace('\n','\n-'))
for i in datas['new']: print('+'+i.replace('\n','\n+'))
