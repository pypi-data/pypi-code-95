#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from xotless.itertools import CyclicInteger, CyclicLine, Line


@given(st.integers(), st.integers(min_value=1), st.integers())
def test_cyclic_integer_range(x, mod, y):
    assert 0 <= CyclicInteger(x, mod) < mod
    assert 0 <= CyclicInteger(x, mod) + y < mod
    assert 0 <= CyclicInteger(x, mod) - y < mod


@given(st.lists(st.integers(), min_size=0))
@example([])
def test_possible_empty_line(instances):
    l = Line.from_iterable(instances)
    assert list(instances) == list(l)
    l.seek(object())


@given(st.lists(st.integers(), min_size=1))
def test_line(instances):
    l = Line(*instances)
    assert list(instances) == list(l)

    l = Line(*instances)
    assert l.current == instances[0]
    assert l.beginning

    l = Line(*instances, start=-1)
    assert l.ending


@given(st.lists(st.integers(), min_size=2), st.integers())
def test_line_next(instances, pos):
    l = Line(*instances, start=pos)
    pos = l.pos
    try:
        l.next()
    except StopIteration:
        pass
    else:
        assert l.pos == pos + 1


@given(st.lists(st.integers(), min_size=2, max_size=100), st.integers())
def test_line_back(instances, pos):
    l = Line(*instances, start=pos)
    pos = l.pos
    try:
        l.back()
    except StopIteration:
        pass
    else:
        assert l.pos == pos - 1


@given(st.lists(st.integers(), min_size=2, max_size=100), st.integers())
def test_line_back_inverse_of_next(instances, pos):
    l = Line(*instances, start=pos)
    r = ~l
    try:
        previous = l.back()
        try:
            assert r.next() == previous
        except StopIteration:
            assert (
                False
            ), "If I can go back in l, I must be able to forward in ~l"
    except StopIteration:
        pass


@given(st.lists(st.integers(), min_size=2, max_size=100), st.integers())
def test_line_next_inverse_of_back(instances, pos):
    l = Line(*instances, start=pos)
    r = ~l
    try:
        following = l.next()
        try:
            assert r.back() == following
        except StopIteration:
            assert (
                False
            ), "If I can go forward in l, I must be able to back in ~l"
    except StopIteration:
        pass


@given(st.lists(st.integers(), min_size=2, max_size=100))
def test_line_back_after_next(instances):
    l = Line(*instances)
    pos = l.pos
    l.next()  # I know I can do this since instances has at least 2 items
    # After a successful next, we expect we can go back.
    l.back()
    assert l.pos == pos


@given(st.lists(st.integers(), min_size=1, max_size=100))
def test_line_at_end(instances):
    l = Line(*instances, start=-1)
    assert l.ending
    pos = l.pos
    l.next()  # At the end, there's still one item left in the iterator
    assert l.pos == pos + 1
    with pytest.raises(StopIteration):
        l.next()
    assert l.pos == pos + 1, "If next() failed we stay where we were"


@given(st.lists(st.integers(), min_size=1, max_size=100))
def test_line_at_beginning(instances):
    l = Line(*instances, start=0)
    assert l.beginning
    pos = l.pos
    # At the beginning, there's still one item left in the reversed iterator
    l.back()
    assert l.pos == pos - 1
    with pytest.raises(StopIteration):
        l.back()
    assert l.pos == pos - 1, "If back() failed we stay where we were"


@given(st.lists(st.integers(), max_size=100), st.data())
def test_seek1(instances, data):
    if instances:
        positions = st.integers(min_value=0, max_value=len(instances) - 1)
        pos = data.draw(positions)
        pos2 = data.draw(positions)
        what = max(instances) + 1  # this won't be in the line
    else:
        pos = pos2 = 0
        what = -1
    instances[pos:pos] = [what]
    l = Line(*instances, start=pos2)
    l.seek(what)
    assert l.pos == pos


@given(st.lists(st.integers(), max_size=100), st.data())
def test_seek2(instances, data):
    if instances:
        positions = st.integers(min_value=0, max_value=len(instances) - 1)
        pos = data.draw(positions)
        what = max(instances) + 1  # this won't be in the line
    else:
        pos = 0
        what = -1
    l = Line(*instances, start=pos)
    l.seek(what)
    assert l.pos == pos


class _distinct(object):
    pass


@st.composite
def distinct(draw):
    return _distinct()


@given(st.lists(distinct(), min_size=2, max_size=100), st.integers())
def test_line_invert_leave_current(instances, pos):
    l = Line(*instances, start=pos)
    # Notice instances are not integers and that we use `is` instead of `==`,
    # so truly the same object.
    assert l.current is (~l).current


def test_singleton_line():
    l = Line(1)
    assert l
    assert l.beginning
    assert l.ending


def test_empty_line():
    l = Line()
    assert list(l) == []

    l = Line()
    assert list(l) == []

    assert list(~l) == list(l)

    with pytest.raises(IndexError):
        l.current

    assert not l
    assert l.beginning  # beginning is ill-defined for an empty list
    assert not l.ending


@given(st.lists(distinct(), max_size=100), st.integers())
def test_ending_entails_no_posterior(instances, pos):
    l = Line(*instances, start=pos)
    if l.ending:
        with pytest.raises(IndexError):
            l.posterior


@given(st.lists(distinct(), max_size=100), st.integers())
def test_beginning_entails_no_anterior(instances, pos):
    l = Line(*instances, start=pos)
    if l.beginning:
        with pytest.raises(IndexError):
            l.anterior


@given(
    st.lists(distinct(), max_size=50),
    st.lists(distinct(), max_size=50),
    st.integers(),
    st.integers(),
)
def test_line_addition(xs, ys, pos, pos2):
    lxs = Line(*xs, start=pos)
    lys = Line(*ys, start=pos2)
    lxys = lxs + lys
    assert lxs.pos == lxys.pos
    assert list(lxs) + list(lys) == list(lxys)

    lxys = lxs + ys
    assert lxs.pos == lxys.pos
    assert list(lxs) + list(ys) == list(lxys)

    lxys = ys + lxs
    assert lxs.pos == lxys.pos
    assert list(ys) + list(lxs) == list(lxys)


@given(
    st.lists(distinct(), max_size=10),
    st.integers(),
    # the multiplier reasonable small
    st.integers(min_value=-100, max_value=100),
)
def test_line_multiplication(xs, pos, times):
    lxs = Line(*xs, start=pos)
    lxys = lxs * times
    assert lxs.pos == lxys.pos
    assert list(lxs) * times == list(lxys)

    lxys = times * lxs
    assert lxs.pos == lxys.pos
    assert times * list(lxs) == list(lxys)


@given(
    st.lists(st.integers(), min_size=10, max_size=100),
    st.integers(min_value=10, max_value=100),
)
def test_cyclic_line_backandforth_forever(items, times):
    length = len(items)
    l = CyclicLine(*items)
    assert not l.beginning and not l.ending
    for _ in range(times + length):
        l.next()
    l = CyclicLine(*items)
    for _ in range(times + length):
        l.back()


def test_non_possible_empty_cyclic_lines():
    with pytest.raises(TypeError):
        CyclicLine()


@given(st.integers(), st.integers(min_value=1))
def test_cycle_integers_are_pickable(x, l):
    import pickle

    c = CyclicInteger(x, l)
    assert c == pickle.loads(pickle.dumps(c))
    assert c == pickle.loads(pickle.dumps(c, pickle.HIGHEST_PROTOCOL))
