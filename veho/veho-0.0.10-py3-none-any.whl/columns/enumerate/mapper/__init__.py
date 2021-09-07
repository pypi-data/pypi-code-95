from veho.columns.getter import column
from veho.matrix import size


def iterate(mx, fn_on_column):
    _, w = size(mx)
    for j in range(w):
        col = column(mx, j)
        fn_on_column(col, j)
    pass


def mapper(mx, fn_on_column):
    _, w = size(mx)
    return [fn_on_column(column(mx, j), j) for j in range(w)]
