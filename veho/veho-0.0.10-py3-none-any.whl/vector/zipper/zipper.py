def zipper(a, b, fn):
    return [fn(x, y) for (x, y) in zip(a, b)]
