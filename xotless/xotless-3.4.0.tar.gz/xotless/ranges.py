#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from dataclasses import dataclass
from enum import Enum
from typing import Generic, List, Optional, Tuple, Type, TypeVar

from xotl.tools.infinity import Infinity
from xotl.tools.symbols import Undefined

from .types import EqTypeClass, OrdTypeClass

TEq = TypeVar("TEq", bound=EqTypeClass)
TOrd = TypeVar("TOrd", bound=OrdTypeClass)


@dataclass(init=False)
class Range(Generic[TOrd]):
    """A range containing values between `lowerbound` and `upperbound`.

    Boundaries can be instances of `Included`:class: or `Excluded`:class:

    Ranges are classified in four `kinds <Range.kind>`:any: according to the
    type of the boundaries.  You can use the four classmethods to build each,
    or you can create the boundaries yourself.

    ===================    =================      ======================
    Lower boundary         Upper boundary         Constructor
    ===================    =================      ======================
    Included               Included               `new_closed`:func:
    Included               Excluded               `new_open_right`:func:
    Excluded               Included               `new_open_left`:func:
    Excluded               Excluded               `new_open`:func:
    ===================    =================      ======================

    In any of the constructors, if `lowerbound` is None, the range's lower
    bound is ``Excluded(-Infinity)``.  If `upperbound` is None, the range's
    upper bound is ``Excluded(Infinity)``.

    Ranges are iterable.  They yield exactly two times: the lower bound and
    the upperbound.  This makes it easy to unpack calling signatures that
    doesn't take ranges but the boundaries.

    Calling `bool` on ranges return True when the range is not empty.

    """

    _lower: "Bound[TOrd]"
    _upper: "Bound[TOrd]"

    __slots__ = ("_lower", "_upper")

    @property
    def lowerbound(self) -> TOrd:
        return self._lower.bound

    @property
    def upperbound(self) -> TOrd:
        return self._upper.bound

    @classmethod
    def new_closed(
        cls, lowerbound: Optional[TOrd], upperbound: Optional[TOrd]
    ) -> "Range[TOrd]":
        """Return a closed range if both boundaries allow it.

        If any of the boundaries is None, or an Infinity value, the result
        will be actually an open or semi-open range.

        """
        lb = Bound.normalized_lower_bound(lowerbound, Included)
        ub = Bound.normalized_upper_bound(upperbound, Included)
        return Range(lb, ub)

    @classmethod
    def new_open(
        cls, lowerbound: Optional[TOrd], upperbound: Optional[TOrd]
    ) -> "Range[TOrd]":
        """Return an open range."""
        lb = Bound.normalized_lower_bound(lowerbound, Excluded)
        ub = Bound.normalized_upper_bound(upperbound, Excluded)
        return Range(lb, ub)

    @classmethod
    def new_open_left(
        cls, lowerbound: Optional[TOrd], upperbound: Optional[TOrd]
    ) -> "Range[TOrd]":
        """Return a range open on the lower boundary and possibly closed in the upper boundary."""
        lb = Bound.normalized_lower_bound(lowerbound, Excluded)
        ub = Bound.normalized_upper_bound(upperbound, Included)
        return Range(lb, ub)

    @classmethod
    def new_open_right(
        cls, lowerbound: Optional[TOrd], upperbound: Optional[TOrd]
    ) -> "Range[TOrd]":
        """Return a range possibly closed on the lower boundary and open in the upper boundary."""
        lb = Bound.normalized_lower_bound(lowerbound, Included)
        ub = Bound.normalized_upper_bound(upperbound, Excluded)
        return Range(lb, ub)

    def __init__(
        self, lowerbound: "Bound[TOrd]", upperbound: "Bound[TOrd]"
    ) -> None:
        lowerbound = (
            lowerbound if lowerbound is not None else Excluded(-Infinity)
        )
        upperbound = (
            upperbound if upperbound is not None else Excluded(Infinity)
        )
        if not isinstance(lowerbound, Bound):
            raise ValueError(
                f"lowerbound ({lowerbound}) is not of type Excluded(), Included() or Unbounded()"
            )
        if not isinstance(upperbound, Bound):
            raise ValueError(
                f"Upperbound ({upperbound}) is not of type Excluded(), Included() or Unbounded()"
            )
        if not lowerbound.bound <= upperbound.bound:
            raise ValueError(f"not {lowerbound} <= {upperbound}")
        if lowerbound.bound == upperbound.bound:
            # Normalize the case of empty range.  All empty ranges will be
            # normalized to Range(Excluded(x), Excluded(x))
            if isinstance(lowerbound, Excluded):
                upperbound = Excluded(upperbound.bound)
            elif isinstance(upperbound, Excluded):
                lowerbound = Excluded(lowerbound.bound)
        self._lower = lowerbound
        self._upper = upperbound

    def __repr__(self):
        return f"Range({self._lower!r}, {self._upper!r})"

    def lift(self):  # pragma: no cover
        "Return the `~xotless.domains.IntervalSet`:class: containing only `self`."
        from .domains import IntervalSet

        return IntervalSet([self])

    def __iter__(self):
        yield self.lowerbound
        yield self.upperbound

    def __bool__(self):
        "True if and only if not empty"
        return not self.empty

    @property
    def empty(self):
        """True if and only if empty"""
        return self.lowerbound == self.upperbound and (
            isinstance(self._lower, Excluded)
            or isinstance(self._upper, Excluded)
        )

    def __contains__(self, value):
        """True if `values` is a member."""
        if self.kind == RangeKind.CLOSED:
            return self.lowerbound <= value <= self.upperbound
        elif self.kind == RangeKind.OPEN:
            return self.lowerbound < value < self.upperbound
        elif self.kind == RangeKind.OPEN_RIGHT:
            return self.lowerbound <= value < self.upperbound
        else:
            assert self.kind == RangeKind.OPEN_LEFT
            return self.lowerbound < value <= self.upperbound

    @property
    def bound(self) -> bool:
        """True if neither boundary is unbounded."""
        return bool(self._lower) and bool(self._upper)

    def diff(self, other: "Range") -> Tuple["Range", ...]:
        """The difference of self from other.

        The result is two ranges that jointly have all the values in self,
        that are not in other.  We need two value of Range because the
        difference is not necessarily a range, but can be fully capture but
        the union of two possibly empty ranges.

        """
        other = self & other
        if self == other:
            return ()
        elif other:
            assert self > other
            res: Tuple[Range[TOrd], ...] = ()
            before = Range(self._lower, ~other._lower)
            if before:
                res += (before,)
            after = Range(~other._upper, self._upper)
            if after:
                res += (after,)
            return res
        else:
            return (self,)

    def _merge_with(self, other: "Range") -> None:
        """Merge an overlapping `other` into self.

        Modify `self` in-place (thus breaking the immutability property) so
        that it becomes the union of `self` and `other`.  It's only valid if
        `self` overlaps with `other`.

        """
        assert self & other or (
            self.upperbound == other.lowerbound
            and (
                isinstance(self._upper, Included)
                or isinstance(other._lower, Included)
            )
        ), f"Cannot merge {self} and {other}"

        # The join of a `Excluded(a)` bound with `Included(a)` bound
        # must allways include a despite the order.
        # So we need find the max and min `bound` and `type`.
        self._lower = min(
            self._lower, other._lower, key=_max_key_by_bound_and_type
        )
        self._upper = max(
            self._upper, other._upper, key=_min_key_by_bound_and_type
        )

    def join(*ranges_: "Range[TOrd]") -> Tuple["Range[TOrd]", ...]:
        """Return several disjoint ranges that describe the union of `ranges`."""
        # The join of `Range(Excluded(a), b)` with `Range(Included(a),
        # c)` must include a despite the order.  So we need order by
        # lowerbound and type.
        ranges = sorted((r for r in ranges_ if r), key=_by_lowerbound_and_type)
        result: List[Range] = []
        for next_ in ranges:
            if not result:
                # Don't use the same object since we can modify it with
                # _merge_with.
                result.append(Range(next_._lower, next_._upper))
            else:
                current = result[-1]
                # We have to implement a softer version of __and__ because if
                # r1 = Range(a, b) and r2 = Range(b, c) are disjoint then:
                #
                #              r1 and r2 can be merged to Range(a,c) if:
                #           =============================================
                # r1 = Range(Bound(a), Excluded(b)) or r1 = Range(Bound(a), Included(b))
                # r2 = Range(Included(b), Bound(c)) or r2 = Range(Excluded(b), Bound(c))
                #
                #                  r1 and r2 can't be merged if:
                #         =============================================
                #                   Range(Bound(a), Excluded(b))
                #                   Range(Excluded(b), Bound(c))
                #
                if current & next_ or (
                    current.upperbound == next_.lowerbound
                    and current._upper != next_._lower
                ):
                    current._merge_with(next_)
                else:
                    result.append(Range(next_._lower, next_._upper))
        if result:
            return tuple(result)
        else:
            return ()

    def __and__(self, other: "Range") -> "Range":
        """Get the intersection of self and other."""
        if not isinstance(other, Range):
            return NotImplemented
        lower = max(self._lower, other._lower, key=_max_key_by_bound_and_type)
        upper = min(self._upper, other._upper, key=_min_key_by_bound_and_type)
        if lower.bound <= upper.bound:
            return Range(lower, upper)
        else:
            # empty set in the min value; we need to make Excluded explicit
            return Range(Excluded(upper.bound), Excluded(upper.bound))

    def __eq__(self, other):
        """True if `self` is equal to `other`.

        There are many representations for the empty range, all are equal:

           >>> Range.new_open(0, 0) == Range.new_open(1, 1)
           True

        """
        if not isinstance(other, Range):
            return NotImplemented
        # There are many possible ways to represent the empty range:
        #
        # - Range(Excluded(x), Excluded(x)),
        # - Range(Included(x), Excluded(x)),
        # - Range(Excluded(x), Included(x))
        #
        # for every value of x; but they're all equal.
        if self.empty and other.empty:
            return True
        return self._lower == other._lower and self._upper == other._upper

    def __hash__(self):
        # Since all empty ranges are equal, all Range(x, x) must hash the
        # same.  So, we hash'em all the same as (Undefined, Undefined).
        if self:
            return hash((self._lower, self._upper))
        else:
            return hash((Undefined, Undefined))

    def __le__(self, other: "Range") -> bool:  # pragma: no cover
        "True if self is a sub-range of other"
        try:
            return self == (self & other)
        except TypeError:
            return NotImplemented

    def __lt__(self, other: "Range") -> bool:  # pragma: no cover
        "True is self is a proper sub-range of other"
        try:
            return self != other and self <= other
        except TypeError:
            return NotImplemented

    def __ge__(self, other: "Range") -> bool:  # pragma: no cover
        "True is self is a super-range of other"
        try:
            return (self & other) == other
        except TypeError:
            return NotImplemented

    def __gt__(self, other: "Range") -> bool:  # pragma: no cover
        "True is self is a proper super-range of other"
        try:
            return self != other and self >= other
        except TypeError:
            return NotImplemented

    @property
    def sample(self) -> Optional[TOrd]:
        """Return a member of the range.  Return None if the range is empty or OPEN."""
        if self.empty or self.kind == RangeKind.OPEN:
            # There's no general way to get a sample from an OPEN range.
            return None
        if isinstance(self._lower, Included):
            return self.lowerbound
        else:
            assert isinstance(self._upper, Included)
            return self.upperbound

    @property
    def kind(self) -> "RangeKind":
        "The kind of the range."
        if isinstance(self._lower, Included) and isinstance(
            self._upper, Excluded
        ):
            return RangeKind.OPEN_RIGHT
        elif isinstance(self._lower, Included) and isinstance(
            self._upper, Included
        ):
            return RangeKind.CLOSED
        elif isinstance(self._lower, Excluded) and isinstance(
            self._upper, Excluded
        ):
            return RangeKind.OPEN
        else:
            assert isinstance(self._lower, Excluded) and isinstance(
                self._upper, Included
            )
            return RangeKind.OPEN_LEFT

    def __str__(self):
        return f"Range({self._lower!s}, {self._upper!s})"


@dataclass(unsafe_hash=True, order=True)
class Bound(Generic[TOrd]):
    """A boundary condition to be used in Range.

    You must use instances of `Included`:class: or `Excluded`:class:.  Calling
    `bool`:func: on instances of Included always return True.  Calling
    `bool`:func: on instances of Excluded return True when the boundary is
    neither `~xotl.tools.infinity.Infinity`:data: nor -Infinity.

    """

    bound: TOrd

    @classmethod
    def normalized_upper_bound(
        cls, bound: Optional[TOrd], Boundary: Type["Bound[TOrd]"]
    ) -> "Bound[TOrd]":
        """Return a normalized instance of Boundary for the upper bound of Range.

        If `bound` is either None, False, Infinity or -Infinity, return
        ``Excluded(Infinity)``; otherwise return ``Boundary(bound)``.

        """
        assert Boundary is Included or Boundary is Excluded
        assert not isinstance(bound, Bound)
        if bound is None or bound is False or isinstance(bound, type(Infinity)):
            return Excluded(Infinity)
        else:
            return Boundary(bound)

    @classmethod
    def normalized_lower_bound(
        cls, bound: Optional[TOrd], Boundary: Type["Bound[TOrd]"]
    ) -> "Bound[TOrd]":
        """Return a normalized instance of Boundary for the upper bound of Range.

        If `bound` is either None, False, Infinity or -Infinity, return
        ``Excluded(-Infinity)``; otherwise return ``Boundary(bound)``.

        """
        assert Boundary is Included or Boundary is Excluded
        assert not isinstance(bound, Bound)
        if bound is None or bound is False or isinstance(bound, type(Infinity)):
            return Excluded(-Infinity)
        else:
            return Boundary(bound)

    def __invert__(self) -> "Bound[TOrd]":
        ...


class Included(Bound):
    "An included boundary in a `Range`:class:."

    def __init__(self, bound: TOrd) -> None:
        assert bound is not -Infinity and bound is not Infinity
        assert bound is not None and bound is not False
        super().__init__(bound)

    @classmethod
    def safer_new(cls, bound: TOrd) -> "Bound[TOrd]":
        """Try to safely create an Included boundary, falling back to
        `Excluded`:class: for infinite marks.

        """
        if bound is Infinity or bound is -Infinity:
            return Excluded(bound)
        else:
            return cls(bound)

    def __bool__(self):
        return True

    def __repr__(self):
        return f"Included({self.bound!r})"

    def __str__(self):
        return f"={self.bound!s}"

    def __invert__(self):
        return Excluded(self.bound)


class Excluded(Bound):
    "An excluded boundary in a `Range`:class:"

    def __bool__(self):
        if self.bound in (Infinity, -Infinity):
            return False
        else:
            return True

    def __repr__(self):
        return f"Excluded({self.bound!r})"

    def __str__(self):
        return f"≠{self.bound!s}"

    def __invert__(self):
        if self.bound not in (Infinity, -Infinity):
            return Included(self.bound)
        else:
            return self


class RangeKind(Enum):
    """The four kinds of ranges"""

    OPEN_RIGHT = "{lb <= a < ub}"
    OPEN_LEFT = "{lb < a <= ub}"
    CLOSED = "{lb <= a <= ub}"
    OPEN = "{lb < a < ub}"


def _max_key_by_bound_and_type(boundary: Bound[TOrd]) -> Tuple[TOrd, int]:
    """Return a tuple of `(bound, -1 or 1)`.

    The second component is -1 if the boundary is Included, and 1 if Excluded.
    This has the nice property of ordering same-boundary Included *before*
    Excluded.  So:

    >>> max(Included(0), Excluded(0), key=_max_key_by_bound_and_type)
    Excluded(0)

    """
    return (boundary.bound, -1 if isinstance(boundary, Included) else 1)


def _min_key_by_bound_and_type(boundary: Bound[TOrd]) -> Tuple[TOrd, int]:
    """Return a tuple of `(bound, -1 or 1)`.

    This is the same as _max_key_by_bound_and_type but negating the second
    component of the result.

    >>> min(Included(0), Excluded(0), key=_min_key_by_bound_and_type)
    Excluded(0)

    """
    bound, order = _max_key_by_bound_and_type(boundary)
    return bound, -order


def _by_lowerbound_and_type(r: Range[TOrd]) -> Tuple[TOrd, int]:
    return _max_key_by_bound_and_type(r._lower)
