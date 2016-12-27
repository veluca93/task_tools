from __future__ import print_function

import logging
import time
import traceback

from italianformat.ui import SimpleUI
from italianformat.executor import TaskExecutor
from italianformat.runner import Task, TaskRunner

def fun(logger, sleep_time, output):
    time.sleep(sleep_time)
    logger.output(output)
    #raise RuntimeError("")

def main():
    # Parse arguments and run the right commands.
    ui = SimpleUI(logging.INFO)
    with ui:
        executor = TaskExecutor(ui, 2)
        runner = TaskRunner(ui, executor)

        task0 = Task("task0", False, fun, 0.4, "0")
        task1 = Task("task1", False, fun, 0.1, "1")
        task2 = Task("task2", False, fun, 0.1, "2")
        task3 = Task("task3", True, fun, 0.1, "3")

        task4 = Task("task4", True, fun, 0.1, "4")
        task5 = Task("task5", False, fun, 0.1, "5")
        task6 = Task("task6", False, fun, 0.1, "6")

        task7 = Task("task7", True, fun, 0.1, "7")
        task8 = Task("task8", False, fun, 0.4, "8")
        task9 = Task("task9", False, fun, 0.1, "9")

        runner.add_task(task0, [])
        runner.add_task(task1, [])
        runner.add_task(task2, [])
        runner.add_task(task3, [])

        runner.add_task(task4, [task0])
        runner.add_task(task5, [task1])
        runner.add_task(task6, [task2])

        runner.add_task(task7, [task0, task1, task2, task3])
        runner.add_task(task8, [task0, task1, task2, task3])
        runner.add_task(task9, [task7, task8])

        runner.run()
