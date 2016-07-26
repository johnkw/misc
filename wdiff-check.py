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

do_test('''
-    def __contains__(self, bar):
-        return bar in self.__items
+    def __contains__(self, foo):
+        assert isinstance(foo, int)
+        return foo in self.__items
''',
'\x1b[0m \n     def __contains__(self, \x1b[7;31mbar\x1b[7;32mfoo\x1b[0m):\n\x1b[7;32m         assert isinstance(foo, int)\n\x1b[0m         return \x1b[7;31mbar\x1b[7;32mfoo\x1b[0m in self.__items\n')

do_test('''
-        if not(
-            (time.time() < go_time) # Check the time for that thing.
-        and (g_got_things > need_thing_count) # Check those things.
-        ):
+        can_do_checks = (
+            time.time() < go_time, # Check the time for that thing.
+            g_got_things > need_thing_count, # Check those things.
+        )
''',
'\x1b[0m \n         \x1b[7;31mif not\x1b[7;32mcan_do_checks = \x1b[0m(\n             \x1b[7;31m(\x1b[0mtime.time() < go_time\x1b[7;31m)\x1b[7;32m,\x1b[0m # Check the time for that thing.\n         \x1b[7;31mand (\x1b[7;32m    \x1b[0mg_got_things > need_thing_count\x1b[7;31m)\x1b[7;32m,\x1b[0m # Check those things.\n         )\x1b[7;31m:\x1b[0m \n')

do_test('''
-        if not(
-            (that_thing_func() > THAT_IMPORTANT_THING) # Do the thing only when it's important.
-        and (len(list_of_things)+1 < len(some_other_list_of_things))
-        and (inside_thing() in list_of_insides) # Check whether it's in the list.
+        can_do_checks = (
+            (that_thing_func() > THAT_IMPORTANT_THING), # Do the thing only when it's important.
+            len(list_of_things)+1 < len(some_other_list_of_things),
+            inside_thing() in list_of_insides, # Check whether it's in the list.
''', '''\x1b[0m \n         \x1b[7;31mif not\x1b[7;32mcan_do_checks = \x1b[0m(\n             (that_thing_func() > THAT_IMPORTANT_THING)\x1b[7;32m,\x1b[0m # Do the thing only when it's important.\n         \x1b[7;31mand (\x1b[7;32m    \x1b[0mlen(list_of_things)+1 < len(some_other_list_of_things)\x1b[7;31m)\n         and (\x1b[7;32m,\n             \x1b[0minside_thing() in list_of_insides\x1b[7;31m)\x1b[7;32m,\x1b[0m # Check whether it's in the list.\n''')

do_test('''-if 1:
-    one()
-else:
-    not()
-    if 2:
-        pass
+    if 1:
+        one()
     else:
-        do()
+        not()
+        if 2:
+            pass
+        else:
+            do()'''
, '\x1b[7;32m    \x1b[0m if 1:\n\x1b[7;32m    \x1b[0m     one()\n\x1b[7;32m    \x1b[0m else:\n\x1b[7;32m    \x1b[0m     not()\n\x1b[7;32m    \x1b[0m     if 2:\n\x1b[7;32m    \x1b[0m         pass\n\x1b[7;32m    \x1b[0m     else:\n\x1b[7;32m    \x1b[0m         do()\x1b[7;31m \n')

do_test(''' A foo
+B foo
 C foo
''', '\x1b[0m A foo\x1b[7;32m\n B foo\x1b[0m\n C foo\n')

do_test('''
-x   hithere b
-y   weedog  z
-sdf   sdfsdf  sdf
+x hithere    b
+y weedog     z
+sdf sdfsdf    sdf
''', '\x1b[0m \n x \x1b[7;31m  \x1b[0mhithere\x1b[7;32m   \x1b[0m b\n y \x1b[7;31m  \x1b[0mweedog\x1b[7;32m   \x1b[0m  z\n sdf \x1b[7;31m  \x1b[0msdfsdf\x1b[7;32m  \x1b[0m  sdf\n')

do_test('''
-x   h b
-y   w  z
+x h    b
+y w     z
''', '\x1b[0m \n x \x1b[7;31m  \x1b[0mh\x1b[7;32m   \x1b[0m b\n y \x1b[7;31m  \x1b[0mw\x1b[7;32m   \x1b[0m  z\n')
