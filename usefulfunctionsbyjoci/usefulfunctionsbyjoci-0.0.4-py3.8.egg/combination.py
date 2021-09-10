def combination(n, r):
    """
    calculate 2 number combination
    .. versionadded:: 0.0.4
    """
    numerator = factorial(n)
    denominator = factorial(r) * factorial(n-r)
    return int(numerator/denominator)