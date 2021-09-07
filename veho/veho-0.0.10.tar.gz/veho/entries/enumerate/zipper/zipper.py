def zipper(a, b, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(ak, bk, i), vfn(av, bv, i))
            for i, ((ak, av), (bk, bv)) in enumerate(zip(a, b))]
