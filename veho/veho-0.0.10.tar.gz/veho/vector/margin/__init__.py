def margin_shallow(vec, h, t):
    return vec[:h] + vec[-t:]


def margin_mapper(vec, fn, h, t):
    return [fn(x) for x in vec[:h]] + [fn(x) for x in vec[-t:]]


def margin_mutate(vec, fn, h, t):
    s = (d := len(vec)) - t
    while (h := h - 1) >= 0: vec[h] = fn(vec[h])
    while (d := d - 1) >= s: vec[d] = fn(vec[d])
    return vec

# if (n := length(fn)) == 1:
