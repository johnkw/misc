#!/bin/python

import subprocess

def do_test(instr, outstr_expect):
    p = subprocess.Popen(['./wdiff.pl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outstr = ''
    while True:
        (stdout, stderr) = p.communicate(instr)
        p.stdin.close()
        outstr += stdout
        assert stderr == ''
        pollret = p.poll()
        if pollret != None:
            assert pollret == 0
            break
    if outstr != outstr_expect:
        raise Exception('\n'+repr(outstr)+'\n'+repr(outstr_expect))

do_test('''
- a_a_a
+ _''', '\x1b[0m \n  \x1b[7;31ma\x1b[0m_\x1b[7;31ma_a\n')

do_test('''
- a.a.a
+ .''', '\x1b[0m \n  \x1b[7;31ma\x1b[0m.\x1b[7;31ma.a\n')

do_test('''
- F.F_F
+ _''',
'\x1b[0m \n  \x1b[7;31mF.F\x1b[0m_\x1b[7;31mF\n')
