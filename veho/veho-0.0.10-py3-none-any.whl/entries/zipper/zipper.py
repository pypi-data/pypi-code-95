def zipper(a, b, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(ak, bk), vfn(av, bv))
            for ((ak, av), (bk, bv)) in zip(a, b)]
