from typing import Callable, TypeVar

A = TypeVar("A")  # pylint: disable = C0103
B = TypeVar("B")  # pylint: disable = C0103
C = TypeVar("C")  # pylint: disable = C0103


def compose(first: Callable[[B], C], second: Callable[[A], B]) -> Callable[[A], C]:
    """
    >>> compose(lambda x: x + 1, lambda x: 2 * x)(1)
    3

    >>> compose(lambda x: 2 * x, lambda x: x + 1)(1)
    4
    """
    return lambda x: first(second(x))


def apply(param: A, func: Callable[[A], B]) -> B:
    """
    >>> apply(1, lambda x: x + 1)
    2
    """
    return func(param)
