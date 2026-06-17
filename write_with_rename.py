import io, lzma, os, tempfile, time

class WriteWithRename(object):
    __slots__ = ['filename', 'logging', 'binary', 'compress', 'tf']
    def __init__(self, filename, logging=True, binary=False, compress=False):
        assert isinstance(filename, str)
        assert isinstance(binary,   bool)
        if logging is True:
            import clog
            logging = clog.trace
        else:
            assert logging is False or callable(logging)
        self.filename = filename
        self.logging  = logging
        self.binary   = binary
        self.compress = compress
    def __enter__(self):
        if self.logging:
            self.logging('WriteWithRename writing '+('binary' if self.binary else 'text')+' '+self.filename)
        self.tf = tempfile.NamedTemporaryFile(dir=os.path.dirname(self.filename), delete=False)
        if self.compress:
            self.tf.file = lzma.LZMAFile(self.tf.file, 'a', format=lzma.FORMAT_XZ,preset=9|lzma.PRESET_EXTREME)
        if not self.binary:
            self.tf.file = io.TextIOWrapper(self.tf.file, write_through=True)
        return self.tf.file
    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.tf.file.close()
        self.tf.close()
        if _exc_type == None:
            os.rename(self.tf.name, self.filename)
            final_time = time.time()
            os.utime(self.filename, times=(final_time, final_time))
        else:
            if self.logging:
                self.logging('WriteWithRename deleting temp file per: %s %s %s' % (_exc_type, _exc_value, _traceback))
            os.unlink(self.tf.name)

class WriteCSV(WriteWithRename):
    __slots__ = ['dialect', 'fields']
    def __init__(self, filename, fields, /, logging=True, binary=False, compress=False, dialect='excel'):
        super().__init__(filename, logging=logging, binary=binary, compress=compress)
        self.dialect = dialect
        self.fields  = fields
    def __enter__(self):
        import csv
        csvwriter = csv.DictWriter(super().__enter__(), self.fields, dialect=self.dialect)
        csvwriter.writeheader()
        return csvwriter

def write(filename, data, /, logging=True, compress=False):
    with WriteWithRename(filename, binary=bool(isinstance(data,bytes)), logging=logging, compress=compress) as f:
        f.write(data)
