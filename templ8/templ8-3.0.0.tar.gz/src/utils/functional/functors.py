from typing import Callable, Iterator, List, TypeVar

A = TypeVar("A")  # pylint: disable = C0103
B = TypeVar("B")  # pylint: disable = C0103


def flatmap(func: Callable[[A], List[B]], lst: Iterator[A]) -> List[B]:
    """
    >>> flatmap(lambda x: [x + 1, x + 2], [1, 2, 3])
    [2, 3, 3, 4, 4, 5]
    """
    return [y for x in lst for y in func(x)]


def refsort(lst: List[A], key: str) -> Callable[[B], int]:
    """
    >>> sorted([1 + 1j, 2 + 3j, 3 + 2j], key=refsort([3, 2, 1], 'imag'))
    [(2+3j), (3+2j), (1+1j)]
    """
    return lambda x: lst.index(getattr(x, key))
