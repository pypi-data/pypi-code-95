from .matrix_margin import MatrixMargin
from .sizing import sizing


def matrix_margin(mx, top, bottom, left, right, height, width, read, rule):
    return MatrixMargin \
        .build(mx, top, bottom, left, right, height, width) \
        .stringify(read) \
        .to_matrix(rule)
