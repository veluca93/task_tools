import itertools
import logging
import os
import time
import threading

try:
    import Queue
except ImportError:
    import queue as Queue

class TaskDescription(object):
    newid = itertools.count().next

    def __init__(self, description):
        self.description = description
        self.id = (os.getpid(), TaskDescription.newid())

    def get_id(self):
        return self.id

    def get_description(self):
        return self.description


class ProcessUIInterface(object):
    def __init__(self, queue):
        self.queue = queue

    def start_task(self, description):
        descr = TaskDescription(description)
        self.queue.put([None, GenericUI.TASK_STARTING, descr])
        return descr

    def stop_task(self, task_descr):
        self.queue.put([None, GenericUI.TASK_STOPPING, task_descr])

    def log(self, lvl, task_descr, msg, *args, **kwargs):
        self.queue.put([lvl, task_descr, msg, args, kwargs])

    def debug(self, task_descr, msg, *args, **kwargs):
        self.log(logging.DEBUG, task_descr, msg, *args, **kwargs)
    
    def info(self, task_descr, msg, *args, **kwargs):
        self.log(logging.INFO, task_descr, msg, *args, **kwargs)

    def warning(self, task_descr, msg, *args, **kwargs):
        self.log(logging.WARNING, task_descr, msg, *args, **kwargs)

    def error(self, task_descr, msg, *args, **kwargs):
        self.log(logging.ERROR, task_descr, msg, *args, **kwargs)

    def critical(self, task_descr, msg, *args, **kwargs):
        self.log(logging.CRITICAL, task_descr, msg, *args, **kwargs)


class GenericUI(object):
    TASK_STARTING = 1
    TASK_STOPPING = 2

    def __init__(self):
        self.queue = Queue()
        self.thread = threading.Thread(target=self.run, args=())
        self.stopping = False

    def start_ui(self):
        self.thread.start()

    def stop_ui(self):
        self.stopping = True
        self.thread.join()

    def run(self):
        stop_attempts = 0
        while True:
            try:
                data = self.queue.get_nowait()
                if data[0] is None:
                    if data[1] == GenericUI.TASK_STARTING:
                        self.register(data[2])
                    else:
                        self.unregister(data[2])
                else:
                    self.handle(data[0], data[1], data[2], *data[3], **data[4])
            except Queue.Empty:
                if self.stopping:
                    stop_attempts += 1
                    if stop_attempts > 10:
                        break
                time.sleep(0.01)

    def get_logger(self):
        return ProcessUIInterface(self.queue)

    # Methods that should be replaced by subclasses

    def register(self, task_descr):
        """Method that is called when a task is started"""
        self.handle(logging.INFO, task_descr, "Starting...", [], dict())

    def unregister(self, task_descr):
        """Method that is called when a task is stopped"""
        self.handle(logging.INFO, task_descr, "Stopping...", [], dict())

    def handle(self, lvl, task_descr, msg, *args, **kwargs):
        """Method that is called for each message sent"""
        raise NotImplementedError("Please subclass this class")
        
