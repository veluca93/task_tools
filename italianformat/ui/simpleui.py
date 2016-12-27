from __future__ import print_function

import logging
import sys

from .base import GenericUI

class SimpleUI(GenericUI):
    def __init__(self, lvl=logging.INFO):
        self.lvl_to_string = {
            logging.DEBUG: "DEBUG",
            logging.INFO: "INFO",
            logging.WARNING: "WARNING",
            logging.ERROR: "ERROR",
            logging.CRITICAL: "CRITICAL"
        }
        self.lvl_to_color = {
            logging.DEBUG: '\033[34;1m',
            logging.INFO: '\033[32;1m',
            logging.WARNING: '\033[33;1m',
            logging.ERROR: '\033[31;1m',
            logging.CRITICAL: '\033[35;1m'
        }
        self.end_color = '\033[0m'
        self.lvl = lvl
        if sys.stdout.isatty():
            self.use_colors = True
        super(SimpleUI, self).__init__()

    def handle(self, lvl, task_descr, msg, *args, **kwargs):
        if lvl == GenericUI.OUTPUT:
            print(msg.format(*args, **kwargs))
        elif lvl >= self.lvl:
            prefix = self.lvl_to_string[lvl].rjust(8)
            prefix += " "
            prefix += task_descr.description
            prefix = "[" + prefix + "]"
            if self.use_colors:
                prefix = self.lvl_to_color[lvl] + prefix + self.end_color
            print(prefix + " " + msg.format(*args, **kwargs))
