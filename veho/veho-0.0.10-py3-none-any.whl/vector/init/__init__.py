def init(size, mapper):
    return [mapper(i) for i in range(size)]


def iso(size, value):
    return [value] * size
    # return [value for _ in range(size)]
