#!/bin/python -ubb

import cmdargs, clog, fcntl, os, re, select, subprocess, sys, time

cmdargs.parse(
    ('--ip',{'default':'8.8.8.8'}),
    ('--timeout',{'type':int,'default':6}),
)
ping_proc = subprocess.Popen(['ping','-i4',cmdargs['ip']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
readable = [fd.fileno() for fd in [ping_proc.stdout, ping_proc.stderr]]
for fd in readable:
    fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)
header = 'PING '+cmdargs['ip']+' ('+cmdargs['ip']+') 56(84) bytes of data.\n'
is_good = None
alert_status = None
last_alert_status = 0
last_good_time = time.time()

while readable:
    ready, _, _ = select.select(readable, [], [], 1)
    for fd in ready:
        data = os.read(fd, 4096).decode('ascii')
        if fd == ping_proc.stderr.fileno():
            clog.warning('stderr '+repr(data))
            is_good = 0
        else:
            if data.startswith(header):
                data = data.removeprefix(header)
                header = ''
            if (r := re.match('64 bytes from '+cmdargs['ip']+': icmp_seq=\\d+ ttl=\\d+ time=(\\d+\\.?\\d+) ms\n', data)) and (float(r.groups()[0]) < 200):
                if is_good:
                    sys.stdout.write({0:'|',1:'/',2:'-',3:'\\'}[is_good%4]+'\b')
                else:
                    clog.info('Online'+(' after %d seconds'%d if (d:=last_good_time - time.time()) > cmdargs['timeout']*2 else '')+'.')
                    is_good = 1
                is_good += 1
                last_good_time = time.time()
            else:
                for i in data.splitlines():
                    clog.warning('stdout '+i)
                    is_good = 0
        if not data:
            clog.warning('EOF from '+repr(fd)+'???')
            readable.remove(fd)
    if is_good != 0 and time.time() - last_good_time > cmdargs['timeout']:
        clog.warning('offline as per no replies in %d seconds'%cmdargs['timeout'])
        is_good = 0
    if alert_status is None:
        alert_status = bool(is_good)
    if (alert_status != bool(is_good)) and (time.time() - last_alert_status > 60):
        sys.stdout.write('\a')
        alert_status = bool(is_good)
        last_alert_status = time.time()
