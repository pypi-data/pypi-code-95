def margin_shallow(mx, tp, bt, lf, rt):
    return [row[:lf] + row[-rt:] for row in mx[:tp]] + \
           [row[:lf] + row[-rt:] for row in mx[-bt:]]


def margin_mapper(mx, fn, tp, bt, lf, rt):
    return [[fn(x) for x in row[:lf]] + [fn(x) for x in row[-rt:]] for row in mx[:tp]] + \
           [[fn(x) for x in row[:lf]] + [fn(x) for x in row[-rt:]] for row in mx[-bt:]]


def margin_mutate(mx, fn, tp, bt, lf, rt, ht=None, wd=None):
    s = (ht := ht if ht else len(mx)) - bt
    while (ht := ht - 1) >= s: margin_mutate_row(mx[ht], fn, lf, rt, wd)
    while (tp := tp - 1) >= 0: margin_mutate_row(mx[tp], fn, lf, rt, wd)
    return mx


def margin_mutate_row(row, fn, lf, rt, wd=None):
    s = (wd := wd if wd else len(row)) - rt
    while (wd := wd - 1) >= s: row[wd] = fn(row[wd])
    while (lf := lf - 1) >= 0: row[lf] = fn(row[lf])
    return row
