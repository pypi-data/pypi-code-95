from enum import Enum

import logging


class LogLevel(Enum):
    '''
    What the stdlib did not provide!
    '''
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR
    NOTSET = logging.NOTSET
    WARNING = logging.WARNING
    CRITICAL = logging.CRITICAL

    def __str__(self):
        return self.name

    @staticmethod
    def items():
        return list(map(lambda c: c, LogLevel))
