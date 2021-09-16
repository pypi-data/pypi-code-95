# flake8: noqa
# TODO: re-add to flake8
from abc import ABC
from abc import abstractmethod
from typing import Final
from typing import Optional
from typing import TypeVar

from ..core import Space


class Euclidean(Space):
    """An abstract containing functions which are common to euclidean spaces."""

    dim: int


class Euclidean1d(Euclidean):
    """1D euclidean space.

    Euclidean1D is a sub-class of Euclidean, because any edge that can go from a N-dim Euclidean
    frame can also go from a 1D Euclidean frame.

    """

    dim = 1


class Euclidean2d(Euclidean):
    dim = 2


class Euclidean3d(Euclidean):
    dim = 3
