from veho.vector.enumerate.zipper.zipper import zipper


def duozipper(a, b, fn):
    return zipper(a, b, fn)


def trizipper(a, b, c, fn):
    return [fn(x, y, z, i) for i, (x, y, z) in enumerate(zip(a, b, c, ))]


def quazipper(a, b, c, d, fn):
    return [fn(x1, x2, x3, x4, i) for i, (x1, x2, x3, x4) in enumerate(zip(a, b, c, d))]


def to_duozipper(fn):
    return lambda a, b: duozipper(a, b, fn)


def to_trizipper(fn):
    return lambda a, b, c: trizipper(a, b, c, fn)


def to_quazipper(fn):
    return lambda a, b, c, d: quazipper(a, b, c, d, fn)
