from typing import List

from intype import has_literal, is_numeric
from texting.str_value import str_value
from veho.matrix import iso, size

from aryth.structs import Select, TagList


def duobound(
        mx: List[list],
        opt_x: Select = Select(is_numeric, float),
        opt_y: Select = Select(has_literal, str_value)
):
    height, width = size(mx)
    mx_x, count_x, when_x, to_x = iso(height, width, None), 0, opt_x.when, opt_x.to
    mx_y, count_y, when_y, to_y = iso(height, width, None), 0, opt_y.when, opt_y.to
    max_x = max_y = min_x = min_y = None
    for i, row in enumerate(mx):
        for j, v in enumerate(row):
            if when_x(v) and (count_x := count_x + 1):
                mx_x[i][j] = v = to_x(v) if to_x else v
                if min_x is None: max_x = min_x = v
                if v > max_x:
                    max_x = v
                elif v < min_x:
                    min_x = v
            elif when_y(v) and (count_y := count_y + 1):
                mx_y[i][j] = v = to_y(v) if to_y else v
                if min_y is None: max_y = min_y = v
                if v > max_y:
                    max_y = v
                elif v < min_y:
                    min_y = v
    return (TagList(mx_x, min=min_x, max=max_x, count=count_x),
            TagList(mx_y, min=min_y, max=max_y, count=count_y))
