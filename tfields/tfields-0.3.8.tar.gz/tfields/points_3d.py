#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

basic threedimensional tensors
"""
import numpy as np
import tfields


class Points3D(tfields.Tensors):
    # pylint: disable=R0904
    """
    Points3D is a general class for 3D Point operations and storage.
    Points are stored in np.arrays of shape (len, 3).
    Thus the three coordinates of the Points stay close.

    Args:
        points3DInstance  -> copy constructor
        [points3DInstance1, points3DInstance2, ...]  -> coord_sys are correctly treated
        list of coordinates (see examples)

    Kwargs:
        coord_sys (str):
            Use tfields.bases.CARTESIAN -> x, y, z
            Use tfields.bases.CYLINDER -> r, phi, z
            Use tfields.bases.SPHERICAL -> r, phi, theta

    Examples:
        Initializing with 3 vectors
        >>> import tfields
        >>> import numpy as np
        >>> p1 = tfields.Points3D([[1., 2., 3.], [4., 5., 6.], [1, 2, -6]])
        >>> assert p1.equal([[1., 2., 3.],
        ...                  [4., 5., 6.],
        ...                  [1., 2., -6.]])

        Initializing with list of coordinates
        >>> p2 = tfields.Points3D(np.array([[1., 2., 3., 4, 5,],
        ...                                 [4., 5., 6., 7, 8],
        ...                                 [1, 2, -6, -1, 0]]).T)
        >>> assert p2.equal(
        ...     [[ 1.,  4.,  1.],
        ...      [ 2.,  5.,  2.],
        ...      [ 3.,  6., -6.],
        ...      [ 4.,  7., -1.],
        ...      [ 5.,  8.,  0.]], atol=1e-8)
        >>> p2.transform(tfields.bases.CYLINDER)
        >>> assert p2.equal(
        ...     [[ 4.12310563, 1.32581766,  1.],
        ...      [ 5.38516481, 1.19028995,  2.],
        ...      [ 6.70820393, 1.10714872, -6.],
        ...      [ 8.06225775, 1.05165021, -1.],
        ...      [ 9.43398113, 1.01219701,  0.]], atol=1e-8)

        Copy constructor with one instance preserves coord_sys of instance
        >>> assert tfields.Points3D(p2).coord_sys == p2.coord_sys

        Unless you specify other:
        >>> assert tfields.Points3D(p2,
        ...                         coord_sys=tfields.bases.CARTESIAN).equal(
        ...    [[ 1.,  4.,  1.],
        ...     [ 2.,  5.,  2.],
        ...     [ 3.,  6., -6.],
        ...     [ 4.,  7., -1.],
        ...     [ 5.,  8.,  0.]], atol=1e-8)

        Copy constructor with many instances chooses majority of coordinates
        systems to avoid much transformation
        >>> assert tfields.Points3D.merged(p1, p2, p1).equal(
        ...     [[ 1.,  2.,  3.],
        ...      [ 4.,  5.,  6.],
        ...      [ 1.,  2., -6.],
        ...      [ 1.,  4.,  1.],
        ...      [ 2.,  5.,  2.],
        ...      [ 3.,  6., -6.],
        ...      [ 4.,  7., -1.],
        ...      [ 5.,  8.,  0.],
        ...      [ 1.,  2.,  3.],
        ...      [ 4.,  5.,  6.],
        ...      [ 1.,  2., -6.]], atol=1e-8)
        >>> p1.transform(tfields.bases.CYLINDER)

        ... unless specified other. Here it is specified
        >>> assert tfields.Points3D.merged(
        ...     p1, p2, coord_sys=tfields.bases.CYLINDER).equal(
        ...     [[ 2.23606798,  1.10714872,  3.        ],
        ...      [ 6.40312424,  0.89605538,  6.        ],
        ...      [ 2.23606798,  1.10714872, -6.        ],
        ...      [ 4.12310563,  1.32581766,  1.        ],
        ...      [ 5.38516481,  1.19028995,  2.        ],
        ...      [ 6.70820393,  1.10714872, -6.        ],
        ...      [ 8.06225775,  1.05165021, -1.        ],
        ...      [ 9.43398113,  1.01219701,  0.        ]], atol=1e-8)

        Shape is always (..., 3)
        >>> p = tfields.Points3D([[1., 2., 3.], [4., 5., 6.],
        ...                       [1, 2, -6], [-5, -5, -5], [1,0,-1], [0,1,-1]])
        >>> p.shape
        (6, 3)

        Empty array will create an ndarray of the form (0, 3)
        >>> tfields.Points3D([])
        Points3D([], shape=(0, 3), dtype=float64)

        Use it as np.ndarrays -> masking etc. is inherited
        >>> mask = np.array([True, False, True, False, False, True])
        >>> mp = p[mask].copy()

        Copy constructor
        >>> assert mp.equal(
        ...     [[ 1.,  2.,  3.],
        ...      [ 1.,  2., -6.],
        ...      [ 0.,  1., -1.]])
        >>> assert tfields.Points3D(mp).equal(
        ...     [[ 1.,  2.,  3.],
        ...      [ 1.,  2., -6.],
        ...      [ 0.,  1., -1.]])

        Coordinate system is implemented. Default is cartesian
        >>> p_cart = p.copy()
        >>> p.transform(tfields.bases.CYLINDER)
        >>> assert p.equal(
        ...     tfields.Points3D([[2.236,  1.107,  3.],
        ...                       [6.403,  0.896,  6.],
        ...                       [2.236,  1.107, -6.],
        ...                       [7.071, -2.356, -5.],
        ...                       [1.   ,  0.   , -1.],
        ...                       [1.   ,  1.571, -1.]],
        ...                      coord_sys=tfields.bases.CYLINDER),
        ...     atol=1e-3)
        >>> p.transform(tfields.bases.CARTESIAN)
        >>> assert p.equal(p_cart, atol=1e-15)

    """

    def __new__(cls, tensors, **kwargs):
        if not issubclass(type(tensors), Points3D):
            kwargs["dim"] = 3
        return super(Points3D, cls).__new__(cls, tensors, **kwargs)

    def balls(self, radius, spacing=(5, 3)):
        """
        Args:
            radius (float): radius of spheres
            spacing (tuple of int): n_phi, n_theta
        Returns:
            tfields.Mesh3D: Builds a sphere around each point with a resolution
                defined by spacing and given radius
        """
        sphere = tfields.Mesh3D.grid(
            (radius, radius, 1),
            (-np.pi, np.pi, spacing[0]),
            (-np.pi / 2, np.pi / 2, spacing[1]),
            coord_sys="spherical",
        )
        sphere.transform("cartesian")
        balls = []
        with self.tmp_transform("cartesian"):
            for point in self:
                ball = sphere.copy()
                ball += point
                balls.append(ball)
        return tfields.Mesh3D.merged(*balls)


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
    # doctest.run_docstring_examples(Points3D, globals())
