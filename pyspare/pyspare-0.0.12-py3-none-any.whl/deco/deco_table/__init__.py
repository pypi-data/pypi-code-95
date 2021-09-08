from ject import oneself
from palett import fluo_matrix, fluo_vector
from palett.presets import FRESH, PLANET
from texting import AEU, COSP, ELLIP, liner
from texting.enum.brackets import BRK
from veho.enum.matrix_directions import COLUMNWISE
from veho.matrix import size
from veho.vector import mapper

from pyspare.margin import MatrixMargin, VectorMargin, table_margin
from pyspare.padder import table_padder
from pyspare.padder.matrix_padder import matrix_padder


def deco_table(table,
               discrete=False,
               read=None,
               head_read=None,
               presets=(FRESH, PLANET),
               direct=COLUMNWISE,
               top=0,
               bottom=0,
               left=0,
               right=0,
               ansi=False,
               full_angle=False,
               level=0,
               rule=ELLIP):
    height, width = size(table.rows)
    label_width = len(table.head)
    if not height or not width or not label_width: return AEU
    table = table_margin(table, top, bottom, left, right, height, width, read, head_read, rule)
    table = table_padder(table, ansi, full_angle)
    if presets:
        table = table.boot(
            head=fluo_vector(table.head, presets, mutate=True),
            rows=fluo_matrix(table.rows, direct, presets, mutate=True)
        )
    lines = [' | '.join(table.head),
             '-+-'.join(table.rule)]
    lines.extend(mapper(table.rows,
                        lambda row: ' | '.join(row)))
    return liner(lines, level=level, discrete=discrete)


def deco_table_arch(table,
                    discrete=False,
                    delim=COSP,
                    bracket=BRK,
                    read=None,
                    head_read=None,
                    presets=(FRESH, PLANET),
                    direct=COLUMNWISE,
                    top=0,
                    bottom=0,
                    left=0,
                    right=0,
                    ansi=False,
                    full_angle=False,
                    level=0,
                    hr=ELLIP):
    head = table['head'], rows = table['rows']
    height, width = size(rows)
    label_width = len(head)
    if not height or not width or not label_width: return AEU
    head_margin, rows_margin = (VectorMargin.build(head, left, right),
                                MatrixMargin.build(rows, top, bottom, left, right, height, width))
    head_raw, rows_raw = (head_margin.map(oneself).to_list(ELLIP),
                          rows_margin.map(oneself).to_matrix(hr))
    head_alt, rows_alt = (head_margin.stringify(read).to_list(ELLIP),
                          rows_margin.stringify(read).to_matrix(hr))
    rows_dye, head_dye = (fluo_vector(head_raw, direct, presets, colorant=True),
                          fluo_matrix(rows_raw, direct, presets, colorant=True)) \
        if presets else (None, None)
    rows = matrix_padder(rows_alt, rows_raw, rows_dye, ansi)
