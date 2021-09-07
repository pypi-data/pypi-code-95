from ject import length


def margin_shallow(vec, h, t):
    return vec[:h] + vec[-t:]


def margin_mapper(vec, fn, h, t):
    if (n := length(fn)) == 1:
        return [fn(x) for x in vec[:h]] + [fn(x) for x in vec[-t:]]
    if n == 2:
        return [fn(x, i) for i, x in enumerate(vec[:h])] + [fn(x, i) for i, x in enumerate(vec[-t:])]
    return margin_shallow(vec, h, t)


def margin_mutate(vec, fn, h, t):
    s = (d := len(vec)) - t
    if (n := length(fn)) == 1:
        while (h := h - 1) >= 0: vec[h] = fn(vec[h])
        while (d := d - 1) >= s: vec[d] = fn(vec[d])
    elif n == 2:
        while (h := h - 1) >= 0: vec[h] = fn(vec[h], h)
        while (d := d - 1) >= s: vec[d] = fn(vec[d], d)
    return vec
