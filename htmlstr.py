import html, io

class htmlstr(object):
    __slots__ = ['_s']
    def __init__(self, s):
        self._s = str(s)
    def __iadd__(self, other):
        if not isinstance(other, htmlstr): raise Exception(repr(other)+' not htmlstr')
        self._s += other._s
        return self
    def __add__(self, other):
        if not isinstance(other, htmlstr): raise Exception(repr(other)+' not htmlstr')
        return htmlstr(self._s + other._s)
    def __lt__(self, other):
        return self._s < other._s
    def __str__(self):
        return self._s
    def __nonzero__(self):
        return bool(self._s)
    @staticmethod
    def argesc(arg):
        if   isinstance(arg, int):        return arg
        elif isinstance(arg, float):      return arg
        elif isinstance(arg, str):        return html.escape(arg)
        elif isinstance(arg, tuple):      return tuple([htmlstr.argesc(a) for a in arg])
        elif arg == None: return arg
        else: assert 0, repr(arg)
    @staticmethod
    def htmlesc(arg):
        return htmlstr(htmlstr.argesc(arg))
    def __pow__(self, dangerous_args):
        return htmlstr(str.__mod__(self._s, htmlstr.argesc(dangerous_args)))
    def join(self, args):
        arrstr = []
        for arg in args:
            if not isinstance(arg, htmlstr): raise Exception(repr(arg)+' not htmlstr')
            arrstr.append(arg._s)
        return htmlstr(self._s.join(arrstr))

class HTMLStrIO(io.TextIOWrapper):
    def write(self, s):
        if type(s) != htmlstr: raise Exception('can only write htmlstr to HTMLStrIO')
        io.TextIOWrapper.write(self, str(s))
