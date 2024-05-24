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

error_count = 0
def error(*msg, frames_back=1):
    global error_count
    back = inspect.currentframe()
    for i in range(frames_back):
        back = back.f_back
    msg = [back.f_code.co_filename.rsplit('/')[-1]+':'+str(back.f_lineno)] + list(msg)
    print('\nERROR:',*msg)
    sys.stderr.write('ERROR: '+' '.join(str(i) for i in msg)+'\n')
    error_count += 1

def check(test, *msg, frames_back=2):
    if not test:
        error(*msg, frames_back=frames_back)
    return test

def ensure(test, *msg, frames_back=2):
    if not test:
        error(*msg, frames_back=frames_back)
        choice('Continue despite above error? ', ['continue'])
    return test

class isused_dict(dict):
    __slots__ = ['__used']
    def __init__(self, init):
        dict.__init__(self, init)
        self.__used = set()
    def __getitem__(self, i):
        self.__used.add(i)
        return dict.__getitem__(self, i)
    def unused(self): return self.__used ^ set(self.keys())
