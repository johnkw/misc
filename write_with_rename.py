import csv, io, lzma, os, tempfile, time

class WriteWithRename(object):
    __slots__ = ['filename', 'logging', 'binary', 'compress', 'tf', 'no_touch_if_identical']
    def __init__(self, filename, logging=True, binary=False, compress=False, no_touch_if_identical=False):
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
        self.no_touch_if_identical = no_touch_if_identical
    def __enter__(self):
        if self.logging:
            self.logging('WriteWithRename writing '+('binary' if self.binary else 'text')+' '+self.filename)
        self.tf = tempfile.NamedTemporaryFile(dir=os.path.dirname(self.filename), delete=False, prefix='write_with_rename.')
        if self.compress:
            self.tf.file = lzma.LZMAFile(self.tf.file, 'a', format=lzma.FORMAT_XZ,preset=9|lzma.PRESET_EXTREME)
        if not self.binary:
            self.tf.file = io.TextIOWrapper(self.tf.file)
        return self.tf.file
    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.tf.file.close()
        self.tf.close()
        if _exc_type == None:
            if self.no_touch_if_identical and open(self.tf.name,'rb').read() == open(self.filename,'rb').read():
                os.unlink(self.tf.name)
                return
            os.rename(self.tf.name, self.filename)
            final_time = time.time()
            os.utime(self.filename, times=(final_time, final_time))
        else:
            if self.logging:
                self.logging('WriteWithRename deleting temp file per: %s %s %s' % (_exc_type, _exc_value, _traceback))
            os.unlink(self.tf.name)

class WriteCSV(WriteWithRename):
    __slots__ = ['dialect', 'fields']
    def __init__(self, filename, fields, /, logging=True, binary=False, compress=False, dialect='excel', no_touch_if_identical=False):
        super().__init__(filename, logging=logging, binary=binary, compress=compress, no_touch_if_identical=no_touch_if_identical)
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

def change_csv(filepath, callback, /, compress=False, dialect=csv.excel_tab, callback_args=[], callback_vargs={}, no_touch_if_identical=False):
    reader = csv.DictReader((lzma.open if compress else open)(filepath,'rt'), dialect=dialect)
    with WriteCSV(filepath, reader.fieldnames, compress=compress, dialect=dialect, no_touch_if_identical=no_touch_if_identical) as writer:
        for row in callback(reader, *callback_args, **callback_vargs):
            writer.writerow(row)
