from functools import partial, reduce

from veho.matrix import size

from aryth.bound.vector.indicator import max_by as max_vec_by, min_by as min_vec_by
from aryth.comparison import max_indicate, min_indicate


def max_by(mx, indicator=None, initial=None):
    h, w = size(mx)
    if not h or not w: return initial
    if initial is None: initial = indicator(mx[0][0]) if indicator else mx[0][0]
    compare = partial(max_indicate, indicator=partial(max_vec_by, indicator=indicator, initial=initial))
    return reduce(compare, mx, initial)


def min_by(mx, indicator=None, initial=None):
    h, w = size(mx)
    if not h or not w: return initial
    if initial is None: initial = indicator(mx[0][0]) if indicator else mx[0][0]
    compare = partial(min_indicate, indicator=partial(min_vec_by, indicator=indicator, initial=initial))
    return reduce(compare, mx, initial)
