from typing import Callable, List

from veho.matrix.utils import size


def mutate(mx: List[list], fn: Callable):
    h, w = size(mx)
    x = 0
    while x < h:
        y = 0
        row = mx[x]
        while y < w:
            row[y] = fn(row[y])
            y += 1
        x += 1
    return mx
