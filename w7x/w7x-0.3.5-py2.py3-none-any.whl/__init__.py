"""Top-level package of w7x."""

__author__ = """Daniel Böckenhoff"""
__email__ = "dboe@ipp.mpg.de"
__version__ = "0.3.5"

from . import compatibility

# from . import simulation
# from . import diagnostic
from .switches import distribute, stateful, exposed
from . import core
from . import model
from . import config
from . import lib
from . import plotting

from .state import (
    State,
    StateComponent,
    StateComposite,
    StateLeaf,
)
from .core import (
    node,
    dependencies,
    compute,
    start_scheduler,
)
