def iterate_keys(entries, kfn):
    i, hi = 0, len(entries)
    while i < hi:
        k, = entries[i]
        kfn(k)
        i += 1
    pass


def mapper_keys(entries, kfn):
    return [(kfn(k), v) for (k, v) in entries]


def mutate_keys(entries, kfn):
    i, hi = 0, len(entries)
    while i < hi:
        k, v = entries[i]
        entries[i] = (kfn(k), v)
        i += 1
    return entries
