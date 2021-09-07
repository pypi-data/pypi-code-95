from veho.entries.enumerate.zipper.zipper import zipper


def duozipper(a, b, kfn, vfn=None):
    return zipper(a, b, kfn, vfn)


def trizipper(a, b, c, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(ak, bk, ck, i), vfn(av, bv, cv, i))
            for i, ((ak, av), (bk, bv), (ck, cv)) in enumerate(zip(a, b, c))]


def quazipper(a, b, c, d, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(ak, bk, ck, dk, i), vfn(av, bv, cv, dv, i))
            for i, ((ak, av), (bk, bv), (ck, cv), (dk, dv)) in enumerate(zip(a, b, c, d))]


def to_duozipper(kfn, vfn=None):
    return lambda a, b: duozipper(a, b, kfn, vfn)


def to_trizipper(kfn, vfn=None):
    return lambda a, b, c: trizipper(a, b, c, kfn, vfn)


def to_quazipper(kfn, vfn=None):
    return lambda a, b, c, d: quazipper(a, b, c, d, kfn, vfn)
