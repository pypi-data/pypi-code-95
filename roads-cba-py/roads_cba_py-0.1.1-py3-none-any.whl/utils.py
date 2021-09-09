import math


def comp(a, b):
    a = a.__dict__["_data"]
    b = b.__dict__["_data"]
    diffs = [print_diff(k, v1, b[k]) for k, v1 in a.items() if not check(v1, b[k]) and k != "eirr"]
    return len(diffs) == 0


def check(x, y):
    if isinstance(x, str) or isinstance(x, int) or x is None:
        return x == y
    if isinstance(x, float):
        return math.isclose(x, y)
    if isinstance(x, list):
        if len(x) == 10 and len(y) == 20:
            y = y[0:10]
        if len(y) == 10 and len(x) == 20:
            x = x[0:10]
        return all(math.isclose(xx, yy) for xx, yy in zip(x, y))
    raise ValueError(type(x))


def comp_str(x, y):
    eq = "==" if x == y else "!="
    if isinstance(x, str) or isinstance(y, str):
        return f"{x: >20} {eq} {y: >20}"
    abs_ = abs(x - y)
    den = max(x, y)
    rel = (x - y) / den * 100.0 if den != 0 else 0
    return f"{x: > 2.3f} {eq} {y: > 2.3f} ({rel: > 03.2f}%) ({abs_ : > 3.3f}) "


def print_diff(k, v1, v2):
    if isinstance(v1, list):
        if len(v1) == 10 and len(v2) == 20:
            v2 = v2[0:10]
        if len(v2) == 10 and len(v1) == 20:
            v1 = v1[0:10]
        print(f"{k}:")
        [print(f"   {comp_str(x, y)}") for x, y in zip(v1, v2)]
        return None

    print(f"{k : >10} => {comp_str(v1, v2)}")
