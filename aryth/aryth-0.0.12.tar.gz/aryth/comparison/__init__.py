def max_indicate(pr, cu, indicator):
    return va if (va := indicator(cu)) > pr else pr


def max_compare(pr, cu):
    return cu if cu > pr else pr


def min_indicate(pr, cu, indicator):
    return va if (va := indicator(cu)) < pr else pr


def min_compare(pr, cu):
    return cu if cu < pr else pr
