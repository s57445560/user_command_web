#!/usr/bin/python
# coding=utf8
# author: Sun yang

import logging
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Log():
    def __init__(self, logname, logger, level):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(level)
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s -%(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def getlog(self):
        return self.logger


print_logs = Log(logname="%s/logs/monitor.log" % BASE, logger="message", level=logging.DEBUG).getlog()
