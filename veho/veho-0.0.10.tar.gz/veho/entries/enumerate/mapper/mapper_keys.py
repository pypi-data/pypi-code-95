def iterate_keys(entries, kfn):
    i, hi = 0, len(entries)
    while i < hi:
        k, = entries[i]
        kfn(k, i)
        i += 1
    pass


def mapper_keys(entries, kfn):
    return [(kfn(k, i), v) for i, (k, v) in enumerate(entries)]


def mutate_keys(entries, kfn):
    i, hi = 0, len(entries)
    while i < hi:
        k, v = entries[i]
        entries[i] = (kfn(k, i), v)
        i += 1
    return entries
