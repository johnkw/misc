#!/bin/python -ubb

import csv, write_with_rename, time, lzma, os

for compress in [False,True]:
    filename = 'write_with_rename-test-%d.tsv'%compress
    (lzma.open if compress else open)(filename,'wt').write('a\tb\n1\t2\n')
    write_with_rename.change_csv(filename, lambda rows:({'a':int(row['a'])+10,'b':int(row['b'])+10} for row in rows), compress=compress)
    assert (_:=list(csv.DictReader((lzma.open if compress else open)(filename,'rt'),dialect=csv.excel_tab))) == [{'a':'11','b':'12'}], _
    print('checked '+filename)
    os.unlink(filename)

for compress in [False,True]:
    for binary in [False,True]:
        for call_style in [0,1]:
            filename = 'write_with_rename-test-%d-%d-%d'%(binary,compress,call_style)
            msg = ''.join(filename+' '+str(i)+' '+str(time.time())+'\n' for i in range(10000))
            if binary:
                msg = msg.encode('utf-8')
            if call_style == 0:
                with write_with_rename.WriteWithRename(filename,binary=binary, compress=compress) as f:
                    f.write(msg)
            else:
                write_with_rename.write(filename, msg, compress=compress)
            assert (lzma.open if compress else open)(filename,'r'+('b' if binary else 't')).read() == msg, filename
            print('checked '+filename)
            os.unlink(filename)
