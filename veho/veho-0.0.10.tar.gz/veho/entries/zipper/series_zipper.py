from veho.entries.zipper.zipper import zipper


def duozipper(a, b, kfn, vfn=None):
    return zipper(a, b, kfn, vfn)


def trizipper(a, b, c, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(ak, bk, ck), vfn(av, bv, cv))
            for ((ak, av), (bk, bv), (ck, cv)) in zip(a, b, c)]


def quazipper(a, b, c, d, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(ak, bk, ck, dk), vfn(av, bv, cv, dv))
            for ((ak, av), (bk, bv), (ck, cv), (dk, dv)) in zip(a, b, c, d)]


def to_duozipper(kfn, vfn=None):
    return lambda a, b: duozipper(a, b, kfn, vfn)


def to_trizipper(kfn, vfn=None):
    return lambda a, b, c: trizipper(a, b, c, kfn, vfn)


def to_quazipper(kfn, vfn=None):
    return lambda a, b, c, d: quazipper(a, b, c, d, kfn, vfn)
