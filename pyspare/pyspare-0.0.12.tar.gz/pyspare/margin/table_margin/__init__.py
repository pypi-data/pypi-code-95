from crostab import Table

from pyspare.margin.matrix_margin import matrix_margin
from pyspare.margin.vector_margin import vector_margin


def table_margin(table: Table, top, bottom, left, right, height, width, read, head_read, rule):
    return Table(
        head=vector_margin(table.head, left, right, head_read, rule),
        rows=matrix_margin(table.rows, top, bottom, left, right, height, width, read, rule),
        title=table.title
    )
