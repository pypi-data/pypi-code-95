# pylint: disable=invalid-name
"""
Definition of generic profiles.

Tasks
-----

TODO-1(@amerlo): Add operator overloading (add, sub, mul, truediv, ...).
TODO-2(@amerlo): Add support for derivative and integral operation.
"""

import abc
import copy
import dataclasses
import typing

import numpy as np
from scipy import interpolate
from scipy.optimize import curve_fit
from scipy.spatial.distance import cdist
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (
    NormalizedKernelMixin,
    Kernel,
    Hyperparameter,
)

import rna
import rna.polymorphism
import tfields


@dataclasses.dataclass
class Profile(abc.ABC, rna.polymorphism.Storable):
    """
    A generic profile representation.

    Examples:
        >>> from numpy import allclose
        >>> from w7x.lib.profiles import PowerSeries

        >>> p = PowerSeries([1, -1], domain=[0, 1])
        >>> p.domain
        [0, 1]

        >>> allclose(p(0.0), 1.0)
        True

        Fit a profile from points
        >>> p = PowerSeries.fit(x=[0, 1], y=[1, 0], deg=1)
        >>> allclose(p(0.0), 1.0)
        True

        Fit a profile from tensor field
        >>> field = tfields.TensorFields([0, 1], [1, 0])
        >>> p = PowerSeries.fit(field, deg=1)
        >>> allclose(p(0.5), 0.5)
        True

        Provide common APIs from numpy
        >>> p.linspace(n=5)[1]
        array([1.  , 0.75, 0.5 , 0.25, 0.  ])
    """

    coefficients: typing.List[float] = dataclasses.field(default_factory=lambda: None)
    domain: typing.List[float] = dataclasses.field(default_factory=lambda: [0, 1])
    coord_sys: str = None

    def __call__(self, x: typing.Union[float, np.ndarray, list]):
        """
        Evaluate profile at location x.
        """
        x = np.asarray(x)
        return self._call(x)

    def __mul__(self, other):
        """
        Multiply by a Profile, array or scalar.

        TODO-2(@amerlo): make operation with another Profile possible, test me.
        """
        if not self._check_op_other(other):
            raise NotImplementedError

        if isinstance(other, Profile):
            raise NotImplementedError

        return self._mul(other)

    def __truediv__(self, other):
        """
        Divide by a Profile, array or scalar.
        """
        return self._truediv(other)

    @classmethod
    def fit(
        cls,
        x: typing.Union[list, np.ndarray, tfields.TensorFields],
        y: typing.Union[list, np.ndarray] = None,
        **kwargs
    ):
        """
        Fit profile to data.

        TODO-2(@amerlo): support fit from nD TensorFields

        Args:
            x (array_like or TensorFields):
                x-coordinates of the sample points.
                If TensorFields, the TensorFields.fields attribute will be
                used as y-coordinates.
            y (array_like): y-coordinates of the sample points.
        """
        if isinstance(x, tfields.TensorFields):
            y = np.asarray(x.fields).reshape(x.shape)
        return cls._fit(x, y, **kwargs)

    def linspace(self, n: int = 100, domain=None):
        """
        Return x, y values at equally spaced points in domain.

        Similar to numpy Polynomial.linspace method.

        Args:
            n (int): Number of point pairs to return.
            domain (array_like): If not None, the specified domain is used instead of
            that of the calling instance.
        """

        if domain is None:
            domain = self.domain

        x = np.linspace(domain[0], domain[-1], n)
        y = self(x)

        return x, y

    def plot(self, **kwargs):
        """
        TODO-2(@amerlo): add plotting routine.

        Args:
            **kwargs: forwarding to rna.plotting.plot_function
        """
        return rna.plotting.plot_function(self, **kwargs)  # pylint: disable=no-member

    @abc.abstractmethod
    def _call(self, x):
        raise NotImplementedError

    @staticmethod
    def _check_op_other(other):
        """
        Check other type from which we support operations.

        TODO-2(@amerlo): could we include TensorFields?
        """
        return isinstance(
            other, (Profile, list, np.ndarray, float, complex, np.number, int)
        )

    @classmethod
    @abc.abstractmethod
    def _fit(cls, x, y, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _mul(self, other):
        raise NotImplementedError

    @abc.abstractmethod
    def _truediv(self, other):
        raise NotImplementedError


@dataclasses.dataclass
class PowerSeries(Profile):
    """
    A power series profile.

    Examples:
        >>> from numpy import allclose
        >>> import w7x
        >>> poly = w7x.lib.profiles.PowerSeries([1, 0, -1], domain=[0, 1])
        >>> poly(0.0)
        1.0

        >>> allclose(poly(0.6), 0.64)
        True

        >>> poly.coefficients = [2, 0, -1]
        >>> allclose(poly(0.6), 1.64)
        True

        Fit from values
        >>> poly = w7x.lib.profiles.PowerSeries.fit(
        ...     x=[0, 0.2, 0.6, 1.0],
        ...     y=[1, 0.96, 0.64, 0.0],
        ...     deg=2)
        >>> allclose(poly(0.6), 0.64)
        True

        >>> allclose(poly.coefficients, [1, 0, -1])
        True

        >>> poly = poly * 2
        >>> allclose(poly(0.6), 1.28)
        True

        >>> allclose(poly.coefficients, [2, 0, -2])
        True
    """

    def _call(self, x):
        coef = np.asarray(self.coefficients)[::-1]
        y = np.zeros_like(x)
        for c in coef:
            y = y * x + c
        return y

    @classmethod
    def _fit(cls, x, y, **kwargs):
        poly = np.polynomial.polynomial.Polynomial.fit(x=x, y=y, domain=[], **kwargs)
        return cls(coefficients=poly.coef, domain=[x[0], x[-1]])

    def _mul(self, other):
        return PowerSeries(
            domain=self.domain,
            coefficients=[c * other for c in self.coefficients],
            coord_sys=self.coord_sys,
        )

    def _truediv(self, other):
        raise NotImplementedError


def two_power_fn(x, c0, c1, c2):
    """
    TwoPower analytical function.
    """
    return c0 * (1 - x ** c1) ** c2


@dataclasses.dataclass
class TwoPower(Profile):
    """
    A two power profile.

    Examples:
        >>> import w7x
        >>> two_power = w7x.lib.profiles.TwoPower([1, 1, 2], domain=[0, 1])
        >>> two_power(0)
        1

        >>> two_power([1, 0.5, 0])
        array([0.  , 0.25, 1.  ])

        >>> two_power = two_power * 2
        >>> two_power([1, 0.5, 0])
        array([0. , 0.5, 2. ])
    """

    def _call(self, x):
        return two_power_fn(x, *self.coefficients)

    @classmethod
    def _fit(cls, x, y, **kwargs):
        coef, _ = curve_fit(two_power_fn, x, y)
        return cls(coefficients=coef, domain=[x[0], x[-1]])

    def _mul(self, other):
        coef = [self.coefficients[0] * other] + self.coefficients[1:]
        return TwoPower(coefficients=coef, domain=self.domain, coord_sys=self.coord_sys)

    def _truediv(self, other):
        raise NotImplementedError


@dataclasses.dataclass
class CubicSpline(Profile):
    """
    A cubic spline.

    TODO-2(@amerlo): return scalar if scalar is given.

    Examples:
        >>> import w7x
        >>> domain = [0, 0.2, 0.6, 1]
        >>> values = [1, 0.96, 0.64, 0]
        >>> cubic_spline = w7x.lib.profiles.CubicSpline(
        ...     values, domain)
        >>> cubic_spline(0)
        array(1.)

        Achtung: data are stored as coefficients
        >>> cubic_spline.coefficients = [2, 0.96, 0.64, 0]
        >>> cubic_spline(0)
        array(2.)

        >>> cubic_spline = w7x.lib.profiles.CubicSpline.fit(
        ...     x=domain, y=values)
        >>> cubic_spline([0.0, 0.5])
        array([1.  , 0.75])
    """

    def _call(self, x):
        """
        TODO-2(@amerlo): natively support cubic spline function.
        """
        poly = interpolate.CubicSpline(
            x=self.domain, y=self.coefficients, extrapolate=True
        )
        return poly(x)

    @classmethod
    def _fit(cls, x, y, **kwargs):
        return cls(coefficients=y, domain=x)

    def _mul(self, other):
        values = [v * other for v in self.coefficients]
        return CubicSpline(
            coefficients=values, domain=self.domain, coord_sys=self.coord_sys
        )

    def _truediv(self, other):
        raise NotImplementedError


# pylint: disable=too-many-arguments
def sum_atan_fn(x, c0, c1, c2, c3, c4):
    """
    Evaluate a sum of arctangent profile at location x.

    From: http://webservices.ipp-hgw.mpg.de/docs/vmec/vmec2000_input.pdf
    """
    return c0 + 2 / np.pi * c1 * np.arctan(c2 * x ** c3 / (1 - x) ** c4)


@dataclasses.dataclass
class SumAtan(Profile):
    """
    A sum of arctangent profile.

    Examples:
        >>> import w7x
        >>> sum_atan = w7x.lib.profiles.SumAtan([0, 1, 1, 1, 1], domain=[0, 1])
        >>> sum_atan(0)
        0.0

        >>> sum_atan([1, 0.5, 0])
        array([1. , 0.5, 0. ])

        >>> sum_atan = sum_atan * 2
        >>> sum_atan.coefficients
        [0, 2, 1, 1, 1]

        >>> sum_atan([1, 0.5, 0])
        array([2., 1., 0.])
    """

    def _call(self, x):
        return sum_atan_fn(x, *self.coefficients)

    @classmethod
    def _fit(cls, x, y, **kwargs):
        coef, _ = curve_fit(sum_atan_fn, x, y)
        return cls(coefficients=coef, domain=[x[0], x[-1]])

    def _mul(self, other):
        coef = [c * other for c in self.coefficients[:2]] + self.coefficients[2:]
        return SumAtan(coefficients=coef, domain=self.domain, coord_sys=self.coord_sys)

    def _truediv(self, other):
        raise NotImplementedError


@dataclasses.dataclass
class GaussianProcess(Profile):
    """
    A gaussian process.

    Examples
        >>> from numpy import allclose
        >>> import w7x
        >>> domain = [0, 0.2, 0.6, 1]
        >>> values = [1, 0.96, 0.64, 0]
        >>> gp = w7x.lib.profiles.GaussianProcess(
        ...     values,
        ...     domain)

        >>> allclose(gp(0), 1.0, rtol=1e-4)
        True

        >>> allclose(gp(0.6), 0.64, rtol=1e-4)
        True

        Achtung: data are stored as coefficients
        >>> gp.coefficients = [2, 0.96, 0.64, 0]
        >>> allclose(gp(0), 2.0, rtol=1e-4)
        True

        >>> gp = w7x.lib.profiles.GaussianProcess.fit(
        ...     x=domain, y=values)
        >>> allclose(gp(0), 1.0, rtol=1e-4)
        True
    """

    constraints: typing.List[callable] = dataclasses.field(default_factory=lambda: [])

    def __init__(
        self, coefficients, domain, coord_sys=None, constraints=None, **kwargs
    ):
        super().__init__(coefficients, domain, coord_sys)

        self.constraints = constraints
        self._gp_kwargs = copy.deepcopy(kwargs)

        gp = GaussianProcessRegressor(**kwargs)
        domain = np.array(self.domain).reshape(-1, 1)
        values = np.array(self.coefficients).reshape(domain.shape)
        gp.fit(domain, values)
        self._gp = gp

    def sample_y(self, x, **kwargs):
        """Draw samples from Gaussian process and evaluate at x.

        Args:
            kwargs: keyword arguments to be passed to the GP sample_y method.

        Returns:
            The samples as a ndarray of shape (n_samples, n_samples_X, [n_output_dims]).
        """

        self._update()
        samples = self._sample_y(x, **kwargs)

        if self.constraints is not None:
            n_samples = samples.shape[0]
            while True:
                for constraint_fn in self.constraints:
                    samples = np.array([s for s in samples if constraint_fn(s).all()])
                n_left = n_samples - samples.shape[0]
                if n_left <= 0:
                    break
                #  Sample 100 * n_left to speed up the sampling
                new_samples = self._sample_y(x, n_samples=n_left * 100)
                if len(samples) != 0:
                    samples = np.vstack((samples, new_samples))
                else:
                    samples = new_samples
            #  Make sure we return the requested number of samples
            samples = samples[:n_samples]

        return samples

    def _sample_y(self, x, **kwargs):
        samples = self._gp.sample_y(
            x.reshape(-1, 1), random_state=np.random.randint(1e6), **kwargs
        )
        samples = np.moveaxis(samples, [0, 1, 2], [1, 2, 0]).reshape((-1, *x.shape))
        return samples

    def _call(self, x):
        return self.sample_y(x).reshape(x.shape)

    @classmethod
    def _fit(cls, x, y, **kwargs):
        return cls(coefficients=y, domain=x)

    def _mul(self, other):
        values = [v * other for v in self.coefficients]
        return GaussianProcess(
            coefficients=values,
            domain=self.domain,
            coord_sys=self.coord_sys,
            **self._gp_kwargs
        )

    def _truediv(self, other):
        raise NotImplementedError

    def _update(self):
        """Check if fitted values are changed, and in case update GP."""
        domain = np.array(self.domain).reshape(-1, 1)
        values = np.array(self.coefficients).reshape(domain.shape)
        if not (
            np.all(np.equal(domain, self._gp.X_train_))
            and np.all(np.equal(values, self._gp.y_train_))
        ):
            self._gp.fit(domain, values)


def tanh(x, l1, l2, l0, lw):
    return (l1 + l2) / 2 - (l1 - l2) / 2 * np.tanh((x - l0) / lw)


class HigdonSwallKernKernel(NormalizedKernelMixin, Kernel):
    """
    A non-stationary kernel with hyperbolic tangent as length scale function.

    TODO-2(@amerlo): provide gradient computation for hp optimization.
    TODO-2(@amerlo): once gradient computation is there, remove "fixed" from default.
    """

    def __init__(
        self,
        l1=1.0,
        l2=1.0,
        l0=0,
        lw=1.0,
        l1_bounds="fixed",
        l2_bounds="fixed",
        l0_bounds="fixed",
        lw_bounds="fixed",
    ):
        self.l1 = l1
        self.l1_bounds = l1_bounds
        self.l2 = l2
        self.l2_bounds = l2_bounds
        self.l0 = l0
        self.l0_bounds = l0_bounds
        self.lw = lw
        self.lw_bounds = lw_bounds

    def __call__(self, X, Y=None, eval_gradient=False):

        if eval_gradient:
            raise NotImplementedError

        X = np.atleast_2d(X)
        if Y is None:
            Y = X
        sigma_x = tanh(X, self.l1, self.l2, self.l0, self.lw)
        sigma_y = tanh(Y, self.l1, self.l2, self.l0, self.lw)
        denom = (sigma_x[:, None, :] ** 2 + sigma_y[None, :, :] ** 2).sum(axis=-1)
        dist = cdist(X, Y, "sqeuclidean") / denom
        factor = 2 * (sigma_x[:, None, :] * sigma_y[None, :, :]).sum(axis=-1) / denom
        K = np.sqrt(factor) * np.exp(-dist)
        return K

    def __repr__(self):
        return "{0}(l1={1:.3g}, l2={2:.3g}, l0={3:.3g}, lw={4:.3g})".format(
            self.__class__.__name__, self.l1, self.l2, self.l0, self.lw
        )

    def is_stationary(self):
        return False

    @property
    def hyperparameter_l1(self):
        return Hyperparameter("l1", "numeric", self.l1_bounds)

    @property
    def hyperparameter_l2(self):
        return Hyperparameter("l2", "numeric", self.l2_bounds)

    @property
    def hyperparameter_l0(self):
        return Hyperparameter("l0", "numeric", self.l0_bounds)

    @property
    def hyperparameter_lw(self):
        return Hyperparameter("lw", "numeric", self.lw_bounds)
