from intype import has_literal, is_numeric
from texting.str_value import str_value

from aryth.structs import Select, TagList


def duobound(
        vec: list,
        opt_x: Select = Select(is_numeric, float),
        opt_y: Select = Select(has_literal, str_value)
):
    size = len(vec)
    vec_x, count_x, when_x, to_x = [None] * size, 0, opt_x.when, opt_x.to
    vec_y, count_y, when_y, to_y = [None] * size, 0, opt_y.when, opt_y.to
    max_x = max_y = min_x = min_y = None
    for i, v in enumerate(vec):
        if when_x(v) and (count_x := count_x + 1):
            vec_x[i] = v = to_x(v) if to_x else v
            if min_x is None: max_x = min_x = v
            if v > max_x:
                max_x = v
            elif v < min_x:
                min_x = v
        elif when_y(v) and (count_y := count_y + 1):
            vec_y[i] = v = to_y(v) if to_y else v
            if min_y is None: max_y = min_y = v
            if v > max_y:
                max_y = v
            elif v < min_y:
                min_y = v
    return (TagList(vec_x, min=min_x, max=max_x, count=count_x),
            TagList(vec_y, min=min_y, max=max_y, count=count_y))
