def mutazip(a, b, fn):
    i = len(a)
    while (i := i - 1) >= 0:
        a[i] = fn(a[i], b[i], i)
    return a
