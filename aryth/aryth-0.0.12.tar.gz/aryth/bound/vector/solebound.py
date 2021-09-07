from intype import is_numeric

from aryth.structs import TagList, Select


def solebound(
        vec: list,
        opt: Select = Select(is_numeric, float)
):
    size = len(vec)
    vec, count, when, to = [None] * size, 0, opt.when, opt.to
    peak = vale = None
    for i, v in enumerate(vec):
        if when(v) and (count := count + 1):
            vec[i] = v = to(v) if to else v
            if not peak and not vale: peak = vale = v
            if v > peak:
                peak = v
            elif v < vale:
                vale = v
    return TagList(vec, min=vale, max=peak, count=count)
