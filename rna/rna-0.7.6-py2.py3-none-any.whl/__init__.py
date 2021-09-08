"""Top-level package of rna."""

__author__ = """Daniel Böckenhoff"""
__email__ = "dboe@ipp.mpg.de"
__version__ = "0.7.6"

from . import log  # NOQA
from . import path  # NOQA
from . import process  # NOQA
from . import parsing  # NOQA
from . import pattern  # NOQA
from . import polymorphism  # NOQA
from . import plotting

plotting.use("matplotlib")  # TODO: remove
