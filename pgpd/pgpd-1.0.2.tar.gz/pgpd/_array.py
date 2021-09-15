#
# PyGEOS ExtensionDType & ExtensionArray
#
import numbers
from collections.abc import Iterable
import numpy as np
import pandas as pd
import pygeos
from pandas.api.extensions import ExtensionArray, ExtensionDtype, register_extension_dtype

try:
    from shapely.geometry.base import BaseGeometry as ShapelyGeometry
except ImportError:
    ShapelyGeometry = None

__all__ = ['GeosDtype', 'GeosArray']


class GeosDtype(ExtensionDtype):
    type = pygeos.lib.Geometry      #: Underlying type of the individual Array elements
    name = 'geos'                   #: Dtype string name
    na_value = pd.NA                #: NA Value that is used on the user-facing side

    @classmethod
    def construct_from_string(cls, string):
        """
        Construct this type from a string (ic. :attr:`~GeosDtype.name`).

        Args:
            string (str): The name of the type.

        Returns:
            GeosDtype: instance of the dtype.

        Raises:
            TypeError: string is not equal to "geos".
        """
        if string == cls.name:
            return cls()
        else:
            raise TypeError(f'Cannot construct a "{cls.__name__}" from "{string}"')

    @classmethod
    def construct_array_type(cls):
        """
        Return the array type associated with this dtype.

        Return:
            GeosArray: Associated ExtensionArray.
        """
        return GeosArray


register_extension_dtype(GeosDtype)


class GeosArray(ExtensionArray):
    dtype = GeosDtype()     #: Dtype for this ExtensionArray
    ndim = 1                #: Number of dimensions of this ExtensionArray

    # -------------------------------------------------------------------------
    # (De-)Serialization
    # -------------------------------------------------------------------------
    def __init__(self, data):
        """
        Create a GeosArray.

        Args:
            data (Iterable): Data for the GeosArray (see Note)

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.

        Raises:
            ValueError: data is not of correct type

        Note:
            The ``data`` argument can be one of different types:

            - *GeosArray* |br|
                Shallow copy of the internal data.
            - *None or pygeos.lib.Geometry* |br|
                Wrap data in an array.
            - *Iterable of pygeos.lib.Geometry* |br|
                use ``np.asarray(data)``.
        """
        if isinstance(data, self.__class__):
            self.data = data.data
        elif data is None or isinstance(data, self.dtype.type):
            self.data = np.array((data,))
        elif isinstance(data, Iterable):
            val = next((d for d in data if d is not None), None)
            if val is None or isinstance(val, self.dtype.type):
                self.data = np.asarray(data)
            else:
                raise TypeError(f'Data should be an iterable of {self.dtype.type}')
        else:
            raise ValueError(f'Data should be an iterable of {self.dtype.type}')

        self.data[pd.isna(self.data)] = None

    @classmethod
    def from_shapely(cls, data, **kwargs):
        """
        Create a GeosArray from shapely data. |br|
        This function is a simple wrapper around :func:`pygeos.io.from_shapely`.

        Args:
            data: Shapely data or list of shapely data.
            kwargs: Keyword arguments passed to :func:`~pygeos.io.from_shapely`.

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.
        """
        data = pygeos.io.from_shapely(data, **kwargs)
        return cls(data)

    @classmethod
    def from_wkb(cls, data, **kwargs):
        """
        Create a GeosArray from WKB data. |br|
        This function is a simple wrapper around :func:`pygeos.io.from_wkb`.

        Args:
            data: WKB data or list of WKB data.
            kwargs: Keyword arguments passed to :func:`~pygeos.io.from_wkb`.

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.
        """
        data = pygeos.io.from_wkb(data, **kwargs)
        return cls(data)

    @classmethod
    def from_wkt(cls, data, **kwargs):
        """
        Create a GeosArray from WKT data. |br|
        This function is a simple wrapper around :func:`pygeos.io.from_wkt`.

        Args:
            data: WKT data or list of WKT data.
            kwargs: Keyword arguments passed to :func:`~pygeos.io.from_wkt`.

        Returns:
            pgpd.GeosArray: Data wrapped in a GeosArray.
        """
        data = pygeos.io.from_wkt(data, **kwargs)
        return cls(data)

    def to_shapely(self, **kwargs):
        """
        Transform the GeosArray to a NumPy array of shapely objects.

        Returns:
            numpy.ndarray: Array with the shapely data.
        """
        return pygeos.io.to_shapely(self.data, **kwargs)

    def to_wkb(self, **kwargs):
        """
        Transform the GeosArray to a NumPy array of WKB bytes. |br|
        This function is a simple wrapper around :func:`pygeos.io.to_wkb`.

        Args:
            kwargs: Keyword arguments passed to :func:`~pygeos.io.to_wkb`.

        Returns:
            numpy.ndarray: Array with the WKB data.
        """
        return pygeos.io.to_wkb(self.data, **kwargs)

    def to_wkt(self, **kwargs):
        """
        Transform the GeosArray to a NumPy array of WKT strings. |br|
        This function is a simple wrapper around :func:`pygeos.io.to_wkt`.

        Args:
            kwargs: Keyword arguments passed to :func:`~pygeos.io.to_wkt`.

        Returns:
            numpy.ndarray: Array with the WKT data.
        """
        return pygeos.io.to_wkt(self.data, **kwargs)

    # -------------------------------------------------------------------------
    # ExtensionArray Specific
    # -------------------------------------------------------------------------
    @classmethod
    def _from_sequence(cls, scalars, dtype=None, copy=False):
        if isinstance(scalars, (str, bytes)) or not isinstance(scalars, Iterable):
            scalars = (scalars,)

        values = np.array(scalars)
        if copy:
            values = values.copy()
        val = next((v for v in values if v is not None), None)

        if isinstance(val, str):
            return cls.from_wkt(values)
        elif isinstance(val, bytes):
            return cls.from_wkb(values)
        elif ShapelyGeometry is not None and isinstance(val, ShapelyGeometry):
            return cls.from_shapely(values)

        return cls(values)

    def _values_for_factorize(self):
        return self.data, None

    @classmethod
    def _from_factorized(cls, values, original):
        return cls(values)

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return self.data[key]

        key = pd.api.indexers.check_array_indexer(self, key)
        if isinstance(key, (Iterable, slice)):
            return GeosArray(self.data[key])
        else:
            raise TypeError('Index type not supported', key)

    def __setitem__(self, key, value):
        key = pd.api.indexers.check_array_indexer(self, key)

        if isinstance(key, (slice, list, np.ndarray)):
            if isinstance(value, self.__class__):
                value = value.data
            else:
                value = self._from_sequence(value)

            self.data[key] = value
        else:
            if isinstance(value, Iterable):
                raise ValueError('cannot set a single element with an array')

            if pd.isna(value):
                self.data[key] = None
            elif isinstance(value, str):
                self.data[key] = pygeos.io.from_wkt(value)
            elif isinstance(value, bytes):
                self.data[key] = pygeos.io.from_wkb(value)
            elif ShapelyGeometry is not None and isinstance(value, ShapelyGeometry):
                self.data[key] = pygeos.io.from_shapely(value)
            else:
                self.data[key] = value

    def __len__(self):
        return self.data.shape[0]

    def __eq__(self, other):
        if isinstance(other, (pd.Series, pd.Index, pd.DataFrame)):
            return NotImplemented

        if isinstance(other, self.__class__):
            return self.data == other.data

        return self.data == other

    @property
    def nbytes(self):
        return self.data.nbytes

    def isna(self):
        return pygeos.is_missing(self.data)

    def take(self, indices, allow_fill=False, fill_value=None):
        from pandas.core.algorithms import take

        if allow_fill:
            if fill_value is None or pd.isna(fill_value):
                fill_value = None
            elif not isinstance(fill_value, self.dtype.type):
                raise TypeError('Provide geometry or None as fill value')

        result = take(self.data, indices, allow_fill=allow_fill, fill_value=fill_value)

        if allow_fill and fill_value is None:
            result[pd.isna(result)] = None

        return self.__class__(result)

    def copy(self, order='C'):
        return GeosArray(self.data.copy(order))

    @classmethod
    def _concat_same_type(cls, to_concat):
        data = np.concatenate([c.data for c in to_concat])
        return cls(data)

    def _values_for_argsort(self):
        """
        Return values for sorting.

        Raises:
            TypeError: Geometries are not sortable.
        """
        raise TypeError('geometries are not sortable')

    # -------------------------------------------------------------------------
    # NumPy Specific
    # -------------------------------------------------------------------------
    @property
    def size(self):
        return self.data.size

    @property
    def shape(self):
        return self.data.shape

    def __array__(self, dtype=None):
        """ Return internal NumPy array. """
        return self.data

    # -------------------------------------------------------------------------
    # Custom Methods
    # -------------------------------------------------------------------------
    def affine(self, matrix):
        r"""
        Performs a 2D or 3D affine transformation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                =
                \begin{bmatrix}
                    a & b & x_{off} \\
                    d & e & y_{off} \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                =
                \begin{bmatrix}
                    a & b & c & x_{off} \\
                    d & e & f & y_{off} \\
                    g & h & i & z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}

        Args:
            matrix (numpy.ndarray or list-like): Affine transformation matrix.

        Returns:
            pgpd.GeosArray: Transformed geometries

        Note:
            The transformation matrix can be one of the following types:

            - numpy.ndarray <3x3 or 2x3> |br|
              Performs a 2D affine transformation, where the last row of homogeneous coordinates can optionally be discarded.
            - list-like <6> |br|
              Performs a 2D affine transformation, where the `matrix` represents **(a, b, d, e, xoff, yoff)**.
            - numpy.ndarray <4x4 or 3x4> |br|
              Performs a 3D affine transformation, where the last row of homogeneous coordinates can optionally be discarded.
            - list-like <12> |br|
              Performs a 3D affine transformation, where the `matrix` represents **(a, b, c, d, e, f, g, h, i, xoff, yoff, zoff)**.
        """
        # Get Correct Affine transformation matrix
        if isinstance(matrix, np.ndarray):
            r, c = matrix.shape
            zdim = c == 4
            if r == 2:
                matrix = np.append(matrix, [[0, 0, 1]], axis=0)
            elif c == 4 and r == 3:
                matrix = np.append(matrix, [[0, 0, 0, 1]], axis=0)
        elif len(matrix) == 6:
            zdim = False
            matrix = np.array([
                [matrix[0], matrix[1], matrix[4]],
                [matrix[2], matrix[3], matrix[5]],
                [0,         0,         1],
            ])
        elif len(matrix) == 12:
            zdim = True
            matrix = np.array([
                [matrix[0], matrix[1], matrix[2], matrix[9]],
                [matrix[3], matrix[4], matrix[5], matrix[10]],
                [matrix[6], matrix[7], matrix[8], matrix[11]],
                [0,         0,         0,         1],
            ])

        matrix = matrix[None, ...]

        # Coordinate Function
        def _affine(points):
            points = np.c_[points, np.ones(points.shape[0])][..., None]
            return (matrix @ points)[:, :-1, 0]

        return self.__class__(pygeos.coordinates.apply(self.data, _affine, zdim))

    def __add__(self, other):
        """
        Performs an addition between the coordinates array and other.

        Args:
            other (array-like): Item to add to the coordinates.

        Note:
            When adding the coordinates array and `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we decide whether to use the Z-dimension,
            depending on the shape of `other`:

            - `other.shape[-1] == 2`: Do not use Z-dimension.
            - `other.shape[-1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.
        """
        other = np.asarray(other)
        shape = other.ndim and other.shape[-1]

        if shape == 2:
            zdim = False
        elif shape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: pt + other,
            zdim,
        ))

    def __radd__(self, other):
        """
        Performs an right-addition between the coordinates array and other.

        Args:
            other (array-like): Item to add to the coordinates.

        Note:
            When adding the coordinates array and `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we decide whether to use the Z-dimension,
            depending on the shape of `other`:

            - `other.shape[-1] == 2`: Do not use Z-dimension.
            - `other.shape[-1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.
        """
        other = np.asarray(other)
        shape = other.ndim and other.shape[-1]

        if shape == 2:
            zdim = False
        elif shape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: other + pt,
            zdim,
        ))

    def __mul__(self, other):
        """
        Performs a multiplication between the coordinates array and other.

        Args:
            other (array-like): Item to add to the coordinates.

        Note:
            When multiplying the coordinates array and `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we decide whether to use the Z-dimension,
            depending on the shape of `other`:

            - `other.shape[-1] == 2`: Do not use Z-dimension.
            - `other.shape[-1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.
        """
        other = np.asarray(other)
        shape = other.ndim and other.shape[-1]

        if shape == 2:
            zdim = False
        elif shape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: pt * other,
            zdim,
        ))

    def __rmul__(self, other):
        """
        Performs a right-multiplication between the coordinates array and other.

        Args:
            other (array-like): Item to add to the coordinates.

        Note:
            When multiplying the coordinates array and `other`, standard NumPy broadcasting rules apply.
            In order to reduce the friction for users, we decide whether to use the Z-dimension,
            depending on the shape of `other`:

            - `other.shape[-1] == 2`: Do not use Z-dimension.
            - `other.shape[-1] == 3`: Do use Z-dimension.
            - `else`: Use Z-dimension if there are any.
        """
        other = np.asarray(other)
        shape = other.ndim and other.shape[-1]

        if shape == 2:
            zdim = False
        elif shape == 3:
            zdim = True
        else:
            zdim = pygeos.predicates.has_z(self.data).any()

        return self.__class__(pygeos.coordinates.apply(
            self.data,
            lambda pt: other * pt,
            zdim,
        ))
