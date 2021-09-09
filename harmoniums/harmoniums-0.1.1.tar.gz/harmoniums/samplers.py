from math import gamma

import numpy as np
from numpy import exp, expm1, log1p, log, random, sqrt, zeros
from scipy.special import loggamma

from numba import jit, float64, uint32
import numba_scipy


# from numba import vectorize
from harmoniums.wrappers import vectorize


@jit(float64(float64, float64, uint32), nopython=True)
def sample_g(a: float, b: float, N: int) -> float:
    """
    Sample from `g`, the approximation of the right truncated gamma distribution.

    Reference:
        [1]: A. Philippe, Stat. Comp. 7, 173 ('97).
    """
    # Step 1.
    u = random.uniform(0.0, 1.0)

    # Step 2.
    w_bar = zeros(N + 1)
    w_tilde = zeros(N + 1)
    w_bar[1] = w_tilde[1] = 1

    for k in range(1, N):
        # Calculate new values for w_tilde[k+1] and w_bar[k+1]: Eq. (5), Ref. [1].
        w_bar[k + 1] = w_bar[k] * b / (a + k)
        # assert w_bar[k + 1] == b ** k / gamma(a + k + 1)
        w_tilde[k + 1] = w_tilde[k] + w_bar[k + 1]

    # w_k -> w_k / w_N.
    w_tilde = w_tilde / w_tilde[N]
    # Take k where w_{k-1} <= u <= w_k.

    for k, w_k in enumerate(w_tilde):
        if u <= w_k:
            break

    # Step 3.
    return random.beta(a, k)


@jit(uint32(float64), nopython=True)
def _choose_number_of_components_right_truncated_gamma(b: float) -> int:
    """
    Choose number of components for right truncated
    """
    # Choose value corresponding to 0.95 quantile of normal distribution.
    t_p = 1.6448536269514727
    # Determine number of components.
    n_p = 0.25 * (t_p + sqrt(t_p ** 2 + 4 * abs(b))) ** 2
    N = int(np.floor(n_p))
    return N


@jit(float64(float64, float64), nopython=True)
def sample_right_truncated_gamma_distribution_positive_b(a: float, b: float) -> float:
    """
    Sample from right truncated (at t=1) gamma distribution: f-(x|a>0, b>0, t=1).

    Perform rejection sampling using approximate distribution `g_N` that consists of
    beta distributions.

    Reference:
        [1]: A. Philippe, Stat. Comp. 7, 173 ('97).
    """
    assert b > 0

    N = _choose_number_of_components_right_truncated_gamma(b)

    # Calculate M once.
    M_inverse = 0.0
    for k in range(1, N + 1):
        # M_inverse += b ** (k - 1) / gamma(k)
        # Numerically more stable for large k, but somewhat slower.
        M_inverse += exp((k - 1) * log(b) - loggamma(float(k)))

    M = 1 / M_inverse

    while True:
        # Step 1.
        u = random.uniform(0.0, 1.0)
        x = sample_g(a, b, N)

        # Step 2.
        z = 0.0
        for k in range(1, N + 1):
            # z += (b * (1 - x)) ** (k - 1) / gamma(k)
            # The following is a numerically more stabler implementation.
            logdz = (k - 1) * log(b * (1 - x)) - loggamma(float(k))
            z += exp(logdz)

        rho = 1 / (exp(b * x) * z)

        # Step 3.
        if u * M <= rho:
            return x


@vectorize
def sample_interval_truncated_gamma_distribution(
    a: float, b: float, t_left: float = 0.0
) -> float:
    """
    Sample gamma distribution truncated to the [`t_left`, 1] interval, `a`>1.
    """
    return _sample_interval_truncated_gamma_distribution(a, b, t_left)


@jit(float64(float64, float64))
def sample_truncated_exponential(lambda_: float = 1.0, t: float = 1.0) -> float:
    """
    Sample from the exponential distribution, normalised to the interval [0, t].

    The distribution normalised to the unit range:
    p(x) = b exp(-bx)/([1-exp[-bt]]),
    so that the cumulative distribution is
    P(x) = (1 - exp[-bx])/(1 - exp[-bt]).
    We can generate samples by inverting the cumulative distribution
    x = -1/b * ln[1 + P(x)(exp[-bt] - 1)].
    """
    p = random.uniform(0.0, 1.0)
    if lambda_ != 0.0:
        return -log1p(p * (expm1(-t * lambda_))) / lambda_
    # When lambda=0, the distribution is uniform.
    return p * t


@jit(float64(float64, float64, float64))
def _sample_interval_truncated_gamma_distribution(
    a: float, b: float, t_left: float = 0.0
) -> float:
    """
    Sample gamma distribution truncated to the [`t_left`, 1] interval, `a`>1.
    """
    # assert a >= 1

    # 1 - a + b is purely negative.
    lambda_ = a - 1 - b

    while True:
        # exp(-lambda x) = exp(|lambda|x) ~ exp(-|lambda|y), with y=1-x.
        y = sample_truncated_exponential(lambda_=lambda_, t=1 - t_left)

        x = 1 - y
        ln_p_accept = (a - 1.0) * (log(x) - x + 1.0)
        u = random.uniform(0.0, 1.0)
        if u < exp(ln_p_accept):
            return x


@vectorize
def sample_right_truncated_gamma_distribution(
    a: float, b: float, truncation_point: float = 1.0
) -> float:
    """
    Sample from right truncated (at `t`) gamma distribution: f-(x|a, b, t).
    """
    if b > 0:
        return (
            sample_right_truncated_gamma_distribution_positive_b(
                a, b * truncation_point
            )
            * truncation_point
        )
    return (
        _sample_interval_truncated_gamma_distribution(
            a, b * truncation_point, t_left=0.0
        )
        * truncation_point
    )
