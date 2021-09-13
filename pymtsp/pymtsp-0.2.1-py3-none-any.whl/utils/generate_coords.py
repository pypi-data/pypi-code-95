import math

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
