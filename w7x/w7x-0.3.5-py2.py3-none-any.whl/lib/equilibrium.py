#  pylint: disable=invalid-name
"""
Components of a plasma equilibrium.

Tasks
-----

TODO-1(@amerlo): add common algebraic operations between series.
TODO-1(@amerlo): move this file under w7x/model/....py
TODO-1(@dboe,@amerlo): think about best representation in tfields
"""

import abc
import dataclasses
import typing
import numpy as np

import rna.polymorphism


def interp(x, xp, fp):
    """
    Vectorize linear interpolation.

    See numpy.interp.
    """

    fp = np.asarray(fp)

    shape = fp.shape[1:]
    fp = fp.reshape((xp.shape[0], -1))

    y = np.array([np.interp(x, xp, fp[:, i]) for i in range(fp.shape[1])]).T.reshape(
        (-1, *shape)
    )

    return y


def validate_coef(coef, set_null: bool):
    """
    Validate Fourier coefficients.

    Args:
        coef (array_like): Fourier coefficients.
        set_null (bool): set Fourier coefficients with poloidal mode numbers
            equal to 0 and negative toroidal mode numbers to 0.

    Returns:
        The Fourier coefficients.
    """

    coef = np.array(coef)
    shape = coef.shape

    if len(shape) != 3:
        raise TypeError(
            "Coefficients array must be a 3-dimensional array, "
            "instead an array of shape %s has been given." % str(shape)
        )

    if coef.shape[2] % 2 == 0:
        raise TypeError(
            "The number of toroidal modes %s must be an odd number" % coef.shape[2]
        )

    ntor = int((coef.shape[2] - 1) / 2)
    if set_null and ntor > 0:
        coef[:, 0, :ntor] = 0

    return coef


@dataclasses.dataclass
class FourierTerm(abc.ABC):
    """
    A representation for a generic Fourier term in toroidal coordinates.

    TODO-1(@amelo): rename coef to coefficients

    Args:
        coef (array_like): coefficients array
        num_field_periods (int): number of field periods

    Examples:
        >>> import w7x
        >>> axis = w7x.lib.equilibrium.Cos.from_coefficients(
        ...    [1.0, 5.5, 0.1], mpol=0, ntor=1, num_field_periods=5)

        >>> axis.num_radial_locations
        1

        >>> axis.set_null()
        >>> axis.coef
        array([[[0. , 5.5, 0.1]]])
    """

    coef: np.ndarray = None
    num_field_periods: int = 1

    def __post_init__(self):

        if self.coef is None:
            raise TypeError("Coefficients array must be non-empty")
        self.coef = validate_coef(self.coef, set_null=False)

    def __call__(self, *points, rtol=0.0, atol=0.0, equal_nan=False) -> float:
        """
        Evaluate Fourier term at given location.

        If a tfields object is given, the coordinate system is taken from the object.
        Otherwise, assume `points` to be defined in toroidal coordinates (s, theta, phi).

        A linear interpolation is used if the s coordinate is outside of the series domain.

        Args:
            points (array-like):
                Input points where to evaluate the Fourier series.
                They should be 3-dimensional objects.
            rtol (float): see numpy.isclose
            atol (float): see numpy.isclose
            equal_nan (bool): see numpy.isclose

        TODO-2(@amerlo): support points3D and tensors coordinate mapping.

        Examples:
            >>> import w7x
            >>> axis = w7x.lib.equilibrium.Cos.from_coefficients(
            ...    [[1.0, 5.5, 0.1], [-0.2, 0.5, 0.3]],
            ...    mpol=0, ntor=1, num_field_periods=5)

            Input could be a simple list
            >>> axis([0.0, 0.0, 0.0])
            array(6.6)

            Or a Points3D
            >>> import tfields
            >>> p = tfields.Points3D([[0.0, 0.0, 0.0]])
            >>> axis(p)
            array(6.6)
        """

        xs = np.array(*points).reshape(-1, 3)

        if (xs[:, 0] < 0).any() or (xs[:, 0] > 1).any():
            raise ValueError("The radial-like `s` coordinate is out of range.")

        #  Validate normalized flux values
        domain = np.linspace(0, 1, num=self.num_radial_locations, endpoint=True)[
            :, np.newaxis
        ]
        is_close = np.isclose(
            xs[:, 0], domain, rtol=rtol, atol=atol, equal_nan=equal_nan
        )

        #  Columns are the input values, rows are the domain values
        #  TODO-2(@amerlo): add not valid input in the exception msg
        if not is_close.any(axis=0).all():
            raise ValueError("An input s value is not in Fourier series domain")

        coef = interp(xs[:, 0], domain[:, 0], self.coef)

        #  Build in advance poloidal and toroidal modes outside of vectorize
        poloidal_modes = np.arange(self.mpol + 1, dtype=int)
        toroidal_modes = np.arange(-self.ntor, self.ntor + 1, dtype=int)

        y = np.zeros(xs.shape[0])
        for i in range(xs.shape[0]):

            y[i] = self._call(
                xs[i, 1],
                xs[i, 2],
                coef=coef[i],
                poloidal_modes=poloidal_modes,
                toroidal_modes=toroidal_modes,
                num_field_periods=self.num_field_periods,
            )

        return np.squeeze(y)

    @classmethod
    def from_coefficients(
        cls,
        coef: typing.List[typing.Union[list, float]],
        mpol: int = 1,
        ntor: int = 1,
        **kwargs,
    ):
        """
        Factory method to create Fourier series from list of coefficients.

        Examples:
            >>> import numpy as np
            >>> import w7x
            >>> axis = w7x.lib.equilibrium.Cos.from_coefficients(
            ...    [0.0, 5.5, 0.1], mpol=0, ntor=1, num_field_periods=5)
            >>> axis([0, 0, 0])
            array(5.6)

            >>> axis([0, 0, np.pi])
            array(5.4)

            >>> axis.poloidal_modes
            [0]

            >>> axis.toroidal_modes
            [-1, 0, 1]

            It supports vmec list structure too
            >>> vmec_axis = w7x.lib.equilibrium.Cos.from_coefficients(
            ...    [5.5, 0.1], mpol=0, ntor=1, num_field_periods=5)

            >>> vmec_axis.coef
            array([[[0. , 5.5, 0.1]]])

            >>> vmec_axis([0, 0, 0])
            array(5.6)
        """

        if coef is None:
            raise TypeError("Coefficients array must be non-empty")

        coef = np.asarray(coef)

        #  Infer radial resolution
        num_coefs = (mpol + 1) * (2 * ntor + 1)

        if len(coef.shape) == 2:
            #  Assume [s, ...]
            ns = coef.shape[0]
        else:
            #  Assume vmec shape
            ns = int(coef.size / num_coefs) + (coef.size % num_coefs > 0)

        shape = (ns, mpol + 1, 2 * ntor + 1)

        #  Check if given shape matches Fourier modes
        if len(coef.shape) == 3:
            if coef.shape[1:] == shape[1:]:
                return cls(coef=coef, **kwargs)
            else:
                raise TypeError(
                    "The shape of the given coefficients %s "
                    "does not match the expected shape from mpol and ntor %s"
                    % (str(coef.shape), str(shape))
                )

        try:
            coef = coef.reshape(shape)
            return cls(coef=coef, **kwargs)
        except ValueError:
            coef_ = np.zeros((ns, num_coefs))
            try:
                coef_[:, ntor:] = coef.reshape((ns, -1))
                coef = coef_.reshape(shape)
                return cls(coef=coef, **kwargs)
            except ValueError:
                raise TypeError(
                    "The shape of the given coefficients could not be inferred"
                )

    def linspace(
        self,
        ns=None,
        ntheta=36,
        nphi=36,
        domain_s=None,
        domain_theta=None,
        domain_phi=None,
    ):
        """
        Return (s, theta, phi), y values at equally spaced points in domain.

        Examples:
            >>> import w7x
            >>> axis = w7x.lib.equilibrium.Cos.from_coefficients(
            ...     [0.0, 0.0, 5.5, 0.1, 0.03], mpol=0, ntor=2, num_field_periods=5)
            >>> axis.linspace(ntheta=1, nphi=5)[1]
            array([5.63, 5.47, 5.43, 5.47, 5.63])
        """

        if domain_s is None:
            domain_s = [0, 1]

        if domain_theta is None:
            domain_theta = [0, 2 * np.pi]

        if domain_phi is None:
            domain_phi = [0, 2 * np.pi / self.num_field_periods]

        if ns is None:
            ns = self.shape[0]

        ss = np.linspace(domain_s[0], domain_s[1], num=ns, endpoint=True)
        theta = np.linspace(domain_theta[0], domain_theta[1], ntheta)
        phi = np.linspace(domain_phi[0], domain_phi[1], nphi)

        grid = np.stack(np.meshgrid(ss, theta, phi), -1).reshape(-1, 3)
        y = self(grid)

        return (ss, theta, phi), y

    def set_null(self):
        self.coef = validate_coef(self.coef, set_null=True)

    def truncated(self, mpol: int = None, ntor: int = None):
        """
        Returns a truncated copy of the Fourier series.

        Examples:
            >>> import w7x
            >>> axis = w7x.lib.equilibrium.Cos.from_coefficients(
            ...    [0.0, 0.0, 5.5, 0.1, 0.03], mpol=0, ntor=2, num_field_periods=5)
            >>> axis([0, 0, 0])
            array(5.63)

            >>> truncated_axis = axis.truncated(ntor=1)
            >>> truncated_axis([0, 0, 0])
            array(5.6)

            >>> axis = w7x.lib.equilibrium.Cos.from_coefficients(
            ...    [0.0, 5.5, 0.1, 0.03, 0.0, 0.0], mpol=1, ntor=1, num_field_periods=5)
            >>> truncated_axis = axis.truncated(mpol=0, ntor=1)
            >>> truncated_axis.coef
            array([[[0. , 5.5, 0.1]]])

        """

        if mpol is None or mpol > self.mpol:
            mpol = self.mpol

        if ntor is None or ntor > self.ntor:
            ntor = self.ntor

        return self.__class__(
            coef=self.coef[:, : mpol + 1, self.ntor - ntor : self.ntor + ntor + 1],
            num_field_periods=self.num_field_periods,
        )

    def plot(self, *args, **kwargs):
        """
        Plot Fourier Series.

        TODO-2(@amerlo): implement me!
        """
        #  w7x.plotting.vmec.plot_fourier(self, *args, **kwargs)
        pass

    @property
    def shape(self) -> typing.Tuple[int]:
        """
        Shape of the Fourier series.
        """
        return self.coef.shape

    @property
    def num_radial_locations(self) -> int:
        """
        Number of radial locations.
        """
        return self.shape[0]

    @property
    def poloidal_modes(self) -> typing.List[int]:
        """
        The poloidal mode numbers.
        """
        return list(range(self.mpol + 1))

    @property
    def toroidal_modes(self) -> typing.List[int]:
        """
        The toroidal mode numbers.
        """
        return list(range(-self.ntor, self.ntor + 1))

    @property
    def mpol(self) -> int:
        """
        The highest poloidal mode number.
        """
        return self.shape[1] - 1

    @property
    def ntor(self) -> int:
        """
        The highest toroidal mode number.
        """
        return int((self.shape[2] - 1) / 2)

    @staticmethod
    @abc.abstractmethod
    def _call(theta, phi, coef, num_field_periods):
        raise NotImplementedError


@dataclasses.dataclass
class Cos(FourierTerm):
    """
    A cosine series term.

    Examples:
        >>> import numpy as np
        >>> import w7x
        >>> cos = w7x.lib.equilibrium.Cos([[[0.0, 5.5, 0.1]]], num_field_periods=5)
        >>> cos([0, 0, 0])
        array(5.6)

        >>> cos([0, 0, np.pi])
        array(5.4)

    """

    @staticmethod
    def _call(theta, phi, coef, poloidal_modes, toroidal_modes, num_field_periods):
        r"""
        Evaluate the cosine series described by coefficients at the given angle position.

        This function computes:

        .. math::
            \sum_{mn} coef_{mn} \cos{m \theta - nfp n \phi}
        """

        poloidal_modes = poloidal_modes[:, None]
        toroidal_modes = toroidal_modes[None, :]

        weight = np.cos(
            poloidal_modes * theta - num_field_periods * toroidal_modes * phi
        )
        return (coef * weight).sum()


@dataclasses.dataclass
class Sin(FourierTerm):
    """
    A sine series term.

    Examples:
        >>> import numpy as np
        >>> import w7x
        >>> sin = w7x.lib.equilibrium.Sin([[[0.0, 0.0, 0.33]]], num_field_periods=5)
        >>> sin([0, 0, 0])
        array(0.)

        >>> sin([0, 0, np.pi / 2 / 5])
        array(-0.33)

    """

    @staticmethod
    def _call(theta, phi, coef, poloidal_modes, toroidal_modes, num_field_periods):
        r"""
        Evaluate the series value at a single position.

        This function computes:

        .. math::
            \sum_{mn} coef_{mn} \sin{m \theta - nfp n \phi}
        """

        poloidal_modes = poloidal_modes[:, None]
        toroidal_modes = toroidal_modes[None, :]

        weight = np.sin(
            poloidal_modes * theta - num_field_periods * toroidal_modes * phi
        )
        return (coef * weight).sum()


@dataclasses.dataclass
class Fourier:
    """
    A Fourier series.

    Examples:
        >>> import w7x

        Create a Fourier series object from a Cos and Sin terms
        >>> cos = w7x.lib.equilibrium.Cos([[[0.0, 5.5, 0.1]]], num_field_periods=5)
        >>> sin = w7x.lib.equilibrium.Sin([[[0.0, 0.0, 0.33]]], num_field_periods=5)
        >>> series = w7x.lib.equilibrium.Fourier(cos=cos, sin=sin)

        Or by directly passing the related coefficients
        >>> series = w7x.lib.equilibrium.Fourier(
        ...     cos=[[[0.0, 5.5, 0.1]]],
        ...     sin=[[[0.0, 0.0, 0.33]]],
        ...     num_field_periods=5)

    """

    def __init__(self, cos: Cos = None, sin: Sin = None, num_field_periods: int = 1):
        if cos is None and sin is None:
            raise TypeError("At least a term of the series must be not None")

        if isinstance(cos, Cos) and isinstance(sin, Sin):
            if cos.num_field_periods != sin.num_field_periods:
                raise TypeError(
                    "Cosine and sine terms must have the same number "
                    "of field periods."
                )
        elif isinstance(cos, Cos):
            if sin is not None:
                sin = Sin(coef=sin, num_field_periods=cos.num_field_periods)
        elif isinstance(sin, Sin):
            if cos is not None:
                cos = Cos(coef=cos, num_field_periods=sin.num_field_periods)
        else:
            if cos is not None:
                cos = Cos(coef=cos, num_field_periods=num_field_periods)
            if sin is not None:
                sin = Sin(coef=sin, num_field_periods=num_field_periods)

        self.cos = cos
        self.sin = sin

    def __call__(self, *args, **kwargs):
        """
        Compute the Fourier series value at the given locations as the sum of
        the cosine and sine terms.

        See w7x.lib.equilibrium.Cos and w7x.lib.equilibrium.Sin.
        """

        if self.sin is None:
            return self.cos(*args, **kwargs)

        if self.cos is None:
            return self.sin(*args, **kwargs)

        return self.cos(*args, **kwargs) + self.sin(*args, **kwargs)

    @classmethod
    def from_coefficients(
        cls,
        cos: typing.List[typing.Union[None, list, float]] = None,
        sin: typing.List[typing.Union[None, list, float]] = None,
        **kwargs,
    ):
        """
        Construct a Fourier series from coefficients.
        """

        if cos is None and sin is None:
            raise TypeError("At least a term of the series must be not None")

        if cos is not None:
            cos = Cos.from_coefficients(coef=cos, **kwargs)

        if sin is not None:
            sin = Sin.from_coefficients(coef=sin, **kwargs)

        return cls(cos=cos, sin=sin)

    @property
    def num_field_periods(self):
        """
        The number of toroidal field periods of the Fourier series.
        """
        return (
            self.cos.num_field_periods
            if self.sin is None
            else self.sin.num_field_periods
        )

    def plot(self, *args, **kwargs):
        """
        TODO-2(@amerlo): implement me!
        """
        pass


@dataclasses.dataclass
class TensorSeries(rna.polymorphism.Storable):
    """
    A representation for a generic tensor with Fourier coefficients.

    Examples:
        >>> import numpy as np
        >>> import w7x
        >>> rcos = w7x.lib.equilibrium.Cos([[[0.0, 5.5, 0.2]]], num_field_periods=5)
        >>> zsin = w7x.lib.equilibrium.Sin([[[0.0, 0.0, 0.1]]], num_field_periods=5)
        >>> axis = w7x.lib.equilibrium.TensorSeries(
        ...     w7x.lib.equilibrium.Fourier(cos=rcos),
        ...     w7x.lib.equilibrium.Fourier(sin=zsin))
        >>> res = axis([0, 0, 0])
        >>> res.shape == (2, )
        True

        >>> res = axis([[0, 0, 0], [0, 0, np.pi / 2 / 5], [0, np.pi / 2, 0]])
        >>> res.shape == (3, 2)
        True

        >>> axis.ndim
        2

    """

    def __init__(self, *args):
        """
        Factory method for a TensorSeries.
        """
        self.dims = list(args)

    def __call__(self, *args, **kwargs):
        """
        Evaluate the tensor series at given locations.

        See w7x.lib.equilibrium.Fourier.
        """
        return np.squeeze(np.stack([dim(*args, **kwargs) for dim in self.dims], -1))

    @property
    def ndim(self) -> int:
        """
        Number of tensor dimensions.
        """
        return len(self.dims)
