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
def error(*msg, frames_back=1):
    global any_failures
    back = inspect.currentframe()
    for i in range(frames_back):
        back = back.f_back
    msg = [back.f_code.co_filename.rsplit('/')[-1]+':'+str(back.f_lineno)] + list(msg)
    print('\nERROR:',*msg)
    sys.stderr.write('ERROR: '+' '.join(repr(i) for i in msg)+'\n')
    any_failures = True

def check(test, *msg):
    if not test:
        error(*msg, frames_back=2)
    return test

def ensure(test, *msg):
    if not test:
        error(*msg, frames_back=2)
        choice('Continue despite above error? ', ['continue'])
