from .descriptor import Descriptor
from .typed import Typed
from .broadtypes import *
from .types import Integer, Float, String, List, Dict


def checkattrs(**kwargs):
    def decorator(cls):
        for k, v in kwargs.items():
            if isinstance(v, Descriptor):
                v.name = k
                setattr(cls, k, v)
            else:
                setattr(cls, k, v(k))
        return cls

    return decorator
