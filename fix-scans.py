#!/bin/python -ubb

import cmdargs, clog, datetime, functools, os, subprocess

cmdargs.parse(
    ('--color',{'choices':['color','gray','bw'],'default':'gray'}),
    ('--flips'),
    ('--quality',{'type':int,'default':15}),
    ('--brightness-contrast',{'default':'0x30'}),
    ('--type',{'default':'avif'})
)
flips = [int(i) for i in cmdargs['flips'].split(',')] if cmdargs['flips'] else []
os.chdir(os.path.expanduser('~/.tmp/scans'))
scans = sorted((os.path.getmtime(i),i) for i in os.listdir() if i.startswith('Scan') and i.endswith('.png'))
assert len(flips) == len(set(flips))
assert all(1 <= i <= len(scans) for i in flips)

# This part is quite slow, so only do it once in case we want to change some other option after seeing the output.
for i in scans:
    if not os.path.exists('trimmed-'+i[1]):
        clog.info('trimming '+i[1])
        subprocess.check_call(['magick','-gravity','center',i[1],'-shave','20x20','-set','option:color','%[pixel:u.p{-1,1}]','-background','%[color]','+deskew','-despeckle','-fuzz','18%','-trim','+repage','-flatten','trimmed-'+i[1]])

subprocess.check_call(
    ['magick','-gravity','center','-background','white']+
    functools.reduce(
        lambda a,b:a+['(','-size','60x60','xc:Transparent',')']+b,
        (['(','trimmed-'+file[1]]+(['-rotate','180'] if num+1 in flips else [])+[')'] for num,file in enumerate(scans))
    )+
    ['-append','+repage','-strip','-flatten','-resize','2000x','-type','optimize']+
    (['-colorspace','gray'] if cmdargs['color'] in ('gray','bw') else [])+
    (['-type','grayscale','-threshold','80%','-depth','1','-define','webp:lossless=true'] if cmdargs['color'] == 'bw' else ['-quality',str(cmdargs['quality']),'-brightness-contrast',cmdargs['brightness-contrast']])+
    [datetime.datetime.fromtimestamp(scans[-1][0]).strftime('%Y-%m-%d_%H_%M_%S.'+cmdargs['type'])])
