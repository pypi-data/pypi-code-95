def iterate(entries, kfn, vfn=None):
    if vfn is None: vfn = kfn
    for (k, v) in entries: kfn(k), vfn(v)
    pass


def mapper(entries, kfn, vfn=None):
    if vfn is None: vfn = kfn
    return [(kfn(k), vfn(v)) for (k, v) in entries]


def mutate(entries, kfn, vfn=None):
    if vfn is None: vfn = kfn
    i, hi = 0, len(entries)
    while i < hi:
        k, v = entries[i]
        entries[i] = (kfn(k), vfn(v))
        i += 1
    return entries
