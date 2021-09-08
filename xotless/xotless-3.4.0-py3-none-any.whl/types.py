#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
# The idea is to support instances registration; then the inspector can be
# improved to find the right widget for the given instance of a typeclass
# annotation.
from typing import Any  # noqa
from typing import Optional, TypeVar

from typing_extensions import Protocol, runtime


class TypeClass(Protocol):
    pass


# fmt: off
class EqTypeClass(TypeClass, Protocol):  # pragma: no cover
    def __eq__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...


class OrdTypeClass(EqTypeClass, Protocol):  # pragma: no cover
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...


# fmt: on


T = TypeVar("T")
S = TypeVar("S", bound="Domain[Any]")
TEq = TypeVar("TEq", bound=EqTypeClass)
TOrd = TypeVar("TOrd", bound=OrdTypeClass)


@runtime
class Domain(Protocol[T]):  # pragma: no cover
    r"""A domain is a generalized type for homogeneous sets.

    It's not iterable because some sets are not iterable (e.g. the open
    interval ``(0-1)``).  There's also no notion of 'the next element'.
    Domains can also represent infinite sets (which are not representable by
    Python's sets).

    All values of a domain are of the same type `T`.  It's an error to mix
    domains of different types of values (``T``) in the operations below.

    """

    @property
    def sample(self: S) -> Optional[T]:
        """Produces a value which is a member of the domain.

        Some non-empty domains cannot produce a sample.  For instance,
        `~xotless.domains.IntervalSet`:class: comprising only open ranges
        cannot produce a sample.  They return None.

        Different calls to `sample` should produce the same value.

        """
        ...

    def union(self: S, *others: S) -> S:
        "Return a domain containing elements of `self` or `other`."
        ...

    def __contains__(self, which: T) -> bool:
        "Return True if `which` is a member."
        ...

    def __sub__(self: S, other: S) -> S:
        "Return a domain containing elements of `self` which are not members of `other`."
        ...

    def __or__(self: S, other: S) -> S:
        "Equivalent to `union`:meth:."
        ...

    def __le__(self: S, other: S) -> bool:
        "Return True if `self` is sub-set of `other`"
        ...

    def __lt__(self: S, other: S) -> bool:
        "Return True if `self` is a proper sub-set of `other`"
        ...

    def __ge__(self: S, other: S) -> bool:
        "Return True if `other` is a sub-set of `self`"
        ...

    def __gt__(self: S, other: S) -> bool:
        "Return True if `other` is a proper sub-set of `self`"
        ...

    def __and__(self: S, other: S) -> S:
        "Return a domain containing common elements of `self` and `other`."
        ...

    def __bool__(self: S) -> bool:
        "Return True if the domain is not empty."
        ...
