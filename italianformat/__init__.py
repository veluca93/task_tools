from __future__ import print_function

import logging

from .ui import SimpleUI

def main():
    # Parse arguments and run the right commands.
    ui = SimpleUI(logging.DEBUG)
    ui.start_ui()
    logger = ui.get_logger()
    task = logger.start_task("Test")
    logger.debug(task, "debug")
    logger.info(task, "info")
    logger.warning(task, "warning")
    logger.error(task, "error")
    logger.critical(task, "critical")
    logger.stop_task(task)
    ui.stop_ui()
