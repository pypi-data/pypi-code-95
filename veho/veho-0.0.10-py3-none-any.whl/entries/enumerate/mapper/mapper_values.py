def iterate_values(entries, vfn):
    i, hi = 0, len(entries)
    while i < hi:
        _, v = entries[i]
        vfn(v, i)
        i += 1
    pass


def mapper_values(entries, vfn):
    return [(k, vfn(v, i)) for i, (k, v) in enumerate(entries)]


def mutate_values(entries, vfn):
    i, hi = 0, len(entries)
    while i < hi:
        k, v = entries[i]
        entries[i] = (k, vfn(v, i))
        i += 1
    return entries
