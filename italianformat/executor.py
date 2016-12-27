import multiprocessing
import threading
import time
import traceback


class TaskExecutor(object):
    def __init__(self, ui, thread_count=None):
        if thread_count is None:
            thread_count = multiprocessing.cpu_count()
        self.max_running = thread_count
        self.state_lock = threading.Lock()
        self.job_finished = threading.Condition(self.state_lock)
        self.running_count = 0
        self.running_excl = False
        self.jobs = set()
        self.ui = ui

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

    def has_finished(self):
        with self.state_lock:
            return len(self.jobs) == 0

    def join(self):
        while True:
            if self.has_finished():
                break
            time.sleep(0.01)

    def __inside(self, exclusive, fun, args, kwargs):
        this_thread = threading.current_thread()
        logger = self.ui.get_logger(
            self.__class__.__name__ + " " + str(this_thread.ident)
        )
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
            logger.debug("Starting job")
            fun(*args, **kwargs)
            logger.debug("Job completed successfully")
        except:
            logger.error(traceback.format_exc())
        finally:
            with self.state_lock:
                self.job_finished.notify()
                self.jobs.remove(this_thread)
                if exclusive:
                    self.running_excl = False
                else:
                    self.running_count -= 1
