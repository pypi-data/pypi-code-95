"""This module provides convenience classes that should make writing
your own proposals and using stochastic mixtures much easier. You
don't need to worry about the logistics of truncation, of the problems
that it might cause or indeed of any of the issues caused by passing
in arrays of a different size than nDims.
"""
from abc import ABC

from numpy import pi, array, log, concatenate, diag, sqrt, nextafter
from numpy.linalg import slogdet, multi_dot, inv, pinv
from scipy.special import erf, erfinv
from functools import lru_cache

from .polychord import Model
from pypolychord.priors import UniformPrior


class ParameterCovarianceModel(Model, ABC):
    """
    This is the abstract base class that you would need to sub-class in
    order to produce a ParameterCovarianceModel. This means that you
    provide it with a mean and a covariance and it then produces the
    standard loglikelihood that corresponds to a gaussian. When
    sublassing, you should worry about the correct dimensionality, and
    produce a prior quantile that correponds to the model you want.
    """

    def __str__(self):
        return f'Gaussian posterior with \nmu = {self.mu}\ncov = {self.cov}'

    def __repr__(self):
        return self.__str__().replace('\n', ' ')

    def __init__(self, bounds, mu, cov, file_root='paramCovModel', **kwargs):
        self.a, self.b = bounds
        self.mu = mu
        self.cov = cov
        try:
            self.nDims = mu.size
        except AttributeError:
            self.mu = array(mu)
            self.nDims = mu.size

        try:
            rows, cols = self.cov.shape
        except AttributeError:
            self.cov = array(self.cov)
            rows, cols = self.cov.shape  # raise VE if too few to unpack
        if rows != cols or rows != self.nDims:
            raise ValueError('Dimensions of cov and mean are incompatible: mean – {}, cov ({}, {}) '.format(
                self.nDims, rows, cols))
        try:
            self._invCov = inv(self.cov)
        except:
            print(
                "Singular matrix, reverting to Penrose-Moore inverse, Singular Value Decomposition. ")
            self._invCov = pinv(self.cov)
        super().__init__(self.dimensionality, self.num_derived, file_root, **kwargs)

    def log_likelihood(self, theta):
        """A Ln(likelihood) of the theta given the model. With a uniform
        prior, this defines the posterior distribution up to a
        multiplicative factor. This is a Gaussian Log-likelihood. 

        Parameters
        ----------
        theta : array(self.dimensionality, dtype=numpy.float64)
            Physical parameters' values.

        Returns
        -------
        logL, [derived..] : (log(likelihood): numpy.float64, list(self.num_derived, dtype=numpy.float64))

            The first element is the log-likelihood, the second is a list
            of the derived parameters. 

        """
        delta = theta - self.mu
        ll = - slogdet(2 * pi * self.cov)[1] / 2
        ll -= multi_dot([delta, self._invCov, delta]) / 2
        return ll, []


class PowerPosteriorPrior(ParameterCovarianceModel):
    default_file_root = 'PowerPosteriorModel'
    # Smallest representable +ve float64
    beta_min, beta_max = (nextafter(0, 1), 1)

    def log_likelihood(self, theta):
        """A Ln(likelihood) of the theta given the model. With a uniform
        prior, this defines the posterior distribution up to a
        multiplicative factor. This is a Gaussian-log-likelihood.

        Parameters
        ----------
        theta : array(self.dimensionality, dtype=numpy.float64)
            Physical parameters' values.

        Returns
        -------
        logL, [derived..] : (log(likelihood): numpy.float64, list(self.num_derived, dtype=numpy.float64))

            The first element is the log-likelihood, the second is a list
            of the derived parameters. 

        """
        t = theta[:self.nDims]
        beta = theta[-1]
        log_l, phi = super().log_likelihood(t)
        log_l += log_likelihood_correction(self, beta, t)
        return log_l, phi

    def prior_quantile(self, cube):
        beta = self.beta_min + (self.beta_max - self.beta_min) * cube[-1]
        theta = power_gaussian_quantile(self, cube[:self.nDims], beta)
        return concatenate([theta, [beta]])

    @property
    def dimensionality(self):
        """Dimesnionality of the power posterior model is nDims + 1. 
        """
        return self.nDims + 1


def _erf_term(d, b, g):
    @lru_cache(maxsize=2)
    def helper(t_delta, t_beta, t_sigma):
        hd, hg = array(t_delta), array(t_sigma)
        return erf(hd * sqrt(t_beta / 2) / hg)

    return helper(tuple(d), b, tuple(g))


def power_gaussian_quantile(m, cube, beta=1):
    sigma = diag(m.cov)
    da = _erf_term(m.a - m.mu, beta, sigma)
    db = _erf_term(m.b - m.mu, beta, sigma)
    ret = erfinv((1 - cube) * da + cube * db)
    return m.mu + sqrt(2 / beta) * sigma * ret


def log_box(m):
    if hasattr(m.b, '__iter__') or hasattr(m.a, '__iter__'):
        return log(m.b - m.a).sum()
    else:
        return m.nDims * log(m.b - m.a)


def log_likelihood_correction(model, beta, theta):
    ll = 0

    def ln_z(m, t, b):
        sigma = diag(m.cov)
        ret = - b * (t - m.mu) ** 2 / 2 / sigma ** 2
        ret -= log(pi * sigma ** 2 / 2 / b) / 2
        db = _erf_term(m.b - m.mu, b, sigma)
        da = _erf_term(m.a - m.mu, b, sigma)
        ret -= log(db - da)
        return ret

    ll -= log_box(model)
    ll -= ln_z(model, theta, beta).sum()

    return ll


class GaussianPeakedPrior(ParameterCovarianceModel):
    """This is implemented as a special case of the power posterior
    repartitioning.  One does need to care if it's the right
    function.

    """
    default_file_root = 'GaussianPosteriorModel'

    def log_likelihood(self, theta):
        """A Ln(likelihood) of the theta given the model. With a uniform
        prior, this defines the posterior distribution up to a
        multiplicative factor.

        Parameters
        ----------
        theta : array(self.dimensionality, dtype=numpy.float64)
            Physical parameters' values.

        Returns
        -------
        logL, [derived..] : (log(likelihood): numpy.float64, list(self.num_derived, dtype=numpy.float64))

            The first element is the log-likelihood, the second is a list
            of the derived parameters. 

        """
        log_l, phi = super().log_likelihood(theta)
        log_l += log_likelihood_correction(self, beta=1, theta=theta)
        return log_l, phi

    def prior_quantile(self, cube):
        """Inverse Cumulative distribution function of the prior. Aka the
        quantile. If the prior has PDF \\pi, then this is (CDF (\\pi))^-1.

        Parameters
        ----------

        hypercube: array(self.dimensionality, dtype=numpy.float64) 
            Physical parameters' images in a unit hypercube, where their
            distribution is uniform.

        Returns
        -------
        theta: array(self.dimensionality, dtype=numpy.float64)
            Physical parameters. 
        """
        return power_gaussian_quantile(self, cube)

    @property
    def dimensionality(self):
        """The dimensionality of the truncated gaussians is nDims. 
        """
        return self.nDims


class BoxUniformPrior(ParameterCovarianceModel):
    default_file_root = 'boxUniform'

    def prior_quantile(self, hypercube):
        """Inverse Cumulative distribution function of the prior. Aka the
        quantile. If the prior has PDF \\pi, then this is (CDF (\\pi))^-1.

        Parameters
        ----------

        hypercube: array(self.dimensionality, dtype=numpy.float64) 
            Physical parameters' images in a unit hypercube, where their
            distribution is uniform.

        Returns
        -------
        theta: array(self.dimensionality, dtype=numpy.float64)
            Physical parameters. 
        """
        return UniformPrior(self.a, self.b)(hypercube)


class ResizeablePrior(ParameterCovarianceModel):
    default_file_root = 'ResizeableBoxUniform'
    beta_min = nextafter(0, 1)  # Smallest representable +ve float
    beta_max = 1

    def log_likelihood(self, theta):
        """A Ln(likelihood) of the theta given the model. With a uniform
        prior, this defines the posterior distribution up to a
        multiplicative factor.

        Parameters
        ----------
        theta : array(self.dimensionality, dtype=numpy.float64)
            Physical parameters' values.

        Returns
        -------
        logL, [derived..] : (log(likelihood): numpy.float64, list(self.num_derived, dtype=numpy.float64))

            The first element is the log-likelihood, the second is a list
            of the derived parameters. 

        """
        t = theta[:self.nDims]
        beta = theta[-1]
        if beta <= self.beta_min:
            beta = self.beta_min
        log_l, phi = super().log_likelihood(t / beta)
        log_l += 2 * self.nDims * (log(beta))
        log_l -= log_box(self)
        return log_l, phi

    def prior_quantile(self, hypercube):
        """Inverse Cumulative distribution function of the prior. Aka the
        quantile. If the prior has PDF \\pi, then this is (CDF (\\pi))^-1.

        Parameters
        ----------

        hypercube: array(self.dimensionality, dtype=numpy.float64)
            Physical parameters' images in a unit hypercube, where their
            distribution is uniform.

        Returns
        -------
        theta: array(self.dimensionality, dtype=numpy.float64)
            Physical parameters.
        """
        beta = hypercube[-1:].item()
        # PolyChord refers to Quantile functions as priors.
        # This is not incorrect, but can be confusing.
        uniform = UniformPrior(self.a * beta, self.b * beta)(hypercube[:-1])
        return concatenate([uniform, [beta]])

    @property
    def dimensionality(self):
        """The dimensionality of the resizeable bounds uniform prior is nDims
        + 1.

        """
        return self.nDims + 1
