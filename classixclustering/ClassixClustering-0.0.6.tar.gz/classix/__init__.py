from . import aggregation_cm
from . import amalgamation_cm

try:
    from .aggregation_cm import aggregate
    from .amalgamation_cm import amalgamate
except ModuleNotFoundError:
    from .aggregation import aggregate
    from .amalgamation import amalgamate
    print("Cython fail.")
from .clustering import classix