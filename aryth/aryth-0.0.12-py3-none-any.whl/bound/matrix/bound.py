from intype import is_numeric
from veho.matrix import size


def bound(mx, dif=False):
    h, w = size(mx)
    (i, j, n) = init_numeral(mx)
    ma = mi = n
    if n is None or h is None:
        return dict(min=mi, dif=None) if dif else dict(min=mi, max=ma)
    while i < h:
        row = mx[i]
        while j < w:
            if is_numeric(x := row[j]):
                if (x := float(x)) < mi: mi = x
                elif x > ma: ma = x
            j += 1
        j = 0
        i += 1
    return dict(min=mi, dif=ma - mi) if dif else dict(min=mi, max=ma)


def init_numeral(mx):
    i = j = 0
    for i, r in enumerate(mx):
        for j, x in enumerate(r):
            if is_numeric(x): return i, j, float(x)
    return i + 1, j + 1, None
