def permutations(n, r):
    """
    calculate 2 number permutation
    .. versionadded:: 0.0.4
    """
    numerator = factorial(n)
    denominator = factorial(n-r)
    return int(numerator/denominator)