#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import operator
import pickle
import unittest
from copy import copy
from datetime import timedelta
from itertools import combinations
from random import sample, shuffle

from hypothesis import example, given, settings
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from xotl.tools.infinity import Infinity

from ..domains import EquivalenceSet, IntervalSet
from ..ranges import Bound, Excluded, Included, Range, RangeKind
from .strategies.domains import (
    date_ranges,
    equivalence_sets,
    float_ranges,
    get_date_member_strategy,
    many_date_ranges,
    many_float_ranges,
    members_of_date_ranges,
    members_of_float_ranges,
    non_empty_equivalence_sets,
    type_of_bounds,
)

DAY = timedelta(1)


kinds_with_samples = st.sampled_from(
    (Range.new_open_left, Range.new_open_right, Range.new_closed)
)


@st.composite
def _sorted_points(draw, many=2):
    assert many >= 2
    points = list(
        sorted(draw(st.sets(st.integers(), min_size=many, max_size=many)))
    )
    if draw(st.booleans()):
        points[0] = -Infinity
    if draw(st.booleans()):
        points[-1] = Infinity
    return tuple(points)


ranges = st.tuples(
    # Generates Ranges by applying zip_map to a list of two Bound
    # to a sorted pair of integers.
    st.lists(type_of_bounds, min_size=2, max_size=2),
    _sorted_points(),
).map(lambda args: Range(*zip_map(args[0], args[1])))

integer_intervalsets: SearchStrategy[IntervalSet[int]] = st.sets(ranges).map(
    lambda s: IntervalSet(s)
)
integer_nonempty_intervalsets: SearchStrategy[IntervalSet[int]] = st.sets(
    ranges.filter(bool), min_size=1
).map(lambda s: IntervalSet(s))


@given(
    st.sets(st.integers(), min_size=3, max_size=3),
    type_of_bounds,
    type_of_bounds,
)
def test_range_intersection_with_a_common_boundary(points, Bound1, Bound2):
    a, b, c = sorted(points)
    r1 = Range(Bound1(a), Included(b))
    r2 = Range(Included(b), Bound2(c))
    assert r1 & r2 == Range(Included(b), Included(b))


@given(
    st.sets(st.integers(), min_size=3, max_size=3),
    type_of_bounds,
    type_of_bounds,
)
def test_range_intersection_with_a_common_Excluded_boundary(
    points, Bound1, Bound2
):
    a, b, c = sorted(points)
    assert not Range(Bound1(a), Excluded(b)) & Range(Included(b), Bound2(c))
    assert not Range(Bound1(a), Included(b)) & Range(Excluded(b), Bound2(c))
    assert not Range(Bound1(a), Excluded(b)) & Range(Excluded(b), Bound2(c))


@given(
    st.sets(st.integers(), min_size=4, max_size=4),
    st.lists(type_of_bounds, min_size=4, max_size=4),
)
def test_range_intersection_with_no_common_bounds(points, Bounds):
    a, b, c, d = zip_map(Bounds, sorted(points))
    assert not Range(a, b) & Range(c, d)


@given(
    st.sets(st.integers(), min_size=4, max_size=4),
    st.lists(type_of_bounds, min_size=4, max_size=4),
)
def test_range_intersection_with_overlapping_bounds(points, Bounds):
    a, b, c, d = zip_map(Bounds, sorted(points))
    assert Range(a, c) & Range(b, d) == Range(b, c)


@given(ranges)
def test_range_intersection_with_overlapping_bounds_and_unbounded(r0):
    r1 = Range(None, r0._upper)
    r2 = Range(r0._lower, None)
    assert r1 & r2 == r0


@given(ranges, ranges)
def test_range_intersection_is_contained_in_the_original_ranges(r1, r2):
    assert r1 & r2 <= r1
    assert r1 & r2 <= r2


@given(ranges, ranges)
def test_range_intersection_is_commutative(r1, r2):
    assert r1 & r2 == r2 & r1


@given(ranges, ranges, ranges)
def test_range_intersection_is_associative(r1, r2, r3):
    assert (r1 & r2) & r3 == r1 & (r2 & r3)


@given(
    st.sets(st.integers(), min_size=4, max_size=4),
    st.lists(type_of_bounds, min_size=4, max_size=4),
)
def test_range_diff_totally_enclosed_range(points, Bounds):
    a, b, c, d = zip_map(Bounds, sorted(points))
    big = Range(a, d)
    small = Range(b, c)
    # So we have something like:
    #
    #   big:   a ------------------------ d
    # small:            b ------- c
    #
    # So, big.diff(small) will result in two ranges:
    #
    #  before:  a ---- ~b
    #  after:                     ~c ---- d
    #
    # ~b means that if b is Included in `small`, it must be Excluded in
    # `before`; if it was Excluded in `small`, it must be Included in
    # `before`.
    result = big.diff(small)
    before, after = result
    assert before == Range(a, ~b)
    assert after == Range(~c, d)


@given(ranges, ranges)
@example(Range.new_open_right(0, None), Range(Excluded(0), Included(1)))
def test_range_diff_is_contained_in_r1_and_missing_in_r2(r1, r2):
    for diff in r1.diff(r2):
        assert diff <= r1
        assert not (diff <= r2)


@given(
    st.sets(st.integers(), min_size=4, max_size=4),
    st.lists(type_of_bounds, min_size=4, max_size=4),
)
def test_range_diff_disjoint_range(points, Bounds):
    a, b, c, d = zip_map(Bounds, sorted(points))
    r1 = Range(a, b)
    r2 = Range(c, d)
    assert r1.diff(r2) == (r1,)
    assert r2.diff(r1) == (r2,)


@given(
    st.sets(st.integers(), min_size=4, max_size=4),
    st.lists(type_of_bounds, min_size=4, max_size=4),
)
def test_range_diff_overlapping_ranges(points, Bounds):
    a, b, c, d = zip_map(Bounds, sorted(points))
    r1 = Range(a, c)
    r2 = Range(b, d)
    (before,) = r1.diff(r2)
    assert before == Range(a, ~b)
    (after,) = r2.diff(r1)
    assert after == Range(~c, d)


@given(_sorted_points(many=3), type_of_bounds, type_of_bounds)
def test_range_join_doesnt_get_confused_about_excluded(points, Bound1, Bound2):
    a, b, c = points
    r1 = Range(Bound1(a), Excluded(b))
    r2 = Range(Excluded(b), Bound2(c))
    assert r1.join(r2) == (r1, r2)


@given(_sorted_points(many=3), type_of_bounds, type_of_bounds)
def test_range_join_collapse_included(points, Bound1, Bound2):
    a, b, c = points
    r1 = Range(Bound1(a), Included(b))
    r2 = Range(Excluded(b), Bound2(c))
    assert r1.join(r2) == (Range(Bound1(a), Bound2(c)),)


@given(_sorted_points(many=5), type_of_bounds, type_of_bounds)
def test_range_multi_bounded_joins(points, Bound1, Bound2):
    # So we have something like:
    #  r1  a ------------------------------------ e
    #  r2                        !=d ------------ e
    #  r3     b -------- ~c
    #  r4                 c -----  d
    #  r5                ~c ----- ~d
    #
    # So now:
    #  -> any range join with r1 will result in r1
    #  -> any r2 and r3 will not overlap so it will result in (r3, r2)
    #  -> any join of (r3,r4,r2) return Range(b, e)
    #  -> any join of (r3,r5,r2) return in the same (r3,r5,r2)
    #
    #  ~c and ~d means that this bounds are Excluded in r2,r3,r5 and
    # Included the other Ranges

    a, b, c, d, e = points
    r1 = Range(Bound1(a), Bound2(e))
    r2 = Range(Excluded(d), Bound2(e))
    r3 = Range(Bound1(b), Excluded(c))
    r4 = Range(Included(c), Included(d))
    r5 = Range(Excluded(c), Excluded(d))
    assert r1.join(r2, r3, r4) == (r1,)
    assert r2.join(r3) == (r3, r2)
    assert r3.join(r4, r2) == (Range(Bound1(b), Bound2(e)),)
    assert r3.join(r5, r2) == (r3, r5, r2)


def test_regression_hash_compatible_with_eq_in_ranges():
    r1 = Range.new_open_right(0, 0)
    r2 = Range.new_open_right(1, 1)
    assert r1 == r2
    assert hash(r1) == hash(r2)


def _test_float_ranges_generation(data, r0, kinds=None):
    r1 = data.draw(float_ranges(outer=r0, kinds=kinds))
    assert r1 <= r0, f"{r1} is not a sub-range of {r0}"
    r2 = data.draw(float_ranges(inner=r1, kinds=kinds))
    assert r1 <= r2, f"{r1} is not a sub-range of {r2}"


@given(st.data(), float_ranges())
def test_float_ranges_generation(data, r0):
    _test_float_ranges_generation(data, r0)


@given(st.data())
def test_float_ranges_generation_regression_job_117109(data):
    _test_float_ranges_generation(
        data, Range.new_open(0, 1), kinds=st.just(Range.new_closed)
    )


@given(st.data(), date_ranges())
def test_date_ranges_confined_generation(data, r0):
    r1 = data.draw(date_ranges(outer=r0))
    assert r1 <= r0, f"{r1} is not a sub-range of {r0}"
    r2 = data.draw(date_ranges(inner=r1))
    assert r1 <= r2, f"{r1} is not a sub-range of {r2}"


class DomainCase(unittest.TestCase):  # pragma: no cover
    def assertPickable(self, what):
        for proto in range(pickle.DEFAULT_PROTOCOL, pickle.HIGHEST_PROTOCOL):
            serialized = pickle.dumps(what, proto)
            self.assertEqual(what, pickle.loads(serialized))

    def assertEmpty(self, x, msg=None):
        if x:
            raise self.failureException(msg or f"{x} is not empty")

    def assertNonEmpty(self, x, msg=None):
        if not x:
            raise self.failureException(msg or f"{x} is empty")

    def assertOverlap(self, a, b, msg=None):
        r = a & b
        if not r:
            raise self.failureException(msg or f"{a} and {b} don't overlap")

    def assertDisjoint(self, a, b, msg=None):
        r = a & b
        if r:
            raise self.failureException(msg or f"{a} and {b} are not disjoint")

    def assertSampleIsMember(self, domain1, domain2):
        if domain1:
            if domain1.sample is not None:
                self.assertIn(domain1.sample, domain1 | domain2)
            else:
                self.assertIsInstance(domain1, IntervalSet)
                for r in domain1.ranges:
                    self.assertEqual(r.kind, RangeKind.OPEN)


class TestRange(DomainCase):
    @staticmethod
    def add(left, right):  # pragma: no cover
        if left and right:
            assert (
                right.lowerbound in left or right.lowerbound == left.upperbound
            )
            return Range.new_open_right(
                left.lowerbound, max(left.upperbound, right.upperbound)
            )
        elif left:
            return left
        else:
            return right

    @given(many_float_ranges(n=10) | many_date_ranges(n=10))
    def test_generated_siblings_are_consecutive(self, siblings):
        last = None
        for right in siblings:
            self.add(last, right)
            last = right
        self.assertIsNot(last, None)
        self.assertEqual(len(siblings), 10)

    @given(many_float_ranges(n=10))
    def test_ranges_generates_disjoint_numbers(self, siblings):
        for left, right in combinations(siblings, 2):
            self.assertEmpty(
                left & right,
                f"{left!r} & {right!r} = {left & right}; and is not empty",
            )

    @given(many_date_ranges(n=10))
    def test_ranges_generates_disjoint_dates(self, siblings):
        for left, right in combinations(siblings, 2):
            self.assertEmpty(
                left & right,
                f"{left!r} & {right!r} = {left & right}; and is not empty",
            )

    @given(many_float_ranges(n=10) | many_date_ranges(n=10))
    def test_ranges_generates_orderered(self, siblings):
        lowers = [r.lowerbound for r in siblings]
        self.assertEqual(lowers, list(sorted(lowers)))

    @given(many_float_ranges(n=4) | many_date_ranges(n=4))
    def test_non_empty_siblings(self, siblings):
        for range_ in siblings:
            self.assertNonEmpty(range_)

    @given(many_float_ranges(n=4) | many_date_ranges(n=4))
    def test_join_is_disjoint(self, siblings):
        joined = Range.join(*siblings)
        for a, b in combinations(joined, 2):
            self.assertDisjoint(a, b)

    @given(many_float_ranges(n=4) | many_date_ranges(n=4))
    def test_join_is_not_order_sensitive(self, siblings):
        expected = Range.join(*siblings)
        shuffled = sample(siblings, len(siblings))
        joined = Range.join(*shuffled)
        self.assertEqual(joined, expected)

    @given(many_float_ranges(n=4) | many_date_ranges(n=4))
    def test_join_doesnt_mutate_args(self, siblings):
        copies = tuple(copy(r) for r in siblings)
        Range.join(*siblings)
        self.assertEqual(siblings, copies)

    def test_join_returns_the_empty_tuple(self):
        ranges = [Range.new_open_right(x, x) for x in range(5)]
        joined = Range.join(*ranges)
        self.assertEmpty(joined)

    @given(float_ranges() | date_ranges())
    def test_diff_with_self_returns_nothing(self, range_):
        empty = range_.diff(range_)
        self.assertEmpty(empty)

    @given(float_ranges() | date_ranges())
    def test_range_iterable(self, range_):
        l, u = range_
        self.assertEqual(range_._lower.bound, l)
        self.assertEqual(range_._upper.bound, u)

    @given(float_ranges() | date_ranges())
    def test_range_pickable(self, range_):
        self.assertPickable(range_)

    @given(
        float_ranges(kinds=st.just(Range.new_open_right))
        .filter(bool)
        .flatmap(lambda r: st.tuples(st.just(r), members_of_float_ranges(r)))
        | date_ranges(kinds=st.just(Range.new_open_right))
        .filter(bool)
        .flatmap(lambda r: st.tuples(st.just(r), members_of_date_ranges(r)))
    )
    def test_members_of_ranges(self, args):
        range_, member = args
        self.assertIn(member, range_)

    @given(
        float_ranges(kinds=kinds_with_samples)
        | date_ranges(kinds=kinds_with_samples)
    )
    def test_sample_in_range(self, range_):
        self.assertIn(
            range_.sample, range_, f"Sample {range_.sample} is not in {range_}"
        )

    @given(float_ranges() | date_ranges())
    def test_range_kinds(self, range_):
        if isinstance(range_._lower, Included) and isinstance(
            range_._upper, Excluded
        ):
            self.assertTrue(range_.kind == RangeKind.OPEN_RIGHT)
        elif isinstance(range_._lower, Included) and isinstance(
            range_._upper, Included
        ):
            self.assertTrue(range_.kind == RangeKind.CLOSED)
        elif isinstance(range_._lower, Excluded) and isinstance(
            range_._upper, Excluded
        ):
            self.assertTrue(range_.kind == RangeKind.OPEN)
        elif isinstance(range_._lower, Excluded) and isinstance(
            range_._upper, Included
        ):
            self.assertTrue(range_.kind == RangeKind.OPEN_LEFT)

    @given(st.floats(allow_nan=False) | st.datetimes() | st.integers())
    def test_for_empty_range(self, point):
        a = point
        r1 = Range.new_open_right(a, a)
        r2 = Range.new_open_left(a, a)
        r3 = Range.new_open(a, a)
        r4 = Range.new_closed(a, a)
        self.assertEmpty(r1)
        self.assertEmpty(r2)
        self.assertEmpty(r3)
        self.assertNonEmpty(r4)

    @given(_sorted_points(many=3))
    def test_for_point_in_range(self, points):
        # any point in between the extremes will allways be in the range
        a, b, c = points
        self.assertIn(b, Range.new_open_right(a, c))
        self.assertIn(b, Range.new_open_left(a, c))
        self.assertIn(b, Range.new_open(a, c))
        self.assertIn(b, Range.new_closed(a, c))
        self.assertIn(b, Range.new_closed(b, b))

    @given(
        st.one_of(
            st.floats(max_value=10000.0, min_value=-10000.0),
            st.datetimes(),
            st.integers(max_value=10000, min_value=-10000),
        )
    )
    def test_bounds_operations(self, bound):
        assert ~Excluded(bound) == Included(bound)
        assert not (Excluded(Infinity) and Excluded(-Infinity))
        assert Included.safer_new(Infinity) == Excluded(Infinity)
        assert Included.safer_new(-Infinity) == Excluded(-Infinity)
        assert Included.safer_new(bound) == Included(bound)
        assert Included(bound)
        assert Excluded(bound)
        assert not (Excluded(-Infinity) and Excluded(-Infinity))
        assert Included(bound) != Excluded(bound)

    @given(
        st.floats() | st.datetimes() | st.integers(),
        st.sampled_from([Included, Excluded]),
    )
    def test_bounds_normalization(self, bound, Bound_):
        assert Bound.normalized_lower_bound(None, Bound_) == Excluded(-Infinity)
        assert Bound.normalized_upper_bound(None, Bound_) == Excluded(Infinity)

        assert Bound.normalized_lower_bound(bound, Excluded) == Excluded(bound)
        assert Bound.normalized_upper_bound(bound, Excluded) == Excluded(bound)

        assert Bound.normalized_lower_bound(bound, Included) == Included(bound)
        assert Bound.normalized_upper_bound(bound, Included) == Included(bound)


class EqSet(DomainCase):
    @given(equivalence_sets)
    def test_sample_returns_the_same(self, eqset):
        sample = eqset.sample
        # test sample returns the same object, and not an arbitrary one
        self.assertIs(sample, eqset.sample)
        self.assertIs(sample, eqset.sample)

    @given(equivalence_sets)
    def test_sample_is_in_the_set(self, eqset):
        sample = eqset.sample
        if eqset:
            self.assertIn(sample, eqset)
        else:
            self.assertIs(sample, None)

    @given(st.lists(equivalence_sets, min_size=1, max_size=20))
    def test_join_doesnt_mutate_args(self, eqsets):
        copies = [copy(r) for r in eqsets]
        EquivalenceSet.join(*eqsets)
        self.assertEqual(eqsets, copies)

    @given(equivalence_sets)
    def test_containment_of_the_empty_eqset(self, eqset):
        self.assertLessEqual(EquivalenceSet([]), eqset)
        self.assertGreaterEqual(eqset, EquivalenceSet([]))

    def _test_containment_of_union(self, eqset, other):
        self.assertLessEqual(eqset, eqset | other)
        self.assertLessEqual(other, eqset | other)
        self.assertSampleIsMember(eqset, eqset | other)
        self.assertSampleIsMember(other, eqset | other)

    @given(
        non_empty_equivalence_sets | integer_nonempty_intervalsets,
        non_empty_equivalence_sets,
    )
    def test_containment_of_union_other_eqset(self, other, eqset):
        self._test_containment_of_union(other, eqset)

    @given(
        non_empty_equivalence_sets | integer_nonempty_intervalsets,
        non_empty_equivalence_sets,
    )
    def test_containment_of_union_eqset_other(self, other, eqset):
        self._test_containment_of_union(eqset, other)

    def _test_containment_of_intersection(self, eqset, other):
        intersection = eqset & other
        self.assertLessEqual(intersection, eqset)
        self.assertLessEqual(intersection, other)
        if intersection:
            self.assertIn(intersection.sample, eqset)
            self.assertIn(intersection.sample, other)

    @given(equivalence_sets | integer_intervalsets, equivalence_sets)
    def test_containment_of_intersection_any_eqset(self, other, eqset):
        self._test_containment_of_intersection(other, eqset)

    @given(equivalence_sets | integer_intervalsets, equivalence_sets)
    def test_containment_of_intersection_eqset_any(self, other, eqset):
        self._test_containment_of_intersection(eqset, other)

    def _test_diff_containment(self, eqset, other):
        diff = eqset.diff(other)
        self.assertLessEqual(diff, eqset)

    @given(equivalence_sets | integer_intervalsets, equivalence_sets)
    def test_diff_containment_other_eqset(self, other, eqset):
        self._test_diff_containment(other, eqset)

    @given(equivalence_sets | integer_intervalsets, equivalence_sets)
    def test_diff_containment_eqset_other(self, other, eqset):
        self._test_diff_containment(eqset, other)


class IntervalTest(DomainCase):
    @given(
        st.lists(float_ranges(kinds=kinds_with_samples), max_size=10)
        | st.lists(date_ranges(kinds=kinds_with_samples), max_size=10)
    )
    def test_sample_is_member(self, ranges):
        interval = IntervalSet(ranges)
        self.assertSampleIsMember(interval, interval)

    @given(
        st.lists(float_ranges(), max_size=10)
        | st.lists(date_ranges(), max_size=10)
    )
    def test_interval_filters_emptys(self, ranges):
        interval = IntervalSet(ranges)
        for range_ in interval.ranges:
            self.assertNonEmpty(range_)

    def _test_interval_diff_produces_disjoint_ranges(self, r1, r2):
        i1 = IntervalSet(r1)
        i2 = IntervalSet(r2)
        idiff = i1.diff(i2)
        assert not any(a & b for a, b in combinations(idiff.ranges, 2))

    @given(
        st.lists(float_ranges(), max_size=10),
        st.lists(float_ranges(), max_size=10),
    )
    def test_float_interval_diff_produces_disjoint_ranges(self, r1, r2):
        self._test_interval_diff_produces_disjoint_ranges(r1, r2)

    @given(st.lists(float_ranges(), min_size=2, max_size=10), st.data())
    def test_float_interval_diff_produces_disjoint_ranges_non_empty_diff(
        self, r1, data
    ):
        last_range = r1[-1]
        next_range = _build_next_range(last_range, 1, data)
        r2 = r1 + [next_range]
        self._test_interval_diff_produces_disjoint_ranges(r1, r2)

    @given(
        st.lists(date_ranges(), min_size=2, max_size=10),
        st.lists(date_ranges(), max_size=10),
    )
    def test_date_interval_diff_produces_disjoint_ranges(self, r1, r2):
        self._test_interval_diff_produces_disjoint_ranges(r1, r2)

    def _test_interval_diff_produces_sorted_ranges(self, r1, r2):
        i1 = IntervalSet(r1)
        i2 = IntervalSet(r2)
        idiff = i1.diff(i2)
        assert idiff.ranges == tuple(
            sorted(idiff.ranges, key=operator.attrgetter("lowerbound"))
        )

    @given(
        st.lists(float_ranges(), min_size=2, max_size=10),
        st.lists(float_ranges(), max_size=10),
    )
    def test_float_interval_diff_produces_sorted_ranges(self, r1, r2):
        self._test_interval_diff_produces_sorted_ranges(r1, r2)

    @given(
        st.lists(date_ranges(), min_size=2, max_size=10),
        st.lists(date_ranges(), max_size=10),
    )
    def test_date_interval_diff_produces_sorted_ranges(self, r1, r2):
        self._test_interval_diff_produces_sorted_ranges(r1, r2)

    @given(st.lists(date_ranges(), min_size=2, max_size=10), st.data())
    def test_date_interval_diff_produces_sorted_ranges_non_emptydiff(
        self, r1, data
    ):
        last_range = r1[-1]
        next_range = _build_next_range(last_range, DAY, data)
        r2 = r1 + [next_range]
        self._test_interval_diff_produces_sorted_ranges(r1, r2)

    def _test_interval_diff_produces_non_toucheing_ranges(self, r1, r2):
        i1 = IntervalSet(r1)
        i2 = IntervalSet(r2)
        idiff = i1.diff(i2)
        assert not idiff.ranges or idiff.ranges == idiff.ranges[0].join(
            *idiff.ranges[1:]
        )

    @settings(deadline=None)
    @given(
        st.lists(float_ranges(), min_size=2, max_size=10),
        st.lists(float_ranges(), max_size=10),
    )
    def test_float_interval_diff_produces_non_toucheing_ranges(self, r1, r2):
        self._test_interval_diff_produces_non_toucheing_ranges(r1, r2)

    @settings(deadline=None)
    @given(st.lists(float_ranges(), min_size=2, max_size=10), st.data())
    def test_float_interval_diff_produces_non_toucheing_ranges_non_emptydiff(
        self, r1, data
    ):
        last_range = r1[-1]
        next_range = _build_next_range(last_range, 1, data)
        r2 = r1 + [next_range]
        self._test_interval_diff_produces_non_toucheing_ranges(r1, r2)

    @given(
        st.lists(date_ranges(), min_size=2, max_size=10),
        st.lists(date_ranges(), max_size=10),
    )
    def test_date_interval_diff_produces_non_toucheing_ranges(self, r1, r2):
        self._test_interval_diff_produces_non_toucheing_ranges(r1, r2)

    @given(
        st.lists(date_ranges(), max_size=10),
        st.lists(date_ranges(), max_size=10),
    )
    def test_containment_of_union(self, r1, r2):
        i1 = IntervalSet(r1)
        i2 = IntervalSet(r2)
        union = i1 | i2
        self.assertLessEqual(i1, union)
        self.assertLessEqual(i2, union)
        self.assertSampleIsMember(i1, union)
        self.assertSampleIsMember(i2, union)

    @given(
        st.lists(date_ranges(), max_size=10),
        st.lists(date_ranges(), max_size=10),
    )
    def test_containment_of_intersection(self, r1, r2):
        i1 = IntervalSet(r1)
        i2 = IntervalSet(r2)
        intersection = i1 & i2
        self.assertLessEqual(intersection, i1)
        self.assertLessEqual(intersection, i2)
        self.assertSampleIsMember(intersection, i1)
        self.assertSampleIsMember(intersection, i2)

    @given(
        st.lists(date_ranges(), max_size=10),
        st.lists(date_ranges(), max_size=10),
    )
    def test_containment_of_diff(self, r1, r2):
        i1 = IntervalSet(r1)
        i2 = IntervalSet(r2)
        diff = i1.diff(i2)
        self.assertLessEqual(diff, i1)

    @given(st.lists(date_ranges(), max_size=10))
    def test_equal_intervals(self, r1):
        i1 = IntervalSet(r1)
        shuffle(r1)
        i2 = IntervalSet(r1)
        self.assertEqual(i1, i2)


@given(get_date_member_strategy())
def test_get_date_member_strategy_produces_nonimaginary_unfolded_dates(d):
    assert getattr(d, "fold", 0) == 0
    assert getattr(d, "tzinfo", None) is None


def _build_next_range(r, delta, data):
    Bound1, Bound2 = data.draw(st.tuples(type_of_bounds, type_of_bounds))
    lowerbound = r.upperbound + delta
    upperbound = lowerbound + delta
    return Range(Bound1(lowerbound), Bound2(upperbound))


# TODO: Move this to xoutil
def zip_map(funcs, iterable):
    for f, x in zip(funcs, iterable):
        yield f(x)
