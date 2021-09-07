def margin_shallow(entries, h, t):
    return [(k, v) for k, v in entries[:h]] + [(k, v) for k, v in entries[-t:]]


def margin_mapper(entries, kfn, vfn, h, t):
    if vfn is None: vfn = kfn
    return [(kfn(k, i), vfn(v, i)) for i, (k, v) in enumerate(entries[:h])] + \
           [(kfn(k, i), vfn(v, i)) for i, (k, v) in enumerate(entries[-t:])]


def margin_mutate(vec, kfn, vfn, h, t):
    if vfn is None: vfn = kfn
    s = (d := len(vec)) - t
    while (h := h - 1) >= 0:
        k, v = vec[h]
        vec[h] = (kfn(k, h), vfn(v, h))
    while (d := d - 1) >= s:
        k, v = vec[d]
        vec[d] = (kfn(k, d), vfn(v, d))
    return vec
