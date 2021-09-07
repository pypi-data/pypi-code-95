from veho.matrix import size


def mutazip(a, b, fn):
    h, w = size(a)
    while (h := h - 1) >= 0:
        ra, rb, y = a[h], b[h], w
        while (y := y - 1) >= 0:
            ra[y] = fn(ra[y], rb[y])
    return a
