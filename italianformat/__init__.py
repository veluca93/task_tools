from __future__ import print_function

import logging
import time

from italianformat.ui import SimpleUI
from italianformat.executor import TaskExecutor

def fun(sleep_time, logger, name):
    task = logger.start_task(name)
    time.sleep(sleep_time)
    logger.output(task, name)
    logger.stop_task(task)

def main():
    # Parse arguments and run the right commands.
    ui = SimpleUI(logging.DEBUG)
    ui.start_ui()
    logger = ui.get_logger()
    executor = TaskExecutor(2)
    executor.run(fun, 0.1, logger, "1")
    executor.run(fun, 0.1, logger, "2")
    executor.run(fun, 0.1, logger, "3")
    executor.run(fun, 0.1, logger, "4")
    executor.run(fun, 0.1, logger, "5")
    executor.run_exclusive(fun, 0.1, logger, "excl1")
    executor.run(fun, 0.1, logger, "6")
    executor.run(fun, 0.1, logger, "7")
    executor.run(fun, 0.1, logger, "8")
    executor.run(fun, 0.1, logger, "9")
    executor.run(fun, 0.1, logger, "10")
    executor.run_exclusive(fun, 0.1, logger, "excl2")
    executor.join()
    ui.stop_ui()
