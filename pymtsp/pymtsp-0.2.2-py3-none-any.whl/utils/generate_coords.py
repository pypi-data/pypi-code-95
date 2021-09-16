import math
from functools import reduce
from itertools import product
from math import ceil

import numpy as np


def get_circular_coords(n: int,
                        r: float = 1.0):  # radius of the circle

    divisor = math.floor(360 / n)
    theta = np.arange(1, 360, divisor)  # degree
    theta_rad = theta * (np.pi / 180)
    x = r * np.cos(theta_rad)
    y = r * np.sin(theta_rad)
    coords = np.stack([x, y], axis=-1)
    return coords


def get_uniform_coords(n: int):
    coords = np.random.uniform(0.0, 1.0, size=(n, 2))
    return coords


def _factors(n):
    factor_set = set(reduce(list.__add__, ([i, n // i] for i in range(1, int(n ** 0.5) + 1) if n % i == 0)))
    return (sorted(list(factor_set)))


def get_regular_coords(n: int):
    # check n is 2 powers of the other integer
    factors = _factors(n)
    _n = factors[ceil(len(factors) / 2) - 1]
    assert _n ** 2 == n, "Given n is not the 2 powers of some integer"

    # assuming the mapsize is bounded as [0.0,1.0]^2
    coord = np.linspace(0.0, 1.0, _n)
    coords = np.array(list(product(coord, coord)))
    return coords


if __name__ == '__main__':
    regular_coords(25)
    regular_coords(36)
    regular_coords(49)
