# type: ignore[attr-defined]
"""Wrapper for interacting with Nanowire platform"""
from .types import *
from .service import *
from .utils import *

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
