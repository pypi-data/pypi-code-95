from ject import oneself
from palett import fluo_matrix
from palett.presets import FRESH, PLANET
from texting import COLF, COSP, ELLIP, bracket as bracket_fn, liner, to_br
from texting.enum.brackets import BRK
from veho.enum.matrix_directions import ROWWISE
from veho.matrix import size
from veho.vector import mapper

from pyspare.margin import MatrixMargin, matrix_margin
from pyspare.padder.matrix_padder import matrix_padder


def deco_matrix(matrix,
                discrete=False,
                delim=COSP,
                bracket=BRK,
                read=None,
                presets=(FRESH, PLANET),
                direct=ROWWISE,
                top=0,
                bottom=0,
                left=0,
                right=0,
                ansi=False,
                level=0,
                rule=ELLIP):
    if not matrix: return str(matrix)
    height, width = size(matrix)
    if not height or not width: return liner([], delim, level, bracket, discrete)
    matrix = matrix_margin(matrix, top, bottom, left, right, height, width, read, rule)
    matrix = matrix_padder(matrix, ansi)
    if presets: fluo_matrix(matrix, direct, presets, colorant=False, mutate=True)
    lines = mapper(matrix, lambda line: br(delim.join(line))) \
        if (br := to_br(bracket)) \
        else mapper(matrix, lambda line: delim.join(line))
    return liner(lines, delim=COLF, bracket=bracket, level=level, discrete=discrete)


def deco_matrix_arch(matrix,
                     discrete=False,
                     delim=COSP,
                     bracket=BRK,
                     read=None,
                     presets=(FRESH, PLANET),
                     direct=ROWWISE,
                     top=0,
                     bottom=0,
                     left=0,
                     right=0,
                     ansi=False,
                     level=0,
                     rule=ELLIP):
    if not matrix: return str(matrix)
    height, width = size(matrix)
    if not height or not width: return liner([], delim, level, bracket, discrete)
    vn = MatrixMargin.build(matrix, top, bottom, left, right, height, width)
    raw, text = vn.map(oneself).to_matrix(rule), vn.stringify(read).to_matrix(rule)
    dye = fluo_matrix(raw, direct, presets, colorant=True) if presets else None
    rows = matrix_padder(text, raw, dye, ansi)
    lines = mapper(rows, lambda line: bracket_fn(delim.join(line))) \
        if bracket \
        else mapper(rows, lambda line: delim.join(line))
    return liner(lines, delim=COLF, bracket=bracket, level=level, discrete=discrete)
