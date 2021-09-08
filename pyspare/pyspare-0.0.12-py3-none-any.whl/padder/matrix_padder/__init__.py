from aryth.bound.vector import max_by
from texting import SP, lange, to_pad
from veho.columns import mapper as mapper_columns
from veho.matrix.enumerate import mapper


def matrix_padder(matrix, ansi=False, fill=SP):
    pad = to_pad(ansi=ansi, fill=fill)
    length = lange if ansi else len
    widths = mapper_columns(matrix, lambda col: max_by(col, indicator=length))
    return mapper(matrix, lambda x, i, j: pad(x, widths[j], x))
