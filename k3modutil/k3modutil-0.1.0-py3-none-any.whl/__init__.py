"""
Submodule Utilities.

"""

# from .proc import CalledProcessError
# from .proc import ProcError

__version__ = "0.1.0"
__name__ = "k3modutil"

from .modutil import (
    submodules,
    submodule_tree,
    submodule_leaf_tree,
)

__all__ = [
    "submodules",
    "submodule_tree",
    "submodule_leaf_tree",
]
