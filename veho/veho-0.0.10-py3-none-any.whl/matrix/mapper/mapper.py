def mapper(mx, fn):
    return [[fn(cell) for cell in row] for row in mx]
