from collections import defaultdict
from collections.abc import Mapping

__all__ = [
    'dict_dist',
    'dict_dif',
    'dict_diff',
    'keydefaultdict',
    'ignorenonedict',
    'function_cache',
]


def dict_dist(a: dict, b: dict, f=lambda x, y: x - y, default_dist=0) -> defaultdict:
    """
        Compute the difference between the pair-wise difference between two dictionaries
        
        a : dict (or defaultdict)
        b : dict (or defaultdict)
        
        Return a defaultdict (with default to 0) with results of (a - b)

        Aliases: dict_diff, dict_dif
        
    """
    c = defaultdict(lambda: default_dist)
    for key in set(a.keys()) | set(b.keys()):
        c[key] = f(a[key], b[key])
    return c


# Aliases
dict_dif = dict_diff = dict_dist


class keydefaultdict(defaultdict):
    """
        Extension of defaultdict that support
        passing the key to the default_factory
    """
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key, "Must pass a default factory with a single argument.")
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class ignorenonedict(dict):
    def __init__(self, other=None, **kwargs):
        super().__init__()
        self.update(other, **kwargs)

    def __setitem__(self, key, value):
        if value is not None:
            super().__setitem__(key, value)

    def update(self, other=None, **kwargs):
        if other is not None:
            for k, v in other.items() if isinstance(other, Mapping) else other:
                self.__setitem__(k, v)
        for k, v in kwargs.items():
            self.__setitem__(k, v)


class FunctionCache(dict):
    def __init__(self, f):
        self.f = f

    def get(self, *args, **kwargs):
        if len(kwargs) > 0:
            raise NotImplementedError('No kwargs allowed when using FunctionCache.')
        key = hash(str(args))
        if key in self:
            return self[key]
        else:
            ret = self[key] = self.f(*args)
            return ret


# Decorator
def function_cache(f, name='cache'):
    """"
    
    Usage Example:

    @function_cache(lambda X: expensive_function(X))
    @function_cache(lambda X: expensive_function2(X), name = 'second_cache')
    def f(X, y):
        return expensive_function(Y) - f.cache.get(X) + f.second_cache.get(X)


    X, Y = ..., ...
    for y in Y:
        f(X, y) # The function is called multiple times with X



    """
    def decorate(func):
        setattr(func, name, FunctionCache(f))
        return func

    return decorate
