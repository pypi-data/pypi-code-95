def mapper(mx, fn):
    return [[fn(cell, x, y) for y, cell in enumerate(row)] for x, row in enumerate(mx)]
