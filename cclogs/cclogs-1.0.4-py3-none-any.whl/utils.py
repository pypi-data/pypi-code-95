import logging
import sys

from .extras import ColorMethod
from .handler import ColoredStreamHandler


def set_root_logger(level: int, fmt: str = "%(levelname)s - %(message)s",
                    color_mode: ColorMethod = ColorMethod.LEVEL):
    r = logging.root
    r.setLevel(level)
    for h in r.handlers:
        r.removeHandler(h)
    c_handler = ColoredStreamHandler(sys.stdout, color_mode, fmt)
    c_handler.setLevel(level)
    r.addHandler(c_handler)
