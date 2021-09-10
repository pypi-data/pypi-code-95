# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import logging
import sys

try:
    import colorlog
    color_available = True
except ModuleNotFoundError:
    color_available = False


class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        self.max_level = max_level
        super().__init__()

    def filter(self, record):
        return record.levelno < self.max_level


def create_logger(log_level, colored=False):
    logger = logging.getLogger('upt')
    logger.setLevel(log_level or logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.addFilter(MaxLevelFilter(logging.ERROR))
    logger.addHandler(stdout_handler)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    logger.addHandler(stderr_handler)

    if colored and not color_available:
        logger.colored = False
        logger_set_formatter(logger, 'upt')
        logger.warning('You requested colored logs, but the colorlog module '
                       'could not be found. Switching to black and white '
                       'logs.')
    else:
        logger.colored = colored

    return logger


def logger_set_formatter(logger, name):
    log_format = f'[%(levelname)-8s] [{name}] %(message)s'
    if logger.colored:
        formatter = colorlog.ColoredFormatter(f'%(log_color)s {log_format}')
    else:
        formatter = logging.Formatter(log_format)
    for handler in logger.handlers:
        handler.setFormatter(formatter)
