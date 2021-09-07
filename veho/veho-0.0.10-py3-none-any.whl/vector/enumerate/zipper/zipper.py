def zipper(a, b, fn):
    return [fn(x, y, i) for i, (x, y) in enumerate(zip(a, b))]
