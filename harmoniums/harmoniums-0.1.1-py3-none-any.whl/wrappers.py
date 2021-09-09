"""
Decorators of functions and classes.
"""
from functools import wraps
import logging

import numpy as np


def warn_unused_parameters(input_function):
    """
    Warn if any argument of `input_function`, except the first, is not None.
    """

    @wraps(input_function)
    def wrapper(*args, **kwargs):
        # All but `self` and the first argument.
        args_none = (a is None for a in args[2:])
        kwargs_none = (v is None for v in kwargs.values())
        if not (all(args_none) and all(kwargs_none)):
            logging.error("Only the first argument must be not None.")
        return input_function(*args, **kwargs)

    return wrapper


def vectorize(func):
    """
    Use NumPy vectorize, but also restore `__name__` attribute.
    """
    return wraps(func)(np.vectorize(func, otypes=[float]))
