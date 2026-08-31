#!/bin/python -ubb

import cmdargs, ensure, os, shutil

cmdargs.parse('DIRECTORY')
os.chdir(cmdargs['DIRECTORY'])

paths = list(os.walk('.'))
assert paths[0][2] == []
paths.pop(0)
paths = sum(([os.path.join(i[0],f) for f in i[2]] for i in paths),[])
matches = []

for pa in paths:
    if os.path.islink(pa):
        pb = os.path.join(os.path.dirname(pa),os.readlink(pa))
        print('match %10d %-60s  <=  %-60s'%(os.path.getsize(pb),pb,pa))
        matches.append([pa,pb])

if matches and ensure.choice('turn links into files?',['yes','']) == 'yes':
    for pa,pb in matches:
        os.unlink(pa)
        shutil.copyfile(pb, pa)
