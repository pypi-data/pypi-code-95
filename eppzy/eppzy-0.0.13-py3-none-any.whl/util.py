from datetime import datetime


def parse_datetime(s):
    try:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


class Add:
    __slots__ = 'v',

    def __init__(self, v):
        self.v = v


class Rem:
    __slots__ = 'v',

    def __init__(self, v):
        self.v = v


def partition(pred, transform, iterable):
    t = []
    f = []
    for i in iterable:
        if pred(i):
            t.append(transform(i))
        else:
            f.append(transform(i))
    return t, f


def _is_add(v):
    if type(v) is Rem:
        return False
    elif type(v) is Add:
        return True
    else:
        raise ValueError("Neither Add nor Rem")


def map_partition_rem(f, iterable):
    return partition(_is_add, lambda i: f(i.v), iterable)


def map_partition_rem_dict(f, d):
    return partition(
        lambda p: _is_add(p[1]),
        lambda p: f(p[0], p[1].v),
        d.items())
