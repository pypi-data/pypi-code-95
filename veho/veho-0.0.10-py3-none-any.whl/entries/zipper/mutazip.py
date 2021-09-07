def mutazip(a, b, kfn, vfn=None):
    if vfn is None: vfn = kfn
    hi = len(a)
    while (hi := hi - 1) >= 0:
        ak, av = a[hi]
        bk, bv = b[hi]
        a[hi] = (kfn(ak, bk), vfn(av, bv))
    return a
