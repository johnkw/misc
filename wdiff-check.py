#!/bin/python -ubb

import subprocess, cmdargs
cmdargs.parse(('--script', {'default':'./wdiff.py'}))

def do_cmd(cmd, instr):
    #print 'calling %s with %s' % (cmd, repr(instr))
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outstr = ''
    while True:
        (stdout, stderr) = p.communicate(instr.encode('utf8'))
        p.stdin.close()
        outstr += stdout.decode('utf8')
        if stderr:
            print('stderr:\n'+stderr.decode('utf8'))
            exit(1)
        pollret = p.poll()
        if pollret != None:
            assert pollret == 0
            break
    #print 'got %s' % (repr(outstr))
    return outstr

def do_test(instr, outstr_expect):
    outstr = do_cmd([cmdargs['script']], instr)
    if outstr != outstr_expect:
        raise Exception('\n'+instr+'\n'+repr(outstr_expect)+'\n'+repr(outstr)+'\n'+outstr_expect+'\n'+outstr+'\x1b[0m')
    outstr_undo = do_cmd(['./wdiff-undo.py'], outstr)
    if outstr_undo != instr:
        raise Exception('\n'+repr(instr)+'\n'+repr(outstr_undo)+'\n'+repr(outstr)+'\n'+instr+'\n'+outstr_undo+'\x1b[0m')

do_test('''-x   h b
-y   w  z
+x h    b
+y w     z
''', '\x1b[0m x\x1b[7;31m  \x1b[0m h\x1b[7;32m   \x1b[0m b\n y\x1b[7;31m  \x1b[0m w\x1b[7;32m   \x1b[0m  z\n')


do_test(''' .
 </p>
 
 <p>
-<b>Ingredients:</b><br>
+<em>Ingredients:</em><br>
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
 .
''',
'\x1b[0m .\n </p>\n \n <p>\n <\x1b[7;31mb\x1b[7;32mem\x1b[0m>Ingredients:</\x1b[7;31mb\x1b[7;32mem\x1b[0m><br>\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n .\n')

do_test('''  2019-09-12    32      Qjm90lf-B2TpVE-3KJ15N Qjm90lf-B2TpVE-3KJ15N
+ 2019-09-13    18      kp3jQW-NyWNH7-mZz-4h kp3jQW-NyWNH7-mZz-4h
  2019-09-13    18      kp3jQW-yWOFyW-2953040 kp3jQW-yWOFyW-2953040
+ 2019-09-13    18      kp3jQW-VsnIev-0820224 kp3jQW-VsnIev-0820224
  2019-09-13    18      kp3jQW-kYn3bZ-1031402 kp3jQW-kYn3bZ-1031402
  2019-09-13    18      kp3jQW-h6X67Y-8480211 kp3jQW-h6X67Y-8480211
''',
'''\x1b[0m  2019-09-12    32      Qjm90lf-B2TpVE-3KJ15N Qjm90lf-B2TpVE-3KJ15N\n\x1b[7;32m  2019-09-13    18      kp3jQW-NyWNH7-mZz-4h kp3jQW-NyWNH7-mZz-4h\n\x1b[0m  2019-09-13    18      kp3jQW-yWOFyW-2953040 kp3jQW-yWOFyW-2953040\n\x1b[7;32m  2019-09-13    18      kp3jQW-VsnIev-0820224 kp3jQW-VsnIev-0820224\n\x1b[0m  2019-09-13    18      kp3jQW-kYn3bZ-1031402 kp3jQW-kYn3bZ-1031402\n  2019-09-13    18      kp3jQW-h6X67Y-8480211 kp3jQW-h6X67Y-8480211\n''')

do_test('''  2019-09-12    32      Qjm90lf-B2TpVE-3KJ15N Qjm90lf-B2TpVE-3KJ15N
  2019-09-13    18      kp3jQW-yWOFyW-2953040 kp3jQW-yWOFyW-2953040
+ 2019-09-13    18      kp3jQW-NyWNH7-mZz-4h kp3jQW-NyWNH7-mZz-4h
+ 2019-09-13    18      kp3jQW-VsnIev-0820224 kp3jQW-VsnIev-0820224
  2019-09-13    18      kp3jQW-kYn3bZ-1031402 kp3jQW-kYn3bZ-1031402
  2019-09-13    18      kp3jQW-h6X67Y-8480211 kp3jQW-h6X67Y-8480211
''',
'\x1b[0m  2019-09-12    32      Qjm90lf-B2TpVE-3KJ15N Qjm90lf-B2TpVE-3KJ15N\n  2019-09-13    18      kp3jQW-yWOFyW-2953040 kp3jQW-yWOFyW-2953040\n\x1b[7;32m  2019-09-13    18      kp3jQW-NyWNH7-mZz-4h kp3jQW-NyWNH7-mZz-4h\n  2019-09-13    18      kp3jQW-VsnIev-0820224 kp3jQW-VsnIev-0820224\n\x1b[0m  2019-09-13    18      kp3jQW-kYn3bZ-1031402 kp3jQW-kYn3bZ-1031402\n  2019-09-13    18      kp3jQW-h6X67Y-8480211 kp3jQW-h6X67Y-8480211\n')

do_test('- a\n',
'\x1b[7;31m  a\x1b[0m\n')

do_test('''- a_a_a
+ _
''', '\x1b[0m  \x1b[7;31ma\x1b[0m_\x1b[7;31ma_a\x1b[0m\n')

do_test('''- a.a.a
+ .
''', '\x1b[0m  \x1b[7;31ma\x1b[0m.\x1b[7;31ma.a\x1b[0m\n')

do_test('''- F.F_F
+ _
''',
'\x1b[0m  \x1b[7;31mF.F\x1b[0m_\x1b[7;31mF\x1b[0m\n')

# ensure: weed out unreadable short u's
do_test('''- xxx xxx
+ yyy yyy
''',
'\x1b[0m  \x1b[7;31mxxx xxx\x1b[7;32myyy yyy\x1b[0m\n')

do_test('''-                def func(u):
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
'\x1b[7;32m                 if True:\n                     def func(u): return Z\n                 else:\n    \x1b[0m                 def func(u):\n\x1b[7;32m    \x1b[0m                     return (\n\x1b[7;32m    \x1b[0m                         Y\n\x1b[7;32m    \x1b[0m                     )\n')

do_test('''-    def __contains__(self, bar):
-        return bar in self.__items
+    def __contains__(self, foo):
+        assert isinstance(foo, int)
+        return foo in self.__items
''',
'\x1b[0m     def __contains__(self, \x1b[7;31mbar\x1b[7;32mfoo\x1b[0m):\x1b[7;32m\n         assert isinstance(foo, int)\x1b[0m\n         return \x1b[7;31mbar\x1b[7;32mfoo\x1b[0m in self.__items\n')

do_test('''-        if not(
-            (time.time() < go_time) # Check the time for that thing.
-        and (g_got_things > need_thing_count) # Check those things.
-        ):
+        can_do_checks = (
+            time.time() < go_time, # Check the time for that thing.
+            g_got_things > need_thing_count, # Check those things.
+        )
''',
'\x1b[0m         \x1b[7;31mif not\x1b[7;32mcan_do_checks = \x1b[0m(\n             \x1b[7;31m(\x1b[0mtime.time() < go_time\x1b[7;31m)\x1b[7;32m,\x1b[0m # Check the time for that thing.\n         \x1b[7;31mand (\x1b[7;32m    \x1b[0mg_got_things > need_thing_count\x1b[7;31m)\x1b[7;32m,\x1b[0m # Check those things.\n         )\x1b[7;31m:\x1b[0m\n')

do_test('''-        if not(
-            (that_thing_func() > THAT_IMPORTANT_THING) # Do the thing only when important.
-        and (len(list_of_things)+1 < len(some_other_list_of_things))
-        and (inside_thing() in list_of_insides) # Check whether in the list.
+        can_do_checks = (
+            (that_thing_func() > THAT_IMPORTANT_THING), # Do the thing only when important.
+            len(list_of_things)+1 < len(some_other_list_of_things),
+            inside_thing() in list_of_insides, # Check whether in the list.
''', '''\x1b[0m         \x1b[7;31mif not\x1b[7;32mcan_do_checks = \x1b[0m(\n             (that_thing_func() > THAT_IMPORTANT_THING)\x1b[7;32m,\x1b[0m # Do the thing only when important.\n         \x1b[7;31mand (\x1b[7;32m    \x1b[0mlen(list_of_things)+1 < len(some_other_list_of_things)\x1b[7;31m)\n         and (\x1b[7;32m,\n             \x1b[0minside_thing() in list_of_insides\x1b[7;31m)\x1b[7;32m,\x1b[0m # Check whether in the list.\n''')

do_test('''-if 1:
-    one()
-else:
-    not()
-    if 2:
-        pass
-    else:
-        do()
+    if 1:
+        one()
+    else:
+        not()
+        if 2:
+            pass
+        else:
+            do()
'''
, '\x1b[7;32m    \x1b[0m if 1:\n\x1b[7;32m    \x1b[0m     one()\n\x1b[7;32m    \x1b[0m else:\n\x1b[7;32m    \x1b[0m     not()\n\x1b[7;32m    \x1b[0m     if 2:\n\x1b[7;32m    \x1b[0m         pass\n\x1b[7;32m    \x1b[0m     else:\n\x1b[7;32m    \x1b[0m         do()\n')

do_test(''' A foo
+B foo
 C foo
''', '\x1b[0m A foo\n\x1b[7;32m B foo\n\x1b[0m C foo\n')

do_test('''-x   hithere b
-y   weedog  z
-sdf   sdfsdf  sdf
+x hithere    b
+y weedog     z
+sdf sdfsdf    sdf
''', '\x1b[0m x\x1b[7;31m  \x1b[0m hithere\x1b[7;32m   \x1b[0m b\n y\x1b[7;31m  \x1b[0m weedog\x1b[7;32m   \x1b[0m  z\n sdf\x1b[7;31m  \x1b[0m sdfsdf\x1b[7;32m  \x1b[0m  sdf\n')

do_test('''-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
- xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
-xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+  xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
+ xxxxxxxxxx
''', '\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m  xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n\x1b[7;32m \x1b[0m xxxxxxxxxx\n')
