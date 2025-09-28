import logging, reprlib, sys

def add_handler(level, handler, show_pid=False):
    handler.setFormatter(logging.Formatter('%(asctime)s '+('%(process)d ' if show_pid else '')+'%(message)s', '%Y-%m-%d %H:%M:%S'))
    handler.setLevel(level)
    logging.root.addHandler(handler)
    return handler

stdout = add_handler(logging.INFO, logging.StreamHandler(sys.stdout))
if not(sys.stdout.isatty() and sys.stderr.isatty()):
    stderr = add_handler(logging.ERROR, logging.StreamHandler(sys.stderr))
logging.root.setLevel(0) # the "logger" logs everything, but the handlers are more choosy
logging.raiseExceptions = False # Without this, the logging module goes crazy if we use `tail` or `head` etc.

def log(lev,msg,*args,**kwargs): logging.root.log    (lev,msg,*args,**kwargs)
def trace  (msg,*args,**kwargs): logging.root.log    (logging.DEBUG-1,msg,*args,**kwargs)
def debug  (msg,*args,**kwargs): logging.root.debug  (msg,*args,**kwargs)
def info   (msg,*args,**kwargs): logging.root.info   (msg,*args,**kwargs)
def warning(msg,*args,**kwargs): logging.root.warning('WARNING: '+msg,*args,**kwargs)
def error  (msg,*args,**kwargs): logging.root.error  ('\007ERROR: '+msg,*args,**kwargs)
def exception(msg,*args,**kwargs): logging.root.exception('\007ERROR: '+msg,*args,**kwargs)

def watch(msg):
    if stdout.level == logging.INFO:
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
