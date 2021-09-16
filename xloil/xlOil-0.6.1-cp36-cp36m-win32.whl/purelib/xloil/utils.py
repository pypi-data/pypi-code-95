import xloil as xlo
import numpy as np
import inspect

def do_array_1(func, arg1):

    if type(arg1) is np.ndarray:
        for idx, x in np.ndenumerate(arg1):
            arg1[*idx] = func(x)
        return arg1
    else:
        return func(arg1)

def do_array_2(func, arg1, arg2):

    is_arr = [type(x) is np.ndarray for x in (arg1, arg2)]
    if is_arr[0] and is_arr[1]:
        if arg1.shape != arg2.shape:
            raise Exception()
        for idx, x in np.ndenumerate(arg1):
            arg1[*idx] = func(x, arg2[*idx])
        return arg1
    elif is_arr[0]:
        for idx, x in np.ndenumerate(arg1):
            arg1[*idx] = func(x, arg2)
    elif is_arr[1]:
        for idx, x in np.ndenumerate(arg2):
            arg2[*idx] = func(arg1, x)
    else:
        return func(arg1, arg2)

def arrayize(fn, argnames):

    def decorate(fn):
        sig = inspect.signature(fn)
        params = sig.parameters

        def result(more1, arg1, more2, arg2, more3):
            def f(a1, a2):
                fn(more1, a1, more2, a2, more3)
            return do_array_2(f, arg1, arg2)
    return decorate if fn is None else decorate(fn)