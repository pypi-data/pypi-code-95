#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from itertools import product
from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence, Tuple, cast

from xotl.tools.future.itertools import iter_without_duplicates
from xotl.tools.objects import memoized_property
from xotl.tools.symbols import Unset as _Unset

from .types import AVM, AttributeLocator, Domain, _MutableAVM

Unset = cast(Sequence[Domain], _Unset)


class Combinator(AVM):
    bases: Tuple[AVM, ...]

    def __new__(cls, *bases: AVM) -> AVM:  # type: ignore
        # Ignores empty bases, and if possible avoid the combinator
        # altogether.
        #
        # Q: Can an intersection combinator ignore the empty bases?  An empty
        # AVM indicates that no attribute is known to affect the price.
        # However, an empty domain for a given attribute indicates that the
        # attribute was known to affect the price, but, somehow, there's no
        # known value.
        bases = tuple(filter(bool, bases))
        if len(bases) == 1:
            return bases[0]
        else:
            res = super().__new__(cls)
            res.bases = bases
            return res

    def __init__(self, *bases: AVM) -> None:
        # Don't set bases here, we manipulate them and set them in __new__
        self._cache: _MutableAVM = {}
        self._keys = None

    def __iter__(self):
        if self._keys is None:
            self._keys = ()
            for base in self.bases:
                for key in base:
                    # We need to be sure the key is indeed present in `self`.
                    # Otherwise FilteringAVM below may report a key it
                    # filters, and then calling `self.items()` would produce a
                    # KeyError.  See issue #933
                    # (https://gitlab.merchise.org/mercurio-2018/xhg2/issues/933)
                    if key not in self._keys and self.get(key, Unset) is not Unset:
                        yield key
                        self._keys += (key,)
        else:
            yield from iter(self._keys)

    @memoized_property
    def length(self):
        return sum(1 for _ in self)

    def __len__(self):
        return self.length

    def __repr__(self):
        cls = type(self).__name__
        bases = ", ".join(repr(base) for base in self.bases)
        return f"{cls}({bases})"


class CombinedAVM(Combinator):
    "The union-based combination of several base AVMs."

    def __getitem__(self, item):
        res = self._cache.get(item, Unset)
        if res is Unset:
            layers: List[Sequence[Domain]] = []
            for base in self.bases:
                domains = base.get(item, [])
                if domains:
                    layers.append(domains)
            if not layers:
                raise KeyError(item)
            for index, layer in enumerate(layers):
                if not index:
                    last: Sequence[Domain] = layer
                else:
                    last = [new | previous for previous, new in product(last, layer)]
            self._cache[item] = res = last
        return res


class CascadingAVM(Combinator):
    """A cascading-based combination of several AVMs.

    Cascade means that if two base AVMs share the same attribute, its values
    will be computed by cascading the differences between the domains of first
    bases and the later one.

    Cascading is not commutative.

    """

    def __getitem__(self, item: AttributeLocator) -> Sequence[Domain]:
        res: Sequence[Domain] = self._cache.get(item, Unset)
        if res is Unset:
            layers: List[Sequence[Domain]] = []
            for base in self.bases:
                domains = base.get(item, [])
                if domains:
                    layers.append(domains)
            if not layers:
                raise KeyError(item)
            last_index = len(layers) - 1
            for index, layer in enumerate(layers):
                if not index:
                    last: Sequence[Domain] = layer
                elif index != last_index:
                    last = [new | previous for previous, new in product(last, layer)]
                else:
                    assert index == last_index
                    diffs = [new - previous for previous, new in product(last, layer)]
                    last = list(filter(bool, diffs))
            self._cache[item] = res = last
        return res


class FilteringAVM(Combinator):
    """A filter-based combination of several AVMs.

    Filter means that if two base AVMs share the same attribute, its value
    will be computed by intersecting the domain of the bases.


    """

    def __getitem__(self, item: AttributeLocator) -> Sequence[Domain]:
        res = self._cache.get(item, Unset)
        if res is Unset:
            layers: List[Sequence[Domain]] = []
            for base in self.bases:
                domains = base.get(item, [])
                if domains:
                    layers.append(domains)
            if not layers:
                raise KeyError(item)
            for index, layer in enumerate(layers):
                if not index:
                    last: Sequence[Domain] = layer
                else:
                    last = list(
                        filter(
                            bool,
                            (new & previous for previous, new in product(last, layer)),
                        )
                    )
            self._cache[item] = res = last
        return res


class MergedAVM(Combinator):
    """A naive merging of AVMs.

    Each key keeps exactly the same domains in the bases.

    """

    def __getitem__(self, item: AttributeLocator) -> Sequence[Domain]:
        res = self._cache.get(item, Unset)
        if res is Unset:
            domains = tuple(
                iter_without_duplicates(
                    domain
                    for base in self.bases
                    for _domains in [base.get(item, Unset)]
                    if _domains is not Unset
                    for domain in _domains
                )
            )
            if domains:
                res = self._cache[item] = domains
            else:
                raise KeyError(item)
        return res


def BranchingAVM(bases: Iterable[Tuple[AVM, AVM]]) -> AVM:
    """Computes the AVM of branching procedures.

    The items of `bases` are the pair of the predicate's AVM and the AVM of
    the sub-procedure of the matching branch.

    While computing the branch AVM, each branch gets an AVM which is computed
    from the `cascade <CascadingAVM>`:class: of the predicates of previous
    branches (so that we keep track which values actually reach the branch),
    and then we must `filter <FilteringAVM>`:class: with the sub-procedure's
    AVM.  All branches are then `merged <MergeAVM>`:class: so that we can keep
    the domains of each branch separated.

    """
    # We explained abundantly that combined AVMs for BranchProcedure are more
    # complex than union-based combined AVMs.
    #
    # See the document ``xhg2/docs/papers/2019-05-09-price-tables.rst``.
    #
    # Cascading is only performed between the AVMs of predicates; filtering
    # happens before returning the combinated AVM at each branch's cascaded
    # AVM and the branche's procedure.
    branches: List[AVM] = []
    cascade: Optional[AVM] = None
    for pred, proc in bases:
        if cascade is None:
            cascade = pred
        else:
            if isinstance(cascade, CascadingAVM):
                # Create a single flat cascade out of all the bases.  This may impact
                # adversely in the _cache (it won't be shared by branches) but cascading
                # is not associative:
                #
                #    CascadingAVM(a1, a2, a3) != CascadingAVM(CascadingAVM(a1, a2), a3)
                #
                # The first is like ``a3 - (a2 | a1)``; whereas the second is
                # a3 - (a2 - a1) -- sets differences.  In the second case elements in a1
                # that are also in a3 remain in the result (they are not in a2 - a1):
                #
                # >>> a3 = {1, 2, 3, 4}
                # >>> a2 = {1, 2}
                # >>> a1 = {3, 4}
                #
                # >>> a3 - (a2 - a1)
                # {3, 4}
                #
                # >>> (a3 - a2) - a1
                # set()
                #
                cascade = CascadingAVM(*cascade.bases, pred)
            else:
                cascade = CascadingAVM(cascade, pred)
        filtered = FilteringAVM(cascade, proc)
        branches.append(filtered)
    return MergedAVM(*branches)


def combine_avms(*many_bases: Iterable[AVM]) -> AVM:
    """Combine several base AMVs."""
    return CombinedAVM(*(base for bases in many_bases for base in bases))


def merge_avms(*many_bases: Iterable[AVM]) -> AVM:
    return MergedAVM(*(base for bases in many_bases for base in bases))


def is_valid_avm(avm: AVM) -> bool:
    from itertools import combinations

    return not any(any(d1 & d2 for d1, d2 in combinations(avm[attr], 2)) for attr in avm)


if TYPE_CHECKING:

    is_valid_avm(CombinedAVM())
    is_valid_avm(CascadingAVM())
    is_valid_avm(FilteringAVM())
    is_valid_avm(BranchingAVM([]))
