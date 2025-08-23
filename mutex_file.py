import clog, datetime, fcntl, os, psutil, stat, time

class MutexFile():
    __slots__ = ['__lock_file_name','__lock_file_handle']

    def __init__(self, lock_file_name):
        self.__lock_file_name = lock_file_name
        self.__lock_file_handle = None

    def attempt_lock(self):
        if not os.stat(self.__lock_file_name).st_mode & stat.S_IRUSR:
            raise Exception('chmod 600 '+self.__lock_file_name)
        if self.__lock_file_handle:
            raise Exception('already locked')
        self.__lock_file_handle = open(self.__lock_file_name,'r+')
        try:
            fcntl.flock(self.__lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lock_data = self.__lock_file_handle.read()
            try:
                p = psutil.Process(int(lock_data))
                lock_data += ' '+repr(p.cmdline())+' '+str(datetime.datetime.fromtimestamp(p.create_time()))[:19]+' '+p.status()
            except Exception as e:
                lock_data += ' error '+str(e)
            clog.info('waiting for lock: '+lock_data)
            self.__lock_file_handle = None
        else:
            self.__lock_file_handle.seek(os.SEEK_SET, 0)
            self.__lock_file_handle.truncate(0)
            self.__lock_file_handle.write(str(os.getpid()))
            self.__lock_file_handle.flush()
        return self.is_locked()

    def is_locked(self):
        return self.__lock_file_handle != None

__global_lock = None
def wait_for_global_lock(filename):
    global __global_lock
    if __global_lock:
        raise NotImplementedError
    __global_lock = MutexFile(filename)
    while not __global_lock.attempt_lock(): time.sleep(1)
