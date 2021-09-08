#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
Tools for sympy coordinate transformation
"""
import tfields
import numpy as np
import sympy
import sympy.diffgeom
from six import string_types
import warnings


def get_coord_system(base):
    """
    Args:
        base (str or sympy.diffgeom.get_coord_system)
    Return:
        sympy.diffgeom.get_coord_system
    """
    if isinstance(base, string_types) or (
        isinstance(base, np.ndarray) and base.dtype.kind in {"U", "S"}
    ):
        base = getattr(tfields.bases, str(base))
    if not isinstance(base, sympy.diffgeom.CoordSystem):
        bse_tpe = type(base)
        expctd_tpe = type(sympy.diffgeom.CoordSystem)
        raise TypeError(
            "Wrong type of coord_system base {bse_tpe}. "
            "Expected {expctd_tpe}".format(**locals())
        )
    return base


def get_coord_system_name(base):
    """
    Args:
        base (str or sympy.diffgeom.get_coord_system)
    Returns:
        str: name of base
    """
    if isinstance(base, sympy.diffgeom.CoordSystem):
        base = getattr(base, "name")
    # if not (isinstance(base, string_types) or base is None):
    #     baseType = type(base)
    #     raise ValueError("Coordinate system must be string_type."
    #                      " Retrieved value '{base}' of type {baseType}."
    #                      .format(**locals()))
    return str(base)


def lambdified_trafo(base_old, base_new):
    """
    Args:
        base_old (sympy.CoordSystem)
        base_new (sympy.CoordSystem)

    Examples:
        >>> import numpy as np
        >>> import tfields

        Transform cartestian to cylinder or spherical
        >>> a = np.array([[3,4,0]])

        >>> trafo = tfields.bases.lambdified_trafo(tfields.bases.cartesian,
        ...                                        tfields.bases.cylinder)
        >>> new = np.concatenate([trafo(*coords).T for coords in a])
        >>> assert new[0, 0] == 5

        >>> trafo = tfields.bases.lambdified_trafo(tfields.bases.cartesian,
        ...                                        tfields.bases.spherical)
        >>> new = np.concatenate([trafo(*coords).T for coords in a])
        >>> assert new[0, 0] == 5

    """
    coords = tuple(base_old.coord_function(i) for i in range(base_old.dim))
    f = sympy.lambdify(
        coords,
        base_old.coord_tuple_transform_to(base_new, list(coords)),
        modules="numpy",
    )
    return f


def transform(array, base_old, base_new, **kwargs):
    """
    Transform the input array in place
    Args:
        array (np.ndarray)
        base_old (str or sympy.CoordSystem):
        base_new (str or sympy.CoordSystem):
    Examples:
        Cylindrical coordinates
        >>> import tfields
        >>> cart = np.array([[0, 0, 0],
        ...                  [1, 0, 0],
        ...                  [1, 1, 0],
        ...                  [0, 1, 0],
        ...                  [-1, 1, 0],
        ...                  [-1, 0, 0],
        ...                  [-1, -1, 0],
        ...                  [0, -1, 0],
        ...                  [1, -1, 0],
        ...                  [0, 0, 1]])
        >>> cyl = tfields.bases.transform(cart, 'cartesian', 'cylinder')
        >>> cyl

        Transform cylinder to spherical. No connection is defined so routing via
        cartesian
        >>> import numpy as np
        >>> import tfields
        >>> b = np.array([[5, np.arctan(4. / 3), 0]])
        >>> newB = b.copy()
        >>> tfields.bases.transform(b, 'cylinder', 'spherical')
        >>> assert newB[0, 0] == 5
        >>> assert round(newB[0, 1], 10) == round(b[0, 1], 10)

    """
    base_old = get_coord_system(base_old)
    base_new = get_coord_system(base_new)

    # very fast trafos in numpy only
    short_trafo = None
    try:
        short_trafo = getattr(base_old, f"to_{base_new.name}".format(**locals()))
    except AttributeError:
        pass
    if short_trafo:
        short_trafo(array, **kwargs)
        return

    if base_new not in base_old.transforms:
        for baseTmp in base_new.transforms:
            if baseTmp in base_old.transforms:
                transform(array, base_old, baseTmp, **kwargs)
                transform(array, baseTmp, base_new, **kwargs)
                return
        raise ValueError(f"Transformation {base_old} -> {base_new} not found.")

    # trafo via lambdified sympy expressions
    trafo = tfields.bases.lambdified_trafo(base_old, base_new)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="invalid value encountered in double_scalars"
        )
        array[:] = np.concatenate([trafo(*coords).T for coords in array])


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
