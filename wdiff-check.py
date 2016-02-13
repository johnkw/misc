#!/bin/python

import subprocess

def do_test(instr, outstr_expect):
    p = subprocess.Popen(['./wdiff.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outstr = ''
    while True:
        (stdout, stderr) = p.communicate(instr)
        p.stdin.close()
        outstr += stdout
        assert stderr == '', stderr
        pollret = p.poll()
        if pollret != None:
            assert pollret == 0
            break
    if outstr != outstr_expect:
        raise Exception('\n'+repr(outstr_expect)+'\n'+repr(outstr)+'\n'+outstr_expect+'\n'+outstr+'\x1b[0m')

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

# ensure: weed out unreadable short u's
do_test('''
- xxx xxx
+ yyy yyy
''',
'\x1b[0m \n  \x1b[7;31mxxx xxx\x1b[7;32myyy yyy\x1b[0m \n')

do_test('''
-                def func(u):
-                    return (
-                        Y
-                    )
+                if True:
+                    def func(u): return Z
+                else:
+                    def func(u):
+                        return (
+                            Y
+                        )
''',
'\x1b[0m \n\x1b[7;32m                 if True:\n                     def func(u): return Z\n                 else:\n    \x1b[0m                 def func(u):\n\x1b[7;32m    \x1b[0m                     return (\n\x1b[7;32m    \x1b[0m                         Y\n\x1b[7;32m    \x1b[0m                     )\n')
