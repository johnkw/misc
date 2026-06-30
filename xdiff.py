#!/bin/python -ubb

import os, select, shlex, subprocess, sys, lzma

def stream_proc(args, streams_to_pipe_inputs):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, pass_fds=[i[1] for i in streams_to_pipe_inputs.values()])
    linebuf = b''
    while True:
        reads,writes,errors = select.select(
            (proc.stdout.fileno(),proc.stderr.fileno()),
            streams_to_pipe_inputs.keys(),
            (proc.stdout,proc.stderr)
        )
        if not(reads or writes or errors):
            assert proc.poll()
            return
        for write in writes:
            assert streams_to_pipe_inputs
            data = streams_to_pipe_inputs[write][0].read(10000)
            if not data:
                os.close(write)
                streams_to_pipe_inputs.pop(write)
                continue
            os.write(write, data)

        assert errors == []
        for read in reads:
            if read == proc.stderr.fileno():
                sys.stderr.buffer.write(os.read(read,10000))
            else:
                newbuf = os.read(read,1000)
                if len(newbuf) == 0 and proc.poll():
                    assert linebuf == b'', 'un-terminated data? '+repr(linebuf)
                    return
                linebuf += newbuf
                del newbuf
                while b'\n' in linebuf:
                    line, linebuf = linebuf.split(b'\n', 1)
                    if line == b'':
                        continue
                    if not streams_to_pipe_inputs and line.startswith(b'Binary files '):
                        assert line.endswith(b' differ')
                        file_names = shlex.split(line.decode('utf-8'))
                        file1 = os.pipe()
                        file2 = os.pipe()
                        stream_proc(
                            ['diff']+sys.argv[1:-2]+['--label',file_names[2]+' --- piped through xz','--label',file_names[4]+' --- piped through xz','/proc/self/fd/%d'%file1[0], '/proc/self/fd/%d'%file2[0]],
                            {
                                file1[1]: (lzma.open(file_names[2],'r'), file1[0]),
                                file2[1]: (lzma.open(file_names[4],'r'), file2[0]),
                            }
                        )
                    else:
                        sys.stdout.buffer.write(line+b'\n')
        
stream_proc(['diff']+sys.argv[1:], {})
