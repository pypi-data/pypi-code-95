def init(h, w, func):
    return [[func(i, j) for j in range(w)] for i in range(h)]


def iso(h, w, val):
    return [[val] * w for _ in range(h)]
    # return [[val for _ in range(w)] for _ in range(h)]
