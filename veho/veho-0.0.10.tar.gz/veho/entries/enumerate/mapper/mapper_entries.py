def iterate(entries, kfn, vfn=None):
    if vfn is None: vfn = kfn
    i, hi = 0, len(entries)
    while i < hi:
        k, v = entries[i]
        kfn(k, i)
        vfn(v, i)
        i += 1
    pass


def mapper(entries, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(k, i), vfn(v, i)) for i, (k, v) in enumerate(entries)]


def mutate(entries, kfn, vfn=None):
    if vfn is None: vfn = kfn
    i, hi = 0, len(entries)
    while i < hi:
        k, v = entries[i]
        entries[i] = (kfn(k, i), vfn(v, i))
        i += 1
    return entries
