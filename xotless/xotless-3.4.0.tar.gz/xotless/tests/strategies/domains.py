#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import datetime
import operator
from functools import reduce
from typing import List, Sequence

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from xotl.tools.infinity import Infinity
from xotl.tools.objects import DelegatedAttribute

from ...domains import EquivalenceSet, IntervalSet, TOrd
from ...ranges import Excluded, Included, Range

# Notice that floats have a maximum.  At the time of writing::
#    >>> l=9007199254740992.0
#    >>> l == l + 1   # Really?!!
#    True
#
# Since we create ranges like Range(lower, lower + delta), let's put a cap on
# the following generators so that generated ranges have a sensible and
# predictable behavior.
numbers = st.floats(
    allow_infinity=False, allow_nan=False, min_value=-10000.0, max_value=10000.0
)
nonnegative_numbers = st.floats(
    allow_infinity=False, allow_nan=False, min_value=0, max_value=10000.0
)
negative_numbers = st.floats(
    allow_infinity=False, allow_nan=False, min_value=-10000.0, max_value=-1
)
positive_numbers = st.floats(
    allow_infinity=False, allow_nan=False, min_value=1, max_value=10000.0
)


equivalence_sets: SearchStrategy[EquivalenceSet[int]] = st.frozensets(
    st.integers()
).map(EquivalenceSet)
non_empty_equivalence_sets: SearchStrategy[EquivalenceSet[int]] = st.frozensets(
    st.integers(), min_size=1
).map(EquivalenceSet)
st.register_type_strategy(EquivalenceSet, equivalence_sets)

type_of_bounds = st.sampled_from([Included.safer_new, Excluded])

range_constructors = st.sampled_from(
    [
        Range.new_open_right,
        Range.new_open_left,
        Range.new_closed,
        Range.new_open,
    ]
)


def float_ranges(inner=None, outer=None, *, kinds=None):
    """Generate instances of Range[float].

    If `inner` is not None, it must be a Range[float], and all generated
    ranges will be super-sets of `inner`.

    If `outer` is not None, it must be a Range[float], and all generated
    ranges will be sub-sets of `outer`.

    If `kinds` is not None, it must a strategy which constructors of ranges
    for the kind you want.  If None, we produce any kind of range.

    """
    return generalized_ranges(
        inner, outer, RangeType=FloatRangeHelper, kinds=kinds
    )


def date_ranges(inner=None, outer=None, *, kinds=None):
    """Generate instances of Range[datetime].

    If `inner` is not None, it must be a Range[datetime], and all generated
    ranges will be super-sets of `inner`.

    If `outer` is not None, it must be a Range[datetime], and all generated
    ranges will be sub-sets of `outer`.

    If `kinds` is not None, it must a strategy which constructors of ranges
    for the kind you want.  If None, we produce any kind of range.

    """
    return generalized_ranges(
        inner, outer, RangeType=DateRangeHelper, kinds=kinds
    )


def members_of_float_ranges(first_range, *other_ranges):
    """Generates members of any of the ranges passed."""
    ranges = [range_ for range_ in (first_range,) + other_ranges if range_]
    if not ranges:
        raise ValueError("At least a range must be non-empty")
    return reduce(
        operator.or_, (get_float_member_strategy(range_) for range_ in ranges)
    )


def members_of_date_ranges(first_range, *other_ranges):
    """Generates members of any of the ranges passed."""
    ranges = [range_ for range_ in (first_range,) + other_ranges if range_]
    if not ranges:
        raise ValueError("At least a range must be non-empty")
    return reduce(
        operator.or_, (get_date_member_strategy(range_) for range_ in ranges)
    )


def many_float_ranges(n=2, outer=None):
    """Generates `n` ranges in a tuple.

    Ranges are ordered by lowerbound (except empty ranges which have no
    particular ordering key).

    There's no overlapping of generated ranges, nor there's a gap between
    consecutive ones.  No empty ranges are generated.

    If `outer` is not None, all ranges will be contained within this `outer`
    range.  The join of all ranges doesn't necessarily cover the entirety of
    `outer`.

    """
    if outer is None:
        outer = Range.new_open_right(
            FloatRangeHelper.LOWER_LIMIT, FloatRangeHelper.UPPER_LIMIT
        )
    if not outer:
        raise ValueError(f"Cannot generate many ranges within {outer!r}")
    assert n >= 0, f"Invalid value for n: {n}"
    if not n:
        return st.just(())
    # To define n consecutive, non-overlapping ranges we need n + 1 *points*
    # which are members of outer.
    return st.lists(
        get_float_member_strategy(outer, allow_upper=True),
        min_size=n + 1,
        max_size=n + 1,
        unique=lambda x: x,
    ).map(_build_ranges)


def many_date_ranges(n=2, outer=None):
    "Just like many_ranges but generates ranges over dates."
    if outer is None:
        outer = Range.new_open_right(
            DateRangeHelper.LOWER_LIMIT, DateRangeHelper.UPPER_LIMIT
        )
    if not outer:
        raise ValueError(f"Cannot generate many ranges within {outer!r}")
    assert n >= 0, f"Invalid value for n: {n}"
    if not n:
        return st.just(())
    # To define n consecutive, non-overlapping ranges we need n + 1 *points*
    # which are members of outer.
    return st.lists(
        get_date_member_strategy(outer, allow_upper=True),
        min_size=n + 1,
        max_size=n + 1,
        unique=lambda x: x,
    ).map(_build_ranges)


def _build_ranges(points: Sequence[TOrd]) -> Sequence[Range[TOrd]]:
    lower, upper, *points = sorted(points)
    res: List[Range[TOrd]] = [Range.new_open_right(lower, upper)]
    for point in points:
        lower = res[-1].upperbound
        res.append(Range.new_open_right(lower, point))
    return tuple(res)


def float_intervals(min_bases=0, max_bases=None, outer=None):
    """Generates instances of IntervalSet[float].

    If `min_bases` is not 0, we guarantee that the generated intervals will
    have at least min_bases non-empty ranges.  If `min_bases` is 0 the
    intervals may be empty.  If `max_bases` is None, it will default to twice
    the value of `min_bases` (or DEFAULT_MAX_BASES, if `min_bases` is 0).

    If `outer` is not None, the bases of the interval will all be contained
    with `outer`.

    See `many_float_ranges`:func:.

    """
    return generalized_intervals(
        min_bases=min_bases,
        max_bases=max_bases,
        outer=outer,
        many_typed_ranges=many_date_ranges,
    )


def date_intervals(min_bases=0, max_bases=10, outer=None):
    """Generates instances of IntervalSet[datetime].

    The meaning of parameters is the same as in `float_intervals`:func:.

    """
    return generalized_intervals(
        min_bases=min_bases,
        max_bases=max_bases,
        outer=outer,
        many_typed_ranges=many_date_ranges,
    )


def generalized_intervals(
    min_bases=0, max_bases=None, outer=None, *, many_typed_ranges
):
    # The algorithm relies on `many_*_ranges` to generate 2*n - 1 sub-ranges
    # within `outer` and then simply takes for the bases of the intervals
    # those in even-indexes.
    if min_bases is None:
        min_bases = 0
    assert 0 <= min_bases
    if max_bases is None:
        max_bases = DEFAULT_MAX_BASES if not min_bases else 2 * min_bases
    return (
        st.integers(min_value=min_bases or 0, max_value=max_bases)
        .flatmap(
            lambda n: many_typed_ranges(2 * n - 1 if n else 0, outer=outer)
        )
        .map(
            lambda rs: IntervalSet([r for i, r in enumerate(rs) if i % 2 == 0])
        )
    )


DEFAULT_MAX_BASES = 5
st.register_type_strategy(IntervalSet, float_intervals() | date_intervals())


class _RangeHelper:
    lowerbound = DelegatedAttribute("base_range", "lowerbound")
    upperbound = DelegatedAttribute("base_range", "upperbound")

    def __init__(self, lower, upper):
        self.base_range = Range.new_open_right(lower, upper)

    def get_member_strategy(self, allow_upper=False):
        if not self.base_range:
            # Empty ranges have no members, but the generic implementation of
            # Range allows for infinite values of Range which are empty (for all
            # value a, Range(a, a) is empty).
            #
            # Instead of requiring the base_range to be non-empty, we simply
            # generate the lowerbound.
            return st.just(self.base_range.lowerbound)
        if self.lowerbound is -Infinity:
            _min = self.LOWER_LIMIT
        else:
            _min = self.lowerbound
        if self.upperbound is Infinity:
            _max = self.UPPER_LIMIT
        else:
            _max = self.upperbound
        assert not isinstance(_min, type(Infinity)), f"Invalid min {_min}"
        assert not isinstance(_max, type(Infinity)), f"Invalid max {_max}"
        result = self.BASE_STRATEGY(min_value=_min, max_value=_max)
        if isinstance(self.base_range._lower, Excluded):
            result = result.filter(lambda v: v != _min)
        if isinstance(self.base_range._upper, Excluded):
            result = result.filter(lambda v: v != _max)
        if self.lowerbound is -Infinity:
            result = result | st.just(-Infinity)
        if self.upperbound is Infinity and allow_upper:
            result = result | st.just(Infinity)
        return result


class FloatRangeHelper(_RangeHelper):
    """Provides utilities to generate arbitrary ranges within the boundaries of this range."""

    # The lowest number generated unless the range has a lower lowerbound
    LOWER_LIMIT = -1e10

    # The highest number generated unless the range has a higher upperbound
    UPPER_LIMIT = 1e10

    BASE_STRATEGY = staticmethod(
        lambda **kwargs: st.floats(
            allow_infinity=False, allow_nan=False, **kwargs
        )
    )


def get_float_member_strategy(base_range=None, allow_upper=False):
    """Return a strategy to generate members from `base_range`.

    If `base_range` is None, we use a *reduced* base range from -1e10 to 1e10.
    The last number is excluded unless `allow_upper` is True.

    """
    if base_range is None:
        base_range = Range.new_open_right(
            FloatRangeHelper.LOWER_LIMIT, FloatRangeHelper.UPPER_LIMIT
        )
    return FloatRangeHelper(*base_range).get_member_strategy(
        allow_upper=allow_upper
    )


class DateRangeHelper(_RangeHelper):
    """Similar to _Range but generates datetimes."""

    # The lowest datetime generated unless the range has a lower lowerbound
    LOWER_LIMIT = datetime.datetime(1910, 1, 1)

    # The highest datetime generated unless the range has a higher upperbound
    UPPER_LIMIT = datetime.datetime(9900, 12, 31)

    BASE_STRATEGY = staticmethod(
        lambda **kwargs: st.datetimes(
            timezones=st.just(datetime.timezone.utc),
            allow_imaginary=False,
            **kwargs,
        ).map(lambda d: d.replace(tzinfo=None, fold=0))
    )


def get_date_member_strategy(base_range=None, allow_upper=False):
    """Return a strategy to generate members from `base_range`.

    If `base_range` is None, we use a *reduced* base range from 1910-01-01 to
    9900-12-31.  The last date is excluded unless `allow_upper` is True.

    """
    if base_range is None:
        base_range = Range.new_open_right(
            DateRangeHelper.LOWER_LIMIT, DateRangeHelper.UPPER_LIMIT
        )
    return DateRangeHelper(*base_range).get_member_strategy(
        allow_upper=allow_upper
    )


@st.composite
def generalized_ranges(draw, inner=None, outer=None, *, RangeType, kinds=None):
    if kinds is None:
        Kind = draw(range_constructors)
    else:
        Kind = draw(kinds)
    if outer is None:
        # FIXME: Go back to Range(None, None), but since Range(None, None) is
        # an open range, it gets messy to ensure the kind of range I'm
        # generating.
        outer = Kind(RangeType.LOWER_LIMIT, RangeType.UPPER_LIMIT)
    _ensure_range(outer)
    if inner is None:
        midpoint = draw(RangeType(*outer).get_member_strategy())
        inner = Kind(midpoint, midpoint)
    _ensure_range(inner)
    if inner == outer:
        return inner
    if inner > outer:
        raise ValueError(
            f"Impossible to find ranges r such that {inner!r} <= r <= {outer!r}"
        )
    left = RangeType(outer.lowerbound, inner.lowerbound).get_member_strategy()
    if outer.lowerbound is -Infinity:
        left |= st.just(-Infinity)
    right = RangeType(inner.upperbound, outer.upperbound).get_member_strategy()
    if outer.upperbound is Infinity:
        right |= st.just(Infinity)
    # The filter is needed because if right or left are at the point of the
    # boundaries of outer or inner, the arbitrary Kind can create an invalid
    # range.
    #
    # For instance: with outer being `Range(Excluded(0), Excluded(1))`; and
    # Kind being new_closed; we could generate `Range(Included(0),
    # Included(0.5))` which is not contained in outer.
    return draw(
        st.builds(Kind, left, right).filter(lambda r: inner <= r <= outer)
    )


def _ensure_range(which):
    if not isinstance(which, Range):
        raise TypeError(f"Invalid type of '{which!r}', expected a Range")


_ranges_strategies = st.sampled_from([many_float_ranges, many_date_ranges])
st.register_type_strategy(Range, float_ranges() | date_ranges())
