import threading
import multiprocessing
import time

class TaskExecutor(object):
    def __init__(self, thread_count=None):
        if thread_count is None:
            thread_count = multiprocessing.cpu_count()
        self.max_running = thread_count
        self.state_lock = threading.Lock()
        self.job_finished = threading.Condition(self.state_lock)
        self.running_count = 0
        self.running_excl = False
        self.jobs = set()

    def run(self, fun, *args, **kwargs):
        with self.state_lock:
            thrd = threading.Thread(
                target=self.__inside, args=(False, fun, args, kwargs)
            )
            self.jobs.add(thrd)
            thrd.start()

    def run_exclusive(self, fun, *args, **kwargs):
        with self.state_lock:
            thrd = threading.Thread(
                target=self.__inside, args=(True, fun, args, kwargs)
            )
            self.jobs.add(thrd)
            thrd.start()
        
    def join(self):
        while True:
            with self.state_lock:
                if len(self.jobs) == 0:
                    break
            time.sleep(0.01)

    def __inside(self, exclusive, fun, args, kwargs):
        with self.state_lock:
            if exclusive:
                while self.running_excl is True or self.running_count > 0:
                    self.job_finished.wait()
                self.running_excl = True
            else:
                while self.running_excl is True or \
                      self.running_count == self.max_running:
                    self.job_finished.wait()
                self.running_count += 1
        try:
            fun(*args, **kwargs)
        finally:
            with self.state_lock:
                self.job_finished.notify()
                self.jobs.remove(threading.current_thread())
                if exclusive:
                    self.running_excl = False
                else:
                    self.running_count -= 1
