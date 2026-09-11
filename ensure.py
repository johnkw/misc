import clog, inspect, select, sys

def input_timeout(prompt, timeout):
    print(prompt,end='')
    read, _, _ = select.select([sys.stdin], [], [], timeout)
    if read:
        ret = sys.stdin.readline()
        if ret == '':
            print('EOF')
            return None
        return ret.removesuffix('\n')
    else:
        print('input timeout')
        return None

def choice(prompt, allowed, default=None, timeout=None):
    for i in range(10):
        ret = input_timeout('\007'+prompt+' ('+', '.join(allowed)+'): '+('(timeout '+str(timeout)+') ' if timeout else ''), timeout)
        if ret == None:
            if default != None:
                assert default in allowed
                ret = default
                print('[default: '+repr(default)+']')
            else:
                raise Exception('no input and no default')
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
    clog.error(' '.join(str(i) for i in msg))
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
    def __setitem__(self, i, n):
        self.__used.add(i)
        return dict.__setitem__(self, i, n)
    def pop(self, i):
        self.__used.discard(i)
        return dict.pop(self, i)
    def unused(self): return self.__used ^ set(self.keys())
