#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# copyright (c) merchise autrement [~º/~] and contributors
# all rights reserved.
#
# this is free software; you can do what the licence file allows you to.
#
"""Implements trees for efficient searching.


"""
import operator
from dataclasses import dataclass
from itertools import takewhile
from typing import Generic, Iterator, Optional, Sequence, Tuple, TypeVar, cast

from xotl.tools.infinity import Infinity

from .ranges import Range, TOrd

T = TypeVar("T")


@dataclass(init=False, unsafe_hash=True)
class Cell(Generic[T, TOrd]):
    """A data-carrying open-right range."""

    # NB: Introducing any kind of Range here entails modifications to the
    # algorithms below.
    lowerbound: TOrd
    upperbound: TOrd
    data: T

    __slots__ = ("lowerbound", "upperbound", "data")

    def __init__(
        self, lower: Optional[TOrd], upper: Optional[TOrd], data: T
    ) -> None:
        self.lowerbound = cast(TOrd, -Infinity if lower is None else lower)
        self.upperbound = cast(TOrd, Infinity if upper is None else upper)
        self.data = data

    @classmethod
    def from_bounds(
        cls, lower: Optional[TOrd], upper: Optional[TOrd], data: T
    ) -> "Cell[T, TOrd]":  # pragma: no cover
        """Return a cell from the boundaries of an open-right range."""
        return cls(lower, upper, data)

    @classmethod
    def from_range(cls, r: Range[TOrd], data: T) -> "Cell[T, TOrd]":
        """Return a cell casting `r` to an open-right range.

        .. note:: We disregard the kind of range, cells are always open-right.

        """
        return cls(r.lowerbound, r.upperbound, data)

    def __contains__(self, which):  # pragma: no cover
        return self.lowerbound <= which < self.upperbound

    def __bool__(self) -> bool:  # pragma: no cover
        return self.lowerbound < self.upperbound


@dataclass
class IntervalTree(Generic[T, TOrd]):
    """A data-containing generic IntervalTree.

    See section 10.1 of [deBerg2008]_.

    The intervals are allowed over any type `TOrd` (i.e, for which `<=` is
    defined and total).

    The `cells` can contain any type of data.

    You shouldn't mutate any of the internal attributes.  The API is just the
    class method `from_cells` and then getting the cells containing a point
    the with either `get` of `__getitem__`.

    .. [deBerg2008] Mark de Berg, et al. *Computational Geometry. Algorithms
       and Applications. Third Edition*. Springer Verlag. 2008.

    """

    center: Optional[TOrd]
    cells: Sequence[Cell[T, TOrd]]  # Ordered by lowerbound
    cells_by_upper: Sequence[Cell[T, TOrd]]  # Ordered in reverse by upperbound.
    left: Optional["IntervalTree"]
    right: Optional["IntervalTree"]

    __slots__ = ("center", "cells", "cells_by_upper", "left", "right")

    @classmethod
    def from_cells(cls, cells: Sequence[Cell[T, TOrd]]) -> "IntervalTree":
        return cls._from_sorted_cells(
            sorted(tuple(cell for cell in cells if cell), key=_getlower)
        )

    def __bool__(self) -> bool:
        return bool(self.cells)

    def __contains__(self, which: TOrd):
        return any(which in cell for cell in self.cells)

    @classmethod
    def _from_sorted_cells(
        cls, cells: Sequence[Cell[T, TOrd]]
    ) -> "IntervalTree[T, TOrd]":
        left_cells = []
        middle_cells = []
        right_cells = []
        if cells:
            middle = len(cells) // 2
            middle_cell = cells[middle]
            center: Optional[TOrd] = middle_cell.lowerbound
            for cell in cells:
                if cell.upperbound <= center:
                    left_cells.append(cell)
                elif center < cell.lowerbound:
                    right_cells.append(cell)
                else:
                    assert center in cell
                    middle_cells.append(cell)
        else:
            center = None
        result = cls(
            center=center,
            cells=tuple(middle_cells),
            cells_by_upper=tuple(
                sorted(middle_cells, key=_getupper, reverse=True)
            ),
            left=cls._from_sorted_cells(left_cells) if left_cells else None,
            right=cls._from_sorted_cells(right_cells) if right_cells else None,
        )
        return result

    def __getitem__(self, which: TOrd) -> Tuple[Cell[T, TOrd], ...]:
        """Return all cells that contains the given item."""
        result = self.get(which)
        if not result:
            raise KeyError(which)
        return result

    def get(self, query: TOrd) -> Tuple[Cell[T, TOrd], ...]:
        return tuple(self.iter_get(query))

    def iter_get(self, query: TOrd) -> Iterator[Cell[T, TOrd]]:
        if not self:
            return
        if query <= self.center:
            # Since self.cells is ordered by lowerbound, only *the first*
            # cells for which the lowerbound is less or equal to the query
            # contain the queried value.  Looking any further won't find any
            # match.
            #
            # See page 222 of [deBerg2008].
            yield from takewhile(lambda c: c.lowerbound <= query, self.cells)
        else:
            # The same as before but with `cells_by_upper`.
            yield from takewhile(
                lambda c: query < c.upperbound, self.cells_by_upper
            )
        if query < self.center and self.left:
            yield from self.left.get(query)
        elif query > self.center and self.right:
            yield from self.right.get(query)

    @property
    def depth(self):
        "The depth of the IntervalTree."
        return 1 + max(
            left.depth if (left := self.left) is not None else 0,
            right.depth if (right := self.right) is not None else 0,
        )


_getlower = operator.attrgetter("lowerbound")
_getupper = operator.attrgetter("upperbound")
