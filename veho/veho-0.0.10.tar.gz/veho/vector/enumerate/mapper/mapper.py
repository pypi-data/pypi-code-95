def mapper(vec, fn):
    return [fn(x, i) for i, x in enumerate(vec)]
