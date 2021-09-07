def zipper(ma, mb, fn):
    zipped = list(zip(ma, mb))
    for (i, (ra, rb)) in enumerate(zipped):
        zipped[i] = (fn(a, b, i, j) for j, (a, b) in enumerate(zip(ra, rb)))
    return zipped
