#!/bin/python -ubb

import cmdargs, ensure, os

cmdargs.parse('DIRECTORY')
os.chdir(cmdargs['DIRECTORY'])

matches = []
paths = sorted(sum(([os.path.join(i[0],f) for f in i[2]] for i in os.walk('.')),[]))

def getfile(path):
    while os.path.islink(path):
        path = os.path.join(os.path.dirname(path),os.readlink(path))
    path = os.path.abspath(path)
    return open(path,'rb').read()

for pb in paths:
 for pa in paths:
    if (
        (pb <= pa)
     or (not os.path.isfile(pa) or os.path.islink(pa))
     or os.path.samefile(pa, pb)
     or (os.path.getsize(pa) != os.path.getsize(pb))
     or (os.path.getsize(pb) == 0)
    ): continue
    if getfile(pa) == getfile(pb):
        print('match %10d %-100s <= %-100s'%(os.path.getsize(pb),pa,pb))
        matches.append([pa,pb])
        break

if matches and ensure.choice('turn matches into links?',['yes','']) == 'yes':
    for pa,pb in matches:
        os.unlink(pb)
        os.symlink(os.path.relpath(pa, os.path.dirname(pb)), pb)
