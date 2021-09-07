import logging
import numpy as np
from hyperopt import tpe


def np_safe_exp(x):
    # Bug fix: we limit the input of the exponential between -700 and +700
    # to avoid under and over flow respectively
    MIN = -700.0
    MAX = +700.0
    return np.exp(np.minimum(np.maximum(MIN, x), MAX)).astype(x.dtype)


def logsum_rows(x):
    m = x.max(axis=1)
    return np.log(np_safe_exp(x - m[:, None]).sum(axis=1)) + m


logging.info("Monkey-patching 'hyperopt' for np.exp under/over-flow")
tpe.logsum_rows = logsum_rows
