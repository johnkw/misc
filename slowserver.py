#!/usr/bin/python

import cmdargs, os, http.server, time

cmdargs.parse(
    ('PORT',    {'type':int,   'help':'Port number to run on'}),
    ('SECONDS', {'type':float, 'help':'Seconds to wait before responding'}),
    ('PATH',    {'type':str,   'help':'Path to serve.'}),
)

class SlowserverRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(s):
        try: time.sleep(cmdargs['SECONDS'])
        except: os._exit(0)
        http.server.SimpleHTTPRequestHandler.do_GET(s)

SlowserverRequestHandler.extensions_map[''] = 'text/html'
os.chdir(cmdargs['PATH'])
http.server.HTTPServer(('', cmdargs['PORT']), SlowserverRequestHandler).serve_forever()
