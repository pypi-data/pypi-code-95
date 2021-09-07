from typing import List

from intype import is_numeric
from veho.matrix import iso, size

from aryth.structs import TagList, Select


def solebound(
        mx: List[list],
        opt: Select = Select(is_numeric, float)
):
    h, w = size(mx)
    matrix, count, when, to = iso(h, w, None), 0, opt.when, opt.to
    ma = mi = None
    for i, row in enumerate(mx):
        for j, v in enumerate(row):
            if when(v) and (count := count + 1):
                matrix[i][j] = v = to(v) if to else v
                if mi is None: ma = mi = v
                if v > ma:
                    ma = v
                elif v < mi:
                    mi = v
    return TagList(matrix, min=mi, max=ma, count=count)
