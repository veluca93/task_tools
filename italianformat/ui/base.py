import itertools
import logging
import time
import threading
import traceback

try:
    import Queue
except ImportError:
    import queue as Queue


class UIInterface(object):
    newid = itertools.count().next

    def __init__(self, queue, description):
        self.queue = queue
        self.description = description
        self.id = UIInterface.newid()

    def __put(self, args):
        self.queue.put([self.id, self.description] + args)

    def __enter__(self):
        self.__put([None, GenericUI.TASK_STARTING])
        return self

    def __exit__(self, type, value, tb):
        if value is not None:
            self.error(
                "".join(traceback.format_exception(type, value, tb))
            )
        self.__put([None, GenericUI.TASK_STOPPING, value is not None])

    def log(self, lvl, msg, *args, **kwargs):
        self.__put([lvl, msg, args, kwargs])

    def debug(self, msg, *args, **kwargs):
        self.log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.log(logging.CRITICAL, msg, *args, **kwargs)

    def output(self, msg, *args, **kwargs):
        self.log(GenericUI.OUTPUT, msg, *args, **kwargs)


class GenericUI(object):
    TASK_STARTING = 1
    TASK_STOPPING = 2
    OUTPUT = logging.CRITICAL+10

    def __init__(self):
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self.run, args=())
        self.stopping = False

    def __enter__(self):
        self.thread.start()

    def __exit__(self, type, value, tb):
        self.stopping = True
        self.thread.join()

    def run(self):
        stop_attempts = 0
        while True:
            try:
                data = self.queue.get_nowait()
                if data[2] is None:
                    if data[3] == GenericUI.TASK_STARTING:
                        self.register(data[0], data[1])
                    else:
                        self.unregister(data[0], data[1], data[4])
                else:
                    self.handle(
                        data[0], data[1], data[2],
                        data[3], *data[4], **data[5]
                    )
            except Queue.Empty:
                if self.stopping:
                    stop_attempts += 1
                    if stop_attempts > 10:
                        break
                time.sleep(0.01)

    def get_logger(self, description):
        return UIInterface(self.queue, description)

    # Methods that should be replaced by subclasses

    def register(self, id, descr):
        """Method that is called when a task is started"""
        self.handle(
            id, descr, logging.INFO,
            "Starting...", [], dict()
        )

    def unregister(self, id, descr, exc):
        """Method that is called when a task is stopped"""
        self.handle(
            id, descr, logging.INFO, "Exiting because of an exception"
            if exc else "Concluded successfully", [], dict()
        )

    def handle(self, id, descr, lvl, msg, *args, **kwargs):
        """Method that is called for each message sent"""
        raise NotImplementedError("Please subclass this class")
        
