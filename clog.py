import logging, sys

def add_handler(level, handler, show_pid=False):
    handler.setFormatter(logging.Formatter('%(asctime)s '+('%(process)d ' if show_pid else '')+'%(message)s', '%Y-%m-%d %H:%M:%S'))
    handler.setLevel(level)
    logging.root.addHandler(handler)
    return handler

stdout = add_handler(logging.INFO, logging.StreamHandler(sys.stdout))
stderr = add_handler(logging.ERROR, logging.StreamHandler(sys.stderr))
logging.root.setLevel(0) # the "logger" logs everything, but the handlers are more choosy

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
