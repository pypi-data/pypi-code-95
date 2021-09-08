#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Implementation of several domains.

Domains are used by AVMs to describe groups of values of an attribute for
which a program behaves in the same way.

"""
from collections import deque
from dataclasses import dataclass
from itertools import product
from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from xotl.tools.objects import lazy, setdefaultattr

from .ranges import Range
from .types import Domain, TEq, TOrd


@dataclass(init=False, unsafe_hash=True)
class EquivalenceSet(Generic[TEq]):
    "A simple wrapper over a Python set for items with EqTypeClass"
    values: AbstractSet[TEq]
    __slots__ = ("values", "_sample")

    def __init__(self, values: AbstractSet[TEq]) -> None:
        self.values = frozenset(values)

    def to_interval_set(self) -> "IntervalSet[TOrd]":
        """Convert to a semantically-equivalent interval set.

        This should only be applied for equivalence sets containing orderable
        (Ord) items.

        """
        ranges: List[Range[TOrd]] = []
        values = set(self.values)
        while values:
            val: TOrd = values.pop()  # type: ignore
            ranges.append(Range.new_closed(val, val))
        return IntervalSet(ranges)

    def __bool__(self):
        return bool(self.values)

    def __contains__(self, val: TEq) -> bool:
        return val in self.values

    def __le__(self, other: "EquivalenceSet") -> bool:
        if isinstance(other, IntervalSet):
            return self.to_interval_set() <= other
        if not isinstance(other, EquivalenceSet):
            return NotImplemented
        return self.values <= other.values

    def __lt__(self, other: "EquivalenceSet") -> bool:  # pragma: no cover
        if isinstance(other, IntervalSet):
            return self.to_interval_set() < other
        if not isinstance(other, EquivalenceSet):
            return NotImplemented
        return self.values < other.values

    def __ge__(self, other: "EquivalenceSet") -> bool:  # pragma: no cover
        if isinstance(other, IntervalSet):
            return self.to_interval_set() >= other
        if not isinstance(other, EquivalenceSet):
            return NotImplemented
        return self.values >= other.values

    def __gt__(self, other: "EquivalenceSet") -> bool:  # pragma: no cover
        if isinstance(other, IntervalSet):
            return self.to_interval_set() > other
        if not isinstance(other, EquivalenceSet):
            return NotImplemented
        return self.values > other.values

    def __and__(
        self, other: "EquivalenceSet"
    ) -> "EquivalenceSet":  # pragma: no cover
        if isinstance(other, IntervalSet):
            return self.to_interval_set() & other
        if not isinstance(other, EquivalenceSet):
            return NotImplemented
        return EquivalenceSet(self.values & other.values)

    def diff(
        self, other: "EquivalenceSet"
    ) -> "EquivalenceSet":  # pragma: no cover
        if isinstance(other, IntervalSet):
            return self.to_interval_set().diff(other)
        if not isinstance(other, EquivalenceSet):
            return NotImplemented
        return EquivalenceSet(self.values - other.values)

    __sub__ = difference = diff

    def __or__(
        self, other: "EquivalenceSet"
    ) -> "EquivalenceSet":  # pragma: no cover
        if isinstance(other, IntervalSet):
            return self.to_interval_set() | other
        if not isinstance(other, EquivalenceSet):
            return NotImplemented
        return EquivalenceSet(self.values | other.values)

    def union(
        self, *others: "EquivalenceSet"
    ) -> "EquivalenceSet":  # pragma: no cover
        from functools import reduce
        from operator import or_

        sets: Tuple[EquivalenceSet, ...] = tuple(
            s for s in (self,) + others if s
        )
        values: AbstractSet = reduce(or_, (s.values for s in sets), frozenset())
        return EquivalenceSet(values)

    join = union

    @property
    def sample(self) -> Optional[TEq]:
        if self.values:
            # We cache the result to return the same sample all the time.
            # set.pop() return an arbitrary element.
            return setdefaultattr(
                self, "_sample", lazy(lambda: set(self.values).pop())
            )
        else:
            return None


class DomainMismatch(TypeError):
    pass


@dataclass(init=False, unsafe_hash=True)
class IntervalSet(Generic[TOrd]):
    ranges: Tuple[Range[TOrd], ...]
    __slots__ = ("ranges",)

    def __init__(self, bases: Iterable[Range[TOrd]]) -> None:
        if bases:
            # Normalize the bases, we must keep our individual bases
            # disjoint.
            base, *others = self._extract_all_ranges(bases)
            # Ensure the first base range is not empty
            while not base and others:
                base, *others = others
            if base:
                normalized = base.join(*others)
                assert all(r for r in normalized)
                # `join` will return non-empty bases since `base` is non-empty
                self.ranges = normalized
            else:
                assert not others
                self.ranges = ()
        else:
            self.ranges = ()

    @classmethod
    def _from_ordered_disjoint(
        cls, bases: Iterable[Range[TOrd]]
    ) -> "IntervalSet[TOrd]":
        result = cls([])
        result.ranges = tuple(bases)
        return result

    @classmethod
    def _extract_ranges(
        cls, other: Union["IntervalSet[TOrd]", Range[TOrd]]
    ) -> Tuple[Range[TOrd], ...]:
        if isinstance(other, EquivalenceSet):
            return other.to_interval_set().ranges
        if isinstance(other, IntervalSet):
            return other.ranges
        else:
            assert isinstance(other, Range)
            return (other,)

    @classmethod
    def _extract_all_ranges(
        cls, *args: Iterable[Union["IntervalSet[TOrd]", Range[TOrd]]]
    ) -> Tuple[Range[TOrd], ...]:
        return tuple(
            base
            for arg in args
            for bases in arg
            for base in cls._extract_ranges(bases)
        )

    def __repr__(self):
        return f"IntervalSet({self.ranges!r})"

    @property
    def sample(self) -> Optional[TOrd]:
        if self.ranges:
            return next(
                (r.sample for r in self.ranges if r.sample is not None), None
            )
        else:
            return None

    def __contains__(self, value: TOrd) -> bool:
        return any(value in base for base in self.ranges)

    def __bool__(self):
        return bool(self.ranges)

    def __le__(self, other: "IntervalSet[TOrd]") -> bool:
        if isinstance(other, EquivalenceSet):
            other = other.to_interval_set()
        if not isinstance(other, IntervalSet):
            return NotImplemented
        if not self:
            return True
        if not other:
            return False
        return all(
            any(mine <= their for their in other.ranges) for mine in self.ranges
        )

    def __lt__(self, other: "IntervalSet[TOrd]") -> bool:  # pragma: no cover
        if isinstance(other, EquivalenceSet):
            other = other.to_interval_set()
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self <= other and not (other <= self)

    def __ge__(self, other: "IntervalSet[TOrd]") -> bool:  # pragma: no cover
        if isinstance(other, EquivalenceSet):
            other = other.to_interval_set()
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return other <= self

    def __gt__(self, other: "IntervalSet[TOrd]") -> bool:  # pragma: no cover
        if isinstance(other, EquivalenceSet):
            other = other.to_interval_set()
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self >= other and not (other >= self)

    def __eq__(self, other) -> bool:
        if isinstance(other, EquivalenceSet):
            other = other.to_interval_set()
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self <= other <= self

    def __and__(self, other: "IntervalSet[TOrd]") -> "IntervalSet[TOrd]":
        if isinstance(other, EquivalenceSet):
            other = other.to_interval_set()
        if not isinstance(other, IntervalSet):
            return NotImplemented
        bases = tuple(
            filter(
                None,
                (
                    base & other_base
                    for base, other_base in product(self.ranges, other.ranges)
                ),
            )
        )
        return IntervalSet(bases)

    def union(self, *others: "IntervalSet[TOrd]") -> "IntervalSet[TOrd]":
        all_ranges = self._extract_all_ranges(self.ranges, others)
        if all_ranges:
            base, *bases = all_ranges
            new_bases = base.join(*bases)
        else:
            new_bases = ()
        return IntervalSet(new_bases)

    __or__ = join = union

    def diff(self, other: "IntervalSet[TOrd]") -> "IntervalSet[TOrd]":
        # The algorithm depends that 'ranges' are sorted ranges from left to
        # right by the lowerbound, like this:
        #
        #    ours      |------|   |------|   |--| |-----| |---|
        #  theirs   |---------------|  |-|          |-------|
        #
        # Our __init__ ensures this.
        if isinstance(other, EquivalenceSet):
            other = other.to_interval_set()
        ours = deque(self.ranges)
        theirs = deque(other.ranges)
        results = []
        while ours and theirs:
            top: Range = ours.popleft()
            bottom: Range = theirs.popleft()
            assert top and bottom
            if top == bottom:
                # Nothing to produce here, both sub-ranges are consumed.
                pass
            elif top & bottom:
                # There are four possible cases here (five if we count top ==
                # bottom, but we ruled that out):
                #
                # case:       a     !     b    !    c   !    d
                # ~~~~~~~~~~~~~~~~~~+~~~~~~~~~~+~~~~~~~~+~~~~~~~~~
                # top      |------| !   |----| ! |---|  !   |--|
                # bottom     |--|   ! |---|    !   |---|! |------|
                #
                # The case 'a' will produce a range to "left" that cannot
                # intercept with any other range; so we can put it the
                # results.  The second range may intercept with another of
                # theirs so we put it in the front of ours.  But this case,
                # has two sub-cases:
                #
                #                a.1               a.2
                #   top        |-----|   and    |-----|
                #   bottom     |---|               |--|
                #
                # In the first sub-case we cannot push the diff to the result.
                # In the second we have nothing to push to ours.  But those
                # can be treated the same as the cases 'b' and 'c'.
                diff = top.diff(bottom)
                if diff:
                    if (
                        len(diff) > 1
                    ):  # ->                                   case 'a'.
                        left, right = diff
                        results.append(left)
                        ours.appendleft(right)
                    else:
                        assert len(diff) == 1
                        if (
                            bottom.lowerbound <= top.lowerbound
                        ):  # ->         cases 'b' or a.1
                            ours.appendleft(diff[0])
                        elif (
                            top.upperbound <= bottom.upperbound
                        ):  # ->       cases 'c' or a.2
                            results.append(diff[0])
                            # We need to reintroduce bottom to theirs, because
                            # it can overlap with the next top of 'ours'.
                            theirs.appendleft(bottom)
                        else:
                            assert False
                else:  # ->                                                   case 'd'
                    # We need to reintroduce bottom to theirs, because it can
                    # overlap with the next top of 'ours'.
                    theirs.appendleft(bottom)
            else:
                # There are two cases here:
                #
                #                 'a'               'b'
                #   top             |-----|   and    |-----|
                #   bottom     |---|                        |--|
                #
                if bottom.upperbound <= top.lowerbound:
                    ours.appendleft(top)
                elif top.upperbound <= bottom.lowerbound:
                    theirs.appendleft(bottom)
                else:  # pragma: no cover
                    assert False

        if ours:
            assert not theirs
            results.extend(ours)
        return IntervalSet._from_ordered_disjoint(results)

    __sub__ = difference = diff


def iter_domain_endpoints(domains: Sequence[Domain[TOrd]]) -> Iterator[TOrd]:
    """Yields likely endpoints in the domains.

    We don't actually yield all the endpoints but those who can be one of the
    max/min endpoint of an entire interval which covers all the domains.

    Basically, for each domain we yield at most two endpoints: the min and max
    of the endpoints in the domain.  For an
    `~xotless.domains.EquivalenceSet`:class:, the endpoints are just the
    min/max values in the set.  If the set has a single value, we only yield
    once.  For an `~xotless.domains.IntervalSet`:class: the endpoints are the
    min and max all the ranges regardless of if they are included or not in
    the interval set.

    Example:

       >>> eq1 = EquivalenceSet({1, -1, 4})
       >>> iset1 = IntervalSet([Range.new_open_right(0, 1), Range.new_open_right(1, 2)])
       >>> list(iter_domain_endpoints([eq1, iset1]))
       [-1, 4, 0, 2]

    """
    for domain in domains:
        if isinstance(domain, EquivalenceSet):
            yield min(domain.values)
            if len(domain.values) > 1:
                yield max(domain.values)
        elif isinstance(domain, IntervalSet):
            # IntervalSet keep their ranges sorted by the lower bound, so the
            # first has the minimal value.
            yield domain.ranges[0].lowerbound
            yield max(r.upperbound for r in domain.ranges)
        else:
            assert False, f"Unknown type of domain {domain.__class__}"


if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime, timedelta

    def check(domain: Domain) -> None:
        return None

    def check_subdomain(domain: Domain[datetime]) -> None:
        return None

    check(EquivalenceSet({1}))
    check(
        Range.new_open_right(
            datetime.now(), datetime.now() + timedelta(1)
        ).lift()
    )
    check_subdomain(
        Range.new_open_right(
            datetime.now(), datetime.now() + timedelta(1)
        ).lift()
    )
