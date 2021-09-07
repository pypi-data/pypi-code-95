def mutate(vec, fn):
    i, hi = 0, len(vec)
    while i < hi:
        vec[i] = fn(vec[i])
        i += 1
    return vec
