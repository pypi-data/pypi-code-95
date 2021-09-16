"""Basic utils."""
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import Union


T = TypeVar("T")


def tuplify(t: Union[Tuple[T, ...], T], n: int = 1) -> Tuple[T, ...]:
    """Make a tuple with `n` copies of `t`, if `t` is not already a tuple."""
    if isinstance(t, (tuple, list)):
        if len(t) != n:
            raise RuntimeError
        return tuple(t)
    else:
        return tuple(t for _ in range(n))


def listify(x: Union[List[T], T], n: int = 1) -> List[T]:
    """Make a list with `n` copies of `x` if `x` is not already a list."""
    if isinstance(x, (tuple, list)):
        return list(x)
    else:
        return [x] * n
