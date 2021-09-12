import numpy as np
from scipy.optimize import minimize
from scipy.stats import gamma


class Distributions:
    """
    Utilities for handling distributions.
    """

    @staticmethod
    def gammaparams(q1, q2, p1=0.1, p2=0.9):
        """A function for parametrizing gamma distributions by specifying two
        quantiles.

        Relevant math can be found in "Determining distribution parameters from
        quantiles" by John D. Cook, 2010.

        :param q1: p1-quantile
        :param q2: p2-quantile
        :param p1: lower percentage (0 < p1 < 1)
        :param p2: higher percentage (0 < p2 < 1)
        """
        # Require the arguments to be positive and q1 < q2, p1 < p2 <1
        if q1 <= 0 or q2 <= q1:
            return (None, None)
        if p1 <= 0 or p2 <= p1 or p2 >= 1:
            return (None, None)

        def f(a):
            return np.abs(
                gamma.ppf(p2, a, scale=1) / gamma.ppf(p1, a, scale=1) - q2 / q1
            )

        shape = minimize(f, 1, bounds=[[0.1, None]], method="L-BFGS-B").x
        rate = gamma.ppf(p1, shape, scale=1) / q1

        return (shape[0], rate[0])
