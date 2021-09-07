from intype import is_numeric


def bound(vec, dif=False):
    hi = len(vec)
    (lo, n) = init_numeral(vec)
    ma = mi = n
    if dif and n is None: return dict(min=None, dif=None)
    while lo < (hi := hi - 1):
        if not is_numeric(x := vec[hi]): continue
        if (x := float(x)) < mi: mi = x
        elif x > ma: ma = x
    return dict(min=mi, dif=ma - mi) if dif else dict(min=mi, max=ma)


def init_numeral(vec):
    i = 0
    for i, x in enumerate(vec):
        if is_numeric(x):
            return i, float(x)
    return i + 1, None
