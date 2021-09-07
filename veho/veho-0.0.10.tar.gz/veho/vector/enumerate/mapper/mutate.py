def mutate(vec, fn):
    i = 0
    size = len(vec)
    while i < size:
        vec[i] = fn(vec[i], i)
        i += 1
    return vec
