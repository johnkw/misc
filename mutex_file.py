import clog, datetime, fcntl, os, psutil, stat, time

class MutexFile():
    __slots__ = ['__lock_file_name','__lock_file_handle','__lock_time']

    def __init__(self, lock_file_name):
        self.__lock_file_name = lock_file_name
        self.__lock_file_handle = None

    def attempt_lock(self, log_level=clog.info):
        if not os.stat(self.__lock_file_name).st_mode & stat.S_IRUSR:
            raise Exception('chmod 600 '+self.__lock_file_name)
        if self.__lock_file_handle:
            raise Exception('already locked')
        self.__lock_file_handle = open(self.__lock_file_name,'r+')
        try:
            fcntl.flock(self.__lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lock_data = self.__lock_file_handle.read().strip()
            try:
                p = psutil.Process(int(lock_data))
                lock_data += ' '+repr(p.cmdline())+' '+str(datetime.datetime.fromtimestamp(p.create_time()))[:19]+' '+p.status()
            except Exception as e:
                lock_data += ' error '+str(e)
            log_level('waiting for lock: '+self.__lock_file_name+' '+lock_data)
            os.utime(self.__lock_file_name)
            self.__lock_file_handle = None
        else:
            self.__lock_file_handle.seek(os.SEEK_SET, 0)
            self.__lock_file_handle.truncate(0)
            self.__lock_file_handle.write(str(os.getpid())+'\n')
            self.__lock_file_handle.flush()
            self.__lock_time = time.time()
        return self.is_locked()

    def wait_for_lock(self):
        had_to_wait = 0
        while not self.attempt_lock(clog.info if had_to_wait > 10 else clog.debug):
            time.sleep(1)
            had_to_wait += 1
        (clog.info if had_to_wait > 10 else clog.debug)('got lock for '+self.__lock_file_name)

    def something_is_waiting(self):
        return os.path.getmtime(self.__lock_file_name) > self.__lock_time

    def __enter__(self):
        self.wait_for_lock()
        return self
    def __exit__(*args): pass

    def is_locked(self):
        return self.__lock_file_handle != None

def create_and_wait_for_lock(filename):
    lock = MutexFile(filename)
    lock.wait_for_lock()
    return lock
