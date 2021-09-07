def zipper(ma, mb, fn):
    zipped = list(zip(ma, mb))
    for (i, (ra, rb)) in enumerate(zipped):
        zipped[i] = (fn(a, b) for (a, b) in zip(ra, rb))
    return zipped
