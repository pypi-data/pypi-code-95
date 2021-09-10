import numpy as np


def exp_for_fit(x, a, b, c):
    return a * np.exp(b * x) + c


def exp(a, b, c):
    def _inner(x):
        return a * np.exp(b * x) + c

    return _inner


def log_for_fit(x, a, b, c, d):
    return a * np.log(b * x + c) + d


def log(a, b, c, d):
    def _inner(x):
        return a * np.log(b * x + c) + d

    return _inner
