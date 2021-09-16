import logging
from enum import Enum


class ColorMethod(Enum):
    NO_COLOR = 0
    LEVEL = 1
    MESSAGE = 2
    ALL = 3


class TerminalColors(Enum):
    NO_COLOR = "\x1b[0m"
    BLACK = "\x1b[30m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    LIGHT_GRAY = "\x1b[37m"
    DARK_GRAY = "\x1b[90m"
    LIGHT_RED = "\x1b[91m"
    LIGHT_GREEN = "\x1b[92m"
    LIGHT_YELLOW = "\x1b[93m"
    LIGHT_BLUE = "\x1b[94m"
    LIGHT_MAGENTA = "\x1b[95m"
    LIGHT_CYAN = "\x1b[96m"
    WHITE = "\x1b[97m"


default_colors = {
    logging.NOTSET: TerminalColors.NO_COLOR,
    logging.DEBUG: TerminalColors.BLUE,
    logging.INFO: TerminalColors.GREEN,
    logging.WARNING: TerminalColors.YELLOW,
    logging.ERROR: TerminalColors.RED,
    logging.CRITICAL: TerminalColors.MAGENTA
}
