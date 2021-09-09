import random

import numpy as np


def generate_random_color(format="RGB"):
    """

    :param seed: Seed for random generation
    :param format: Either "RGB" or "HEX"
    :return:
    """

    if format == "RGB":
        return list(np.random.choice(range(256), size=3))
    elif format == "HEX":
        return "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
    else:
        raise ValueError("Format %s is not valid, must be 'RGB' or 'HEX' " % format)
