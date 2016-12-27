import itertools
import sys
import threading
import time

class Task(object):
    newid = itertools.count().next 

    def __init__(self, description, exclusive, fun, *args, **kwargs):
        """fun will receive a logger as the first argument"""
        self.description = description
        self.exclusive = exclusive
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.id = Task.newid()

    def run(self):
        return self.fun(*self.args, **self.kwargs)


class TaskRunner(object):
    def __init__(self, ui, executor):
        self.executor = executor
        self.ui = ui
        self.logger = ui.get_logger(self.__class__.__name__)
        self.id_to_task = dict()
        self.deps = dict()
        self.completed_tasks = set()
        self.started_tasks = set()
        self.state_lock = threading.Lock()
        self.error = False

    def add_task(self, task, deps):
        self.id_to_task[task.id] = task
        task_deps = []
        for dep in deps:
            if hasattr(dep, 'id') and isinstance(dep.id, int):
                task_deps.append(dep.id)
            elif isinstance(dep, int):
                task_deps.append(dep)
            else:
                self.logger.critical("Invalid dependency passed!")
                assert False
        self.deps[task.id] = task_deps

    def run(self):
        while True:
            with self.state_lock:
                if self.error:
                    self.logger.error(
                        "An error has occurred while executing a task."
                    )
                    sys.exit(1)
                if len(self.started_tasks) == len(self.id_to_task):
                    break
                tasks_started = 0
                for task in self.id_to_task.keys():
                    if task in self.started_tasks:
                        continue
                    can_start = True
                    for dep in self.deps[task]:
                        if dep not in self.completed_tasks:
                            can_start = False
                            break
                    if can_start:
                        tasks_started += 1
                        self.started_tasks.add(task)
                        if self.id_to_task[task].exclusive:
                            self.executor.run_exclusive(self.__inside, task)
                        else:
                            self.executor.run(self.__inside, task)
                if tasks_started == 0 and self.executor.has_finished():
                    self.logger.error(
                        "No tasks are running and no task could be started. "
                        "This probably means there is a cicle in the "
                        "dependency graph."
                    )
                    sys.exit(1)
            time.sleep(0.01)
        self.executor.join()
        if self.error:
            self.logger.error(
                "An error has occurred while executing a task."
            )
            sys.exit(1)

    def __inside(self, task):
        task = self.id_to_task[task]
        try:
            with self.ui.get_logger(task.description) as logger:
                task.fun(logger, *task.args, **task.kwargs)
        except:
            with self.state_lock:
                self.error = True
            return
        with self.state_lock:
            self.completed_tasks.add(task.id)
