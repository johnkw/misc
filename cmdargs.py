import argparse, clog, sys, types

class tmp(types.ModuleType):
    def __getitem__(self, name): return self.vars_args[name]
    def __contains__(self, name):return name in self.vars_args
    def subparse(self, var, *options):
        parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=9999, max_help_position=9999))

        for arg in options:
            if isinstance(arg, tuple):
                arg, kwarg = arg
            else:
                kwarg = {}
            if 'default' in kwarg:
                if 'help' not in kwarg:
                    kwarg['help'] = ''
                else:
                    kwarg['help'] += ' '
                if type(kwarg['default']) == str:
                    kwarg['help'] += '(default: "%(default)s")'
                else:
                    kwarg['help'] += '(default: %(default)s)'
            if arg[0] in parser.prefix_chars:
                kwarg['dest'] = arg.lstrip(parser.prefix_chars) # stop argparse confusingly converting - to _
            parser.add_argument(arg, **kwarg)
        return vars(parser.parse_args(var))
    def parse(self, *options):
        options = list(options)
        for arg in options:
            if isinstance(arg, str):
                assert arg != '--debug'
            elif arg[0] == '--debug':
                assert 'type' in arg[1]
                assert arg[1]['type'] == int
                break
        else:
            options.append(('--debug',{'type':int,'default':0,'metavar':'num'}))
        options.append(('--quiet',{'action':'store_true'}))
        options.append(('--logstdout',{'choices':clog.logging.getLevelNamesMapping().keys(),'metavar':'level-name'}))

        self.vars_args = self.subparse(None, *options)
        if not self.vars_args['logstdout']:
            if self.vars_args['debug'] > 0:
                self.vars_args['logstdout'] = 'NOTSET' if self.vars_args['debug'] > 1 else 'DEBUG'
            if self.vars_args['quiet']:
                self.vars_args['logstdout'] = 'ERROR'
        if self.vars_args['logstdout']:
            clog.stdout.setLevel(clog.logging.getLevelNamesMapping()[self.vars_args['logstdout']])

sys.modules[__name__] = tmp('')
