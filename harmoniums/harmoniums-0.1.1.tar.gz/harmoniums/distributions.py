from math import factorial, gamma
from typing import Union

import numpy as np
from numpy import cos, exp, infty, log, mean, pi, sin, sqrt, std
from scipy.optimize import fsolve
from scipy.special import dawsn, loggamma, gammainc, poch
from scipy.stats import beta

from harmoniums.wrappers import vectorize


def g(x: Union[float, np.array], a: float, b: float, n: int) -> float:
    """
    Density approximation of the right truncated (at t=1) gamma distribution.

    Approximation of the right truncated gamma distribution f-(x|a,b, t=1) as a series
    of beta functions, cut off at `n` terms.
    """
    g_truncated = 0.0
    # Sum series of beta function up to `n` terms.
    for k in range(1, n + 1):
        g_truncated += b ** (k - 1) / gamma(a + k) * beta.pdf(x, a, k)
    return b ** a * exp(-b) / gammainc(a, b) * g_truncated


def _incomplete_gamma_series_expansion(
    a: float, z: float, tolerance: float = 1.0e-10
) -> float:
    """
    gamma*(a, z) = 1/Gamma(a) sum_k=0^inf (-z)^k/(k!(a+k)) {Eq. (6) Ref. [1]}.

    Ref:
        [1]: Gil et al., Algorithm 969: Computation of the incomplete gamma function for
        negative values of the argument. ACM Trans. Math. Softw., 43(3), November 2016.

    """
    # Zeroth element.
    series_sum = 1 / a
    reciprocal_gamma = 1.0 / gamma(a)

    k = 1
    while True:
        term = (-z) ** k / (factorial(k) * (a + k))
        series_sum += term
        if term * reciprocal_gamma < tolerance:
            break
        k += 1

    return series_sum * reciprocal_gamma


def _incomplete_gamma_Poincare_expansion(
    a: float, z: float, tolerance: float = 1.0e-10
) -> float:
    """
    gamma*(a, z) = e^z/[z Gamma(a)] sum_n=0^inf (1-a)_n/z^n {Eq. (29) Ref. [1]}.

    Ref:
        [1]: Gil et al., Algorithm 969: Computation of the incomplete gamma function for
        negative values of the argument. ACM Trans. Math. Softw., 43(3), November 2016.
    """
    f = exp(-z) / (-z * gamma(a))
    # Zeroth element.
    series_sum = 0

    n = 0
    while True:
        term = poch(1 - a, n) / (-z) ** n
        series_sum += term
        if abs(term) * f < tolerance:
            break
        n += 1

    gamma_star = series_sum * f
    return gamma_star


def _incomplete_gamma_uniform_asymptotic_expansion(a: float, z: float) -> float:
    """
    {Eq. (9), Ref. [1]}.
    """
    lambda_ = z / a
    half_eta_squared = lambda_ - 1 - log(lambda_)
    eta = sqrt(2 * (lambda_ - 1 - log(lambda_)))
    bracket_term = sqrt(-2 / a) * dawsn(eta * sqrt(-a / 2))
    return z ** (-a) * (
        cos(-pi * a)
        - sqrt(-2 * a / pi) * exp(-a * half_eta_squared) * sin(-pi * a) * bracket_term
    )


def gamma_star_negative_z(a: float, z: float) -> float:
    """
    Integral gamma*(a, z) = 1/Gamma(a) * int_0^1 dt t(a-1) e(-zt) for z < 0.

    Refs:
        [1]: Gil et al., Algorithm 969: Computation of the incomplete gamma function for
        negative values of the argument. ACM Trans. Math. Softw., 43(3), November 2016.
    """
    if a > 0:
        if z < -50:
            return _incomplete_gamma_Poincare_expansion(a, z)
        return _incomplete_gamma_series_expansion(a, z)
    else:
        if a.is_integer():
            return z ** (-a)
        raise NotImplementedError()


@vectorize
def gamma_star(a: float, z: float) -> float:
    """
    1/Gamma[a] * Integral_0^1 dt t^(a-1) exp[-zt].

    See Eq. (8.2.7) in Ref. [1].

    Ref:
        [1]: Paris, Incomplete gamma and related functions. NIST digital library
            of mathematical functions, pp. 173–192 (2010).
    """
    if z > 0:
        # N.B. the 1/Gamma[a] convention in NumPy compared to NIST handbook.
        return z ** (-a) * gammainc(a, z)
    elif z < 0:
        return gamma_star_negative_z(a, z)
    return 1 / (gamma(a) * a)


@vectorize
def log_normalisation_gamma_distribution(a: float, b: float, t: float = 1.0) -> float:
    """
    Return logarithm of integral_0^t dx x^(a-1) exp[-bx].
    """
    if t == 0:  # Integral of zero measure.
        return -infty
    # N.B.: Multiply by gamma(a) to get the indefinite integral (= addition in
    # log space), see
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.gammainc.html.
    if b > 0:
        return loggamma(a) - a * log(b) + log(gammainc(a, t * b))
    return loggamma(a) + a * log(t) + log(gamma_star_negative_z(a, b * t))


@vectorize
def normalisation_gamma_distribution(a: float, b: float, t: float = 1.0) -> float:
    """
    Return value of integral_0^t dx x^(a-1) exp[-bx].
    """
    return exp(log_normalisation_gamma_distribution(a, b, t))


@vectorize
def normalisation_gamma_interval_distribution(
    a: float, b: float, t_left: float = 0.0, t_right: float = 1.0
) -> float:
    """
    Return value of integral_{t_left}^{t_right} dx x^(a-1) exp[-bx].
    """
    phi_right = normalisation_gamma_distribution(a, b, t_right)
    phi_left = normalisation_gamma_distribution(a, b, t_left)
    return phi_right - phi_left


@vectorize
def truncated_gamma_distribution(x: float, a: float, b: float, t: float = 1.0) -> float:
    """
    Gamma distribution right truncated to the interval [0, t].
    """
    if b > 0:
        return b ** a * exp(-b * x) * x ** (a - 1) / (gammainc(a, b * t) * gamma(a))

    # Integral_0^t dx x^(a-1) exp[-zx] = t^a gamma*(a, tz) * Gamma(a)
    return (
        exp(-b * x)
        * x ** (a - 1)
        * t ** (-a)
        / (gamma(a) * gamma_star_negative_z(a, b * t))
    )


@vectorize
def interval_truncated_gamma_distribution(
    x: float, a: float, b: float, t_left: float, t_right: float = 1.0
) -> float:
    """
    Gamma distribution truncated to the interval [`t_left`,`t_right`].
    """
    # Return 0 outside interval.
    is_outside_interval = (x < t_left) | (x > t_right)
    interval_mask = np.where(is_outside_interval, 0.0, 1.0)

    Z = normalisation_gamma_interval_distribution(a, b, t_left, t_right)
    return interval_mask * exp(-b * x) * x ** (a - 1) / Z


@vectorize
def truncated_gamma_cumulative_distribution(
    x: float, a: float, b: float, t: float = 1.0,
):
    """
    Cumulative distribution of the right truncated Gamma distribution.
    """
    if b > 0:
        return gammainc(a, b * x) / (gammainc(a, b * t))
    return (
        (x / t) ** a * gamma_star_negative_z(a, b * x) / gamma_star_negative_z(a, b * t)
    )


def interval_truncated_gamma_cumulative_distribution(
    x, a, b, left_truncation, right_truncation=1.0
):
    """
    Cumulative function of ther interval truncated gamma distribution.
    """
    # Return 0.0 left of the interval, and 1.0 on the right.
    is_outside_interval = (x < left_truncation) | (x > right_truncation)
    interval_mask = np.where(is_outside_interval, 0.0, 1.0)
    right_end_ones = np.where(x > right_truncation, 1.0, 0.0)

    phi_x = normalisation_gamma_distribution(a, b, x)
    phi_right = normalisation_gamma_distribution(a, b, right_truncation)
    phi_left = normalisation_gamma_distribution(a, b, left_truncation)
    Z = phi_right - phi_left
    return interval_mask * (phi_x - phi_left) / Z + right_end_ones


def truncated_exponential(x: float, lambda_: float, t: float = 1.0) -> float:
    """
    Exponential distribution normalised on the [0, t] range.
    """
    return truncated_gamma_distribution(x, a=1.0, b=lambda_, t=t)


def fit_truncated_gamma_parameters(X: np.ndarray) -> tuple:
    """
    Try to solve for `a` and `b` from the truncated gamma distribution.
    """

    def constraint(X: np.ndarray, mu: np.ndarray, sigma: np.ndarray) -> np.ndarray:
        """
        Pose optimisation problem as mean and variance constraint.

        Solve for `a` and `b` (concatenated into `X`), so that the mean
        and variance according to the truncated gamma distribution coincides
        with `mu` and `sigma` passed to the function.
        """
        X = X.reshape(2, -1)
        a, b = X[0], X[1]
        # Mean of truncated Gamma distribution with parameters `a` and `b`.
        p_mean = normalisation_gamma_distribution(
            a + 1, b
        ) / normalisation_gamma_distribution(a, b)
        # Variance (= <x^2> - <x>^2) of truncated Gamma distribution with
        # parameters `a` and `b`.
        p_var = (
            normalisation_gamma_distribution(a + 2, b)
            / normalisation_gamma_distribution(a, b)
            - p_mean ** 2
        )
        mean_constraint = p_mean - mu
        var_constraint = p_var - sigma ** 2

        # Concatenate because `fsolve` requires flat arrays.
        return np.array([mean_constraint, var_constraint]).ravel()

    emperical_mean = mean(X, axis=0)
    emperical_std = std(X, axis=0)
    # Initial guess of parameters.
    x0 = np.ones(shape=(len(emperical_mean) + len(emperical_std)))
    X_solution = fsolve(constraint, x0, args=(emperical_mean, emperical_std))
    # Unpack solution.
    X_solution = X_solution.reshape(2, -1)
    alpha, beta = X_solution[0], X_solution[1]

    return alpha, beta
