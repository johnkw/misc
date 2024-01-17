import inspect, sys

def choice(prompt, allowed, default=None):
    for i in range(10):
        try: ret = input('\007'+prompt+' ('+', '.join(allowed)+'): ')
        except EOFError:
            if default != None:
                assert default in allowed
                ret = default
                print('[default: '+repr(default)+']')
            else: raise
        if ret in allowed:
            return ret
    raise

any_failures = False
def error(*msg):
    global any_failures
    print('\nERROR:',*msg)
    sys.stderr.write('ERROR: '+repr(msg)+'\n')
    any_failures = True

def check(test, *msg):
    if not test:
        error(inspect.currentframe().f_back.f_lineno, *msg)

def ensure(test, *msg):
    if not test:
        back = inspect.currentframe().f_back
        error(back.f_code.co_filename+':'+str(back.f_lineno), *msg)
        choice('Continue despite above error? ', ['continue'])
