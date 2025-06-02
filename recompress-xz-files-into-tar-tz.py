#!/bin/python -ttu

import cmdargs, io, lzma, tarfile

cmdargs.parse('output-tar-xz',('input-xz',{'nargs':'+'}))
assert cmdargs['output-tar-xz'].endswith('.tar.xz')
with tarfile.open(cmdargs['output-tar-xz'],'x:xz',preset=9|lzma.PRESET_EXTREME) as tar:
    for file in cmdargs['input-xz']:
        assert file.endswith('.xz')
        tarinfo = tar.gettarinfo(file)
        tarinfo.name = tarinfo.name.removesuffix('.xz')
        data = lzma.open(file).read()
        tarinfo.size = len(data)
        tar.addfile(tarinfo, io.BytesIO(data))
