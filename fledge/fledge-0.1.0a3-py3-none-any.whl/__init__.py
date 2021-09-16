"""Fledge: Spatial Programming with Reference Graphs."""
from importlib.metadata import version

from .core import Body
from .core import Edge
from .core import Frame
from .core import get_graph
from .core import get_projection
from .core import get_space
from .core import Identity
from .core import Node
from .core import Projection
from .core import Reference
from .core import show
from .core import Space
from .core import Transform

__version__ = version(__name__)


__all__ = [
    "get_space",
    "get_projection",
    "Space",
    "Node",
    "Frame",
    "Body",
    "Edge",
    "Identity",
    "Reference",
    "Transform",
    "Projection",
    "get_graph",
    "show",
    "__version__",
]
