def factorial(n):
    """
    function to calculate factorial
    .. versionadded:: 0.0.4
    """
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
    