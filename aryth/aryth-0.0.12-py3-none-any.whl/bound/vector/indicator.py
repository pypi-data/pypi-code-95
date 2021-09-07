from functools import partial, reduce

from aryth.comparison import max_compare, max_indicate, min_compare, min_indicate


def max_by(vec, indicator=None, initial=None):
    if not len(vec): return initial
    if initial is None: initial = indicator(vec[0]) if indicator else vec[0]
    compare = partial(max_indicate, indicator=indicator) if indicator else max_compare
    return reduce(compare, vec, initial)


def min_by(vec, indicator=None, initial=None):
    if not len(vec): return initial
    if initial is None: initial = indicator(vec[0]) if indicator else vec[0]
    compare = partial(min_indicate, indicator=indicator) if indicator else min_compare
    return reduce(compare, vec, initial)
