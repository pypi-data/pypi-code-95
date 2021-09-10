#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Additional utilities
"""

from time import time
from datetime import datetime
from .config import Config as config


def ts() -> None:
    """
    Get the current date and time in the format% YYYY-MM-DD HH:MM:SS
    """
    get_time = time()
    ts = datetime.fromtimestamp(get_time).strftime('%Y-%m-%d %H:%M:%S')
    return ts


class Message(object):
    """
    Formation of a log.
    Usage example:

    from util import Message

    msg = Message()
    msg.info('test')
    """
    def __init__(self, loglevel=None, color=None, end_color=config.ENDCOLOR):
        """
        Initialization
        """
        self.loglevel = loglevel
        self.color = color
        self.end_color = end_color

    def info(self, message) -> str:
        """
        Returning a message of type INFO
        """
        self.loglevel = '[INFO]'
        self.color = config.BLUE
        return print(self.color, ts(), self.loglevel, message, self.end_color)

    def ok(self, message) -> str:
        """
        Returning a message of type OK
        """
        self.loglevel = '[OK]'
        self.color = config.GREEN
        return print(self.color, ts(), self.loglevel, message, self.end_color)

    def warn(self, message) -> str:
        """
        Returning a message of type WARN
        """
        self.loglevel = '[WARN]'
        self.color = config.YELLOW
        return print(self.color, ts(), self.loglevel, message, self.end_color)

    def error(self, message) -> str:
        """
        Returning a message of type ERROR
        """
        self.loglevel = '[ERROR]'
        self.color = config.RED
        return print(self.color, ts(), self.loglevel, message, self.end_color)
