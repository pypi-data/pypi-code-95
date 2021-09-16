import logging
import sys
from logging import Formatter

from .extras import ColorMethod, TerminalColors
from .formatter import ColorFormatter


class ColoredStreamHandler(logging.StreamHandler):

    def __init__(self, stream=sys.stdout, mode: ColorMethod = ColorMethod.LEVEL,
                 fmt: str = "%(levelname)s - %(message)s") -> None:
        super().__init__(stream)
        self._mode = mode
        self.formatter: ColorFormatter = ColorFormatter(fmt, mode)

    def setFormatter(self, fmt: Formatter) -> None:
        super().setFormatter(fmt)

    def setColorMode(self, color_mode: ColorMethod):
        if type(self.formatter) == ColorFormatter:
            self.formatter.setMode(color_mode)

    def setLevelColor(self, level: int, color: TerminalColors) -> None:
        if type(self.formatter) == ColorFormatter:
            self.formatter.setLevelColor(level, color)
