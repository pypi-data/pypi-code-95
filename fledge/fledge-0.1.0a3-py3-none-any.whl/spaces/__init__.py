"""Spaces."""
from ..core import Space
from .euclidean import Euclidean
from .euclidean import Euclidean1d
from .euclidean import Euclidean2d
from .euclidean import Euclidean3d

__all__ = ["Space", "Euclidean", "Euclidean1d", "Euclidean2d", "Euclidean3d"]
