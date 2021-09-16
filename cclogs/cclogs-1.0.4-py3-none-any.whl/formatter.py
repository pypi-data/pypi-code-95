import logging
import sys
from logging import LogRecord

from .extras import ColorMethod, default_colors, TerminalColors

_styles = {
    "%": ("%(levelname)s", "%(message)s"),
    "{": ("{levelname}", "{message}"),
    "$": ("${levelname}", "${message}"),
}


class ColorFormatter(logging.Formatter):

    def __init__(self, fmt=None, color_mode: ColorMethod = ColorMethod.LEVEL, datefmt=None, style='%', validate=True):
        if sys.version_info[0] == 3:
            if sys.version_info[1] < 8:
                super().__init__(fmt, datefmt, style)
            else:
                super().__init__(fmt, datefmt, style, validate)
        else:
            raise RuntimeError("Requires python 3.6 or higher")
        self._color_mode = color_mode
        self._colors = default_colors
        self._level_str = _styles[style][0]
        self._message_str = _styles[style][1]
        self._original_fmt = self._fmt

    def setMode(self, mode: ColorMethod):
        self._color_mode = mode

    def format(self, record: LogRecord) -> str:
        if self._color_mode == ColorMethod.NO_COLOR:
            return super().format(record)
        elif self._color_mode == ColorMethod.ALL:
            color_str = self._colors.get(record.levelno, TerminalColors.NO_COLOR).value
            return color_str + super().format(record) + TerminalColors.NO_COLOR.value
        elif self._color_mode == ColorMethod.LEVEL:
            msg = self._reformat_message(self._level_str, record)
            return msg
        elif self._color_mode == ColorMethod.MESSAGE:
            msg = self._reformat_message(self._message_str, record)
            return msg

    def setLevelColor(self, level: int, color: TerminalColors):
        self._colors[level] = color

    def _reformat_message(self, param: str, record: LogRecord):
        color_str = self._colors.get(record.levelno, TerminalColors.NO_COLOR).value
        # original_fmt = self._style._fmt
        self._style._fmt = self._original_fmt.replace(param, color_str + param + TerminalColors.NO_COLOR.value)
        msg = super().format(record)
        self._style._fmt = self._original_fmt
        return msg
