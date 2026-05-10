import logging, reprlib, sys

def add_handler(level, handler, show_pid=False, show_thread=False):
    handler.setFormatter(logging.Formatter('%(asctime)s '+('%(process)d ' if show_pid else '')+('%(threadName)s ' if show_thread else '')+'%(message)s', '%Y-%m-%d %H:%M:%S'))
    handler.setLevel(level)
    logging.root.addHandler(handler)
    return handler

def add_rotating_log(codename, filename, maxBytes=100_000, backupCount=2):
    logging.getLogger(codename).addHandler(logging.handlers.RotatingFileHandler(filename, maxBytes=maxBytes, backupCount=backupCount))
    logging.getLogger(codename).handlers[0].setFormatter(logging.Formatter('%(asctime)s %(message)s', '%Y-%m-%d %H:%M:%S'))

def disconnect(handler):
    handler.close()
    logging.root.removeHandler(handler)

stdout = add_handler(logging.INFO, logging.StreamHandler(sys.stdout))
if not(sys.stdout.isatty() and sys.stderr.isatty()):
    stderr = add_handler(logging.ERROR, logging.StreamHandler(sys.stderr))
logging.root.setLevel(0) # the "logger" logs everything, but the handlers are more choosy
logging.raiseExceptions = False # Without this, the logging module goes crazy if we use `tail` or `head` etc.

def log(lev,msg): logging.root.log    (lev,msg)
def trace  (msg): logging.root.log    (logging.DEBUG-1,msg)
def debug  (msg): logging.root.debug  (msg)
def info   (msg): logging.root.info   (msg)
def warning(msg): logging.root.warning('WARNING: '+msg)
def error  (msg): logging.root.error  ('\007ERROR: '+msg)
def exception(msg,*args,**kwargs): logging.root.exception('\007ERROR: '+msg, *args,**kwargs)

def watch(msg):
    if stdout.level == logging.INFO:
        if len(msg) > 1 and '\n' not in msg:
            import datetime
            msg = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S ')+msg
        print(msg,end='')

_builtin_repr = repr
def repr(input_obj):
    class ReprGood(reprlib.Repr):
        def __init__(self):
            reprlib.Repr.__init__(self)
            self.maxlist=99
            self.maxdict=99
            self.indent=1
        def repr_list(self,obj,level):
            return _builtin_repr(obj) if not any(isinstance(i,(list,dict,tuple)) for i in obj) else reprlib.Repr.repr_list(self,obj,level)
    tmp = ReprGood()
    return tmp.repr(input_obj)
