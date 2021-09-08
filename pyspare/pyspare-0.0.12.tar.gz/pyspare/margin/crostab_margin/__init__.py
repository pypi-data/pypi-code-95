from crostab import Crostab

from pyspare.margin.matrix_margin import matrix_margin
from pyspare.margin.vector_margin import vector_margin


def crostab_margin(crostab: Crostab, top, bottom, left, right, height, width, read, side_read, head_read, rule):
    # print(matrix_margin(crostab.rows, top, bottom, left, right, height, width, read, rule))
    return Crostab(
        side=vector_margin(crostab.side, top, bottom, side_read, rule),
        head=vector_margin(crostab.head, left, right, head_read, rule),
        rows=matrix_margin(crostab.rows, top, bottom, left, right, height, width, read, rule),
        title=crostab.title
    )
