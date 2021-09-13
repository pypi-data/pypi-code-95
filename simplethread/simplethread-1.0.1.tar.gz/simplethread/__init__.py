"""
Some useful utilities for Python's ``threading`` module.
"""

from typing import Final, Tuple

from simplethread.decorators import AnyFunc
from simplethread.decorators import synchronized
from simplethread.decorators import threaded

__all__: Final[Tuple[str, ...]] = ("AnyFunc", "synchronized", "threaded")

__version__: Final[str] = "1.0.1"
