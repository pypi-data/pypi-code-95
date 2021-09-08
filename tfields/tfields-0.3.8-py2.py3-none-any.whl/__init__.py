# flake8: noqa: F401
"""Top-level package of tfields.
TODO: proper documentation, also in dough.
"""

__author__ = """Daniel Böckenhoff"""
__email__ = "dboe@ipp.mpg.de"
__version__ = "0.3.8"

# methods:
from tfields.core import dim, rank
from tfields.mask import evalf

# classes:
from tfields.core import Tensors, TensorFields, TensorMaps, Container, Maps
from tfields.tensor_grid import TensorGrid
from tfields.points_3d import Points3D
from tfields.mesh_3d import Mesh3D
from tfields.triangles_3d import Triangles3D
from tfields.planes_3d import Planes3D
from tfields.bounding_box import Node
