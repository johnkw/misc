#!/bin/python -ubb

import write_with_rename, time, lzma

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
            print(filename,'success' if (lzma.open if compress else open)(filename,'r'+('b' if binary else 't')).read() == msg else 'error')
