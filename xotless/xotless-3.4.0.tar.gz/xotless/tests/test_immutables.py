#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import doctest
from dataclasses import dataclass
from typing import Any

from hypothesis import given
from hypothesis import strategies as s
from hypothesis.strategies import SearchStrategy

import xotless.immutables
from xotless.immutables import ImmutableWrapper

from .support import captured_stderr, captured_stdout


def test_doctests():
    with captured_stdout() as stdout, captured_stderr() as stderr:
        failure_count, test_count = doctest.testmod(
            xotless.immutables,
            verbose=True,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            raise_on_error=False,
        )
    if test_count and failure_count:  # pragma: no cover
        print(stdout.getvalue())
        print(stderr.getvalue())
        raise AssertionError("ImmutableWrapper doctest failed")


def test_wrap_callable():
    class Bar:
        def return_self(self):
            return self

    class Foo(Bar):
        pass

    obj = Foo()
    wrapper = ImmutableWrapper(obj)
    assert wrapper.return_self() is obj

    wrapper2 = ImmutableWrapper(obj, wrap_callables=True)
    assert wrapper2.return_self() is wrapper2


def test_wrap_properties():
    from dataclasses import dataclass
    from datetime import datetime, timedelta

    @dataclass(frozen=True)
    class Commodity:
        start_date: datetime
        duration: timedelta

        @property
        def end_date(self):
            return self.start_date + self.duration

    now = datetime.utcnow()
    day = timedelta(1)
    item = ImmutableWrapper(
        Commodity(None, None), wrap_descriptors=True
    ).replace(start_date=now, duration=day)
    assert item.end_date == now + day

    commodity = Commodity(datetime.utcnow(), timedelta(1))
    assert hash(commodity) == hash(ImmutableWrapper(commodity))


def test_wrap_descriptors():
    class Descriptor:
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return id(instance)

    class Item:
        identity = Descriptor()

    item = ImmutableWrapper(Item(), wrap_descriptors=True)
    assert item.identity == id(item)


anything: SearchStrategy[Any] = s.integers() | s.floats() | s.text()
anything = (
    anything
    | s.dictionaries(s.text(), anything)
    | s.tuples(anything)
    | s.lists(anything)
)


@dataclass
class Obj:
    truth: bool

    def __bool__(self):
        return self.truth


@given(anything | s.from_type(Obj))
def test_boolean_values_basic(val):
    assert bool(ImmutableWrapper(val)) == bool(val)
