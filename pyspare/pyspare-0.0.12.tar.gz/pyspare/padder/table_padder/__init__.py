from aryth.bound.vector import max_by
from crostab import Table
from texting import DA, SP, lange, to_pad
from veho.columns import mapper as mapper_columns
from veho.matrix.enumerate import mapper as mapper_matrix
from veho.vector import mapper, zipper


def table_padder(table: Table, ansi=False, full_angle=False, fill=SP):
    # if (full_angle):
    padder = to_pad(ansi=ansi, fill=fill)
    length = lange if ansi else len
    widths = mapper_columns([table.head] + table.rows, lambda col: max_by(col, indicator=length))
    return Table(
        head=zipper(table.head, widths, lambda x, p: padder(x, p, x)),
        rule=mapper(widths, lambda p: DA * p),
        rows=mapper_matrix(table.rows, lambda x, i, j: padder(x, widths[j], x)),
        title=table.title
    )
