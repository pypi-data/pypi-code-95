from typing import Callable, List

from veho.matrix.utils import size


def iterate(mx: List[list], fn: Callable):
    h, w = size(mx)
    x = 0
    while x < h:
        y = 0
        row = mx[x]
        while y < w:
            fn(row[y])
            y += 1
        x += 1
    pass


def iterate_dev(mx: List[list], fn: Callable):
    for row in mx:
        for cell in row:
            fn(cell)
    pass
