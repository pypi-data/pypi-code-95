#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
"""
import warnings
import typing
import numpy as np
import tfields
import logging
from tfields.lib.decorators import cached_property


class Triangles3D(tfields.TensorFields):
    # pylint: disable=R0904
    """
    Points3D child restricted to n * 3 Points.
    Three Points always group together to one triangle.

    Args:
        tensors (Iterable | tfields.TensorFields)
        *fields (Iterable | tfields.Tensors): Fields with the same length as tensors
        **kwargs: passed to base class

    Attributes:
        see :class:`~tfields.TensorFields`

    Examples:
        >>> import tfields
        >>> t = tfields.Triangles3D([[1,2,3], [3,3,3], [0,0,0]])

        You can add fields to each triangle

        >>> t = tfields.Triangles3D(t, tfields.Tensors([42]))
        >>> assert t.fields[0].equal([42])

    """

    def __new__(cls, tensors, *fields, **kwargs):
        kwargs["dim"] = 3
        kwargs["rigid"] = False
        obj = super(Triangles3D, cls).__new__(cls, tensors, *fields, **kwargs)

        if not len(obj) % 3 == 0:
            warnings.warn(
                "Input object of size({0}) has no divider 3 and"
                " does not describe triangles.".format(len(obj))
            )
        return obj

    def ntriangles(self):
        """
        Returns:
            int: number of triangles
        """
        return len(self) // 3

    def _to_triangles_mask(self, mask):
        mask = np.array(mask)
        mask = mask.reshape((self.ntriangles(), 3))
        mask = mask.all(axis=1)
        return mask

    def __getitem__(self, index):
        """
        In addition to the usual, also slice fields

        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> vectors = tfields.Tensors(np.array([range(30)] * 3).T)
            >>> triangles = tfields.Triangles3D(vectors, range(10))
            >>> assert np.array_equal(triangles[3:6],
            ...                       [[3] * 3,
            ...                        [4] * 3,
            ...                        [5] * 3])
            >>> assert triangles[3:6].fields[0][0] == 1

        """
        item = super(tfields.TensorFields, self).__getitem__(index)
        try:  # __iter__ will try except __getitem__(i) until IndexError
            if issubclass(type(item), Triangles3D):  # block int, float, ...
                if len(item) % 3 != 0:
                    item = tfields.Tensors(item)
                elif item.fields:
                    # build triangle index / indices / mask when possible
                    tri_index = None
                    if isinstance(index, tuple):
                        index = index[0]

                    if isinstance(index, int):
                        pass
                    elif isinstance(index, slice):
                        start = index.start or 0
                        stop = index.stop or len(self)
                        step = index.step
                        if start % 3 == 0 and (stop - start) % 3 == 0 and step is None:
                            tri_index = slice(start // 3, stop // 3)
                    else:
                        try:
                            tri_index = self._to_triangles_mask(index)
                        except ValueError:
                            pass

                    # apply triangle index to fields
                    if tri_index is not None:
                        item.fields = [
                            field.__getitem__(tri_index) for field in item.fields
                        ]
                    else:
                        item = tfields.Tensors(item)
        except IndexError:
            logging.warning(
                "Index error occured for field.__getitem__. Error "
                "message: {err}".format(**locals())
            )
        return item

    @classmethod
    def _load_stl(cls, path):
        """
        Factory method
        Given a path to a stl file, construct the object
        """
        import stl.mesh

        triangles = stl.mesh.Mesh.from_file(path)
        obj = cls(triangles.vectors.reshape(-1, 3))
        return obj

    @classmethod
    def merged(cls, *objects, **kwargs):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            obj = super(Triangles3D, cls).merged(*objects, **kwargs)
        if not len(obj) % 3 == 0:
            warnings.warn(
                "Input object of size({0}) has no divider 3 and"
                " does not describe triangles.".format(len(obj))
            )
        return obj

    def evalf(self, expression=None, coord_sys=None):
        """
        Triangle3D implementation

        Examples:
            >>> from sympy.abc import x
            >>> t = tfields.Triangles3D([[1., 2., 3.], [-4., 5., 6.], [1, 2, -6],
            ...                          [5, -5, -5], [1,0,-1], [0,1,-1],
            ...                          [-5, -5, -5], [1,0,-1], [0,1,-1]])
            >>> mask = t.evalf(x >= 0)
            >>> assert np.array_equal(t[mask],
            ...                       tfields.Triangles3D([[ 5., -5., -5.],
            ...                                            [ 1.,  0., -1.],
            ...                                            [ 0.,  1., -1.]]))

        Returns:
            np.array: mask which is True, where expression evaluates True
        """
        mask = super(Triangles3D, self).evalf(expression, coord_sys=coord_sys)
        mask = self._to_triangles_mask(mask)
        mask = np.array([mask] * 3).T.reshape((len(self)))
        return mask

    def cut(self, expression, coord_sys=None):
        """
        Default cut method for Triangles3D

        Examples:
            >>> import sympy
            >>> import tfields
            >>> x, y, z = sympy.symbols('x y z')
            >>> t = tfields.Triangles3D([[1., 2., 3.], [-4., 5., 6.], [1, 2, -6],
            ...                          [5, -5, -5], [1, 0, -1], [0, 1, -1],
            ...                          [-5, -5, -5], [1, 0, -1], [0, 1, -1]])
            >>> tc = t.cut(x >= 0)
            >>> assert tc.equal(tfields.Triangles3D([[ 5., -5., -5.],
            ...                                      [ 1.,  0., -1.],
            ...                                      [ 0.,  1., -1.]]))
            >>> t.fields.append(tfields.Tensors([1,2,3]))
            >>> tc2 = t.cut(x >= 0)
            >>> assert np.array_equal(tc2.fields[-1], np.array([2.]))

        """
        # mask = self.evalf(expression, coord_sys=coord_sys)
        # inst = self[mask].copy()
        # return inst
        return super().cut(expression, coord_sys)

    def mesh(self):
        """
        Returns:
            tfields.Mesh3D
        """
        mp = tfields.TensorFields(np.arange(len(self)).reshape((-1, 3)), *self.fields)
        mesh = tfields.Mesh3D(self, maps=[mp])
        return mesh.cleaned(stale=False)  # stale vertices can not occure here

    @cached_property()
    def _areas(self):
        """
        Cached method to retrieve areas of triangles
        """
        transform = np.eye(3)
        return self.areas(transform=transform)

    def areas(self, transform=None):
        """
        Calculate area with "heron's formula"

        Args:
            transform (np.ndarray): optional transformation matrix
                The triangle points are transformed with transform if given
                before calclulating the area

        Examples:
            >>> m = tfields.Mesh3D([[1,0,0], [0,0,1], [0,0,0]],
            ...                    faces=[[0, 1, 2]])
            >>> assert np.allclose(m.triangles().areas(), np.array([0.5]))

            >>> m = tfields.Mesh3D([[1,0,0], [0,1,0], [0,0,0], [0,0,1]],
            ...                    faces=[[0, 1, 2], [1, 2, 3]])
            >>> assert np.allclose(m.triangles().areas(), np.array([0.5, 0.5]))

            >>> m = tfields.Mesh3D([[1,0,0], [0,1,0], [1,1,0], [0,0,1], [1,0,1]],
            ...                    faces=[[0, 1, 2], [0, 3, 4]])
            >>> assert np.allclose(m.triangles().areas(), np.array([0.5, 0.5]))

        """
        if transform is None:
            return self._areas
        else:
            indices = range(self.ntriangles())
            aIndices = [i * 3 for i in indices]
            bIndices = [i * 3 + 1 for i in indices]
            cIndices = [i * 3 + 2 for i in indices]

            # define 3 vectors building the triangle, transform it back and take their norm

            if not np.array_equal(transform, np.eye(3)):
                a = np.linalg.norm(
                    np.linalg.solve(
                        transform.T, (self[aIndices, :] - self[bIndices, :]).T
                    ),
                    axis=0,
                )
                b = np.linalg.norm(
                    np.linalg.solve(
                        transform.T, (self[aIndices, :] - self[cIndices, :]).T
                    ),
                    axis=0,
                )
                c = np.linalg.norm(
                    np.linalg.solve(
                        transform.T, (self[bIndices, :] - self[cIndices, :]).T
                    ),
                    axis=0,
                )
            else:
                a = np.linalg.norm(self[aIndices, :] - self[bIndices, :], axis=1)
                b = np.linalg.norm(self[aIndices, :] - self[cIndices, :], axis=1)
                c = np.linalg.norm(self[bIndices, :] - self[cIndices, :], axis=1)

            # sort by length for numerical stability
            lengths = np.concatenate(
                (a.reshape(-1, 1), b.reshape(-1, 1), c.reshape(-1, 1)), axis=1
            )
            lengths.sort()
            a, b, c = lengths.T

            return 0.25 * np.sqrt(
                (a + (b + c)) * (c - (a - b)) * (c + (a - b)) * (a + (b - c))
            )

    def corners(self):
        """
        Returns:
            three np.arrays with corner points of triangles
        """
        indices = range(self.ntriangles())
        aIndices = [i * 3 for i in indices]
        bIndices = [i * 3 + 1 for i in indices]
        cIndices = [i * 3 + 2 for i in indices]

        a = self.bulk[aIndices, :]
        b = self.bulk[bIndices, :]
        c = self.bulk[cIndices, :]
        return a, b, c

    def circumcenters(self):
        """
        Semi baricentric method to calculate circumcenter points of the
        triangles

        Examples:
            >>> m = tfields.Mesh3D([[0,0,0], [1,0,0], [-1,0,0], [0,1,0], [0,0,1]],
            ...                    faces=[[0, 1, 3],[0, 2, 3],[1,2,4], [1, 3, 4]]);
            >>> assert np.allclose(
            ...     m.triangles().circumcenters(),
            ...     [[0.5, 0.5, 0.0],
            ...      [-0.5, 0.5, 0.0],
            ...      [0.0, 0.0, 0.0],
            ...      [1.0 / 3, 1.0 / 3, 1.0 / 3]])

        """
        pointA, pointB, pointC = self.corners()
        a = np.linalg.norm(
            pointC - pointB, axis=1
        )  # side length of side opposite to pointA
        b = np.linalg.norm(pointC - pointA, axis=1)
        c = np.linalg.norm(pointB - pointA, axis=1)
        bary1 = a ** 2 * (b ** 2 + c ** 2 - a ** 2)
        bary2 = b ** 2 * (a ** 2 + c ** 2 - b ** 2)
        bary3 = c ** 2 * (a ** 2 + b ** 2 - c ** 2)
        matrices = np.concatenate((pointA, pointB, pointC), axis=1).reshape(
            pointA.shape + (3,)
        )
        # transpose the inner matrix
        matrices = np.einsum("...ji", matrices)
        vectors = np.array((bary1, bary2, bary3)).T
        # matrix vector product for matrices and vectors
        P = np.einsum("...ji,...i", matrices, vectors)
        P /= vectors.sum(axis=1).reshape((len(vectors), 1))
        return tfields.Points3D(P)

    @cached_property()
    def _centroids(self):
        """
        this version is faster but takes much more ram also.
        So much that i get memory error with a 32 GB RAM
        """
        nT = self.ntriangles()
        mat = np.ones((1, 3)) / 3.0
        # matrix product calculatesq center of all triangles
        return tfields.Points3D(
            np.dot(mat, self.reshape(nT, 3, 3))[0], coord_sys=self.coord_sys
        )

        """
        Old version:
        pointA, pointB, pointC = self.corners()
        return Points3D(1. / 3 * (pointA + pointB + pointC)), coord_sys=self.coord_sys
        This versioin was slightly slower (110 % of new version)
        Memory usage of new version is better for a factor of 4 or so.
        Not really reliable method of measurement
        """

    def centroids(self):
        """
        Returns:
            :func:`~tfields.Triangles3D._centroids`

        Examples:
            >>> m = tfields.Mesh3D([[0,0,0], [1,0,0], [-1,0,0], [0,1,0], [0,0,1]],
            ...                    faces=[[0, 1, 3],[0, 2, 3],[1,2,4], [1, 3, 4]]);
            >>> assert m.triangles().centroids().equal(
            ...     [[1./3, 1./3, 0.],
            ...      [-1./3, 1./3, 0.],
            ...      [0., 0., 1./3],
            ...      [1./3, 1./3, 1./3]])

        """
        return self._centroids

    def edges(self):
        """
        Retrieve two of the three edge vectors

        Returns:
            two np.ndarrays: vectors ab and ac, where a, b, c are corners (see
                self.corners)
        """
        a, b, c = self.corners()

        ab = b - a
        ac = c - a

        return ab, ac

    def norms(self):
        """
        Examples:
            >>> m = tfields.Mesh3D([[0,0,0], [1,0,0], [-1,0,0], [0,1,0], [0,0,1]],
            ...                    faces=[[0, 1, 3],[0, 2, 3],[1,2,4], [1, 3, 4]]);
            >>> assert np.allclose(m.triangles().norms(),
            ...                    [[0.0, 0.0, 1.0],
            ...                     [0.0, 0.0, -1.0],
            ...                     [0.0, 1.0, 0.0],
            ...                     [0.57735027] * 3],
            ...                    atol=1e-8)

        """
        ab, ac = self.edges()
        vectors = np.cross(ab, ac)
        norms = np.apply_along_axis(np.linalg.norm, 0, vectors.T).reshape(-1, 1)
        # cross product may be zero, so replace zero norms by ones to divide vectors by norms
        np.place(norms, norms == 0.0, 1.0)
        return vectors / norms

    def _baricentric(self, point, delta=0.0):
        """
        Determine baricentric coordinates like

        [u,v,w] = [ab, ac, ab x ac]^-1 * ap
        where ax is vector from point a to point x

        Examples:
            empty Meshes return right formatted array
            >>> m = tfields.Mesh3D([], faces=[])
            >>> m.triangles()._baricentric(np.array([0.2, 0.2, 0]))
            array([], dtype=float64)

            >>> m2 = tfields.Mesh3D([[0,0,0], [2,0,0], [0,2,0], [0,0,2]],
            ...                     faces=[[0, 1, 2], [0, 2, 3]]);
            >>> assert np.array_equal(
            ...     m2.triangles()._baricentric(np.array([0.2, 0.2, 0]),
            ...                                 delta=2.),
            ...     [[0.1, 0.1, 0.0],
            ...      [0.1, 0.0, 0.1]])

            if point lies in the plane, return np.nan, else inf for w if delta
            is exactly 0.

            >>> baric = m2.triangles()._baricentric(np.array([0.2, 0.2, 0]),
            ...                                             delta=0.),
            >>> baric_expected = np.array([[0.1, 0.1, np.nan],
            ...                            [0.1, 0.0, np.inf]])
            >>> assert ((baric == baric_expected) | (np.isnan(baric) &
            ...                                      np.isnan(baric_expected))).all()

        Raises:
            If you define triangles that have colinear side vectors or in general lead to
            not invertable matrices [ab, ac, ab x ac] the values will be nan and
            a warning will be triggered:
            >>> import warnings
            >>> m3 = tfields.Mesh3D([[0,0,0], [2,0,0], [4,0,0], [0,1,0]],
            ...                     maps=[[[0, 1, 2], [0, 1, 3]]]);
            >>> with warnings.catch_warnings(record=True) as wrn:
            ...     warnings.simplefilter("ignore")
            ...     bc = m3.triangles()._baricentric(np.array([0.2, 0.2, 0]), delta=0.3)
            >>> bc_exp = np.array([[ np.nan,  np.nan,  np.nan], [ 0.1,  0.2,  0. ]])
            >>> assert ((bc == bc_exp) | (np.isnan(bc) &
            ...                           np.isnan(bc_exp))).all()

            The warning would be:
                UserWarning('Singular matrix: Could not invert matrix ...
                    ... [[ 2.  4.  0.], [ 0.  0.  0.], [ 0.  0.  0.]]. Return nan matrix.',)

        Returns:
            np.ndarray: barycentric coordinates u, v, w of point with respect to each triangle
        """
        if self.ntriangles() == 0:
            return np.array([])

        a, _, _ = self.corners()

        ap = point - a
        # matrix vector product for matrices and vectors
        barCoords = np.einsum("...ji,...i", self._baricentric_matrix, ap)
        with warnings.catch_warnings():
            # python2.7
            warnings.filterwarnings(
                "ignore", message="invalid value encountered in divide"
            )
            warnings.filterwarnings(
                "ignore", message="divide by zero encountered in divide"
            )
            # python3.x
            warnings.filterwarnings(
                "ignore", message="invalid value encountered in true_divide"
            )
            warnings.filterwarnings(
                "ignore", message="divide by zero encountered in true_divide"
            )
            barCoords[:, 2] /= delta  # allow devide by 0.
        return barCoords

    @cached_property()
    def _baricentric_matrix(self):
        """
        cached barycentric matrix for faster calculations
        """
        ab, ac = self.edges()

        # get norm vector TODO: replace by norm = self.norms()
        norm = np.cross(ab, ac)
        normLen = np.linalg.norm(norm, axis=1)
        normLen = normLen.reshape((1,) + normLen.shape)
        colinear_mask = normLen == 0
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
            # prevent divide by 0
            norm[np.where(~colinear_mask.T)] = (
                norm[np.where(~colinear_mask.T)] / normLen.T[np.where(~colinear_mask.T)]
            )

        matrix = np.concatenate((ab, ac, norm), axis=1).reshape(ab.shape + (3,))
        matrix = np.einsum("...ji", matrix)  # transpose the inner matrix

        # invert matrix if possible
        # matrixI = np.linalg.inv(matrix)  # one line variant without exception
        matrixI = []
        for mat in matrix:
            try:
                matrixI.append(np.linalg.inv(mat))
            except np.linalg.linalg.LinAlgError as e:
                if str(e) == "Singular matrix":
                    warnings.warn(
                        "Singular matrix: Could not invert matrix "
                        "{0}. Return nan matrix.".format(str(mat).replace("\n", ","))
                    )
                    matrixI.append(np.full((3, 3), np.nan))
        return np.array(matrixI)

    def _in_triangles(self, point, delta=0.0):
        """
        Barycentric method to optain, wheter a point is in any of the triangles

        Args:
            point (list of len 3)
            delta (float / None):
                float: acceptance in +- norm vector direction
                None: accept the face with the minimum distance to the point

        Returns:
            np.array: boolean mask, True where point in a triangle within delta

        Examples:
            see tests/test_triangles_3d.py
        """

        if self.ntriangles() == 0:
            return np.array([], dtype=bool)

        try:
            point = np.reshape(point, 3)
        except ValueError:
            raise ValueError(
                "point must be castable to shape 3 but is of shape {0}".format(
                    point.shape
                )
            )

        # min_dist_method switch if delta is None
        if delta is None:
            delta = 1.0
            min_dist_method = True
        else:
            min_dist_method = False

        u, v, w = self._baricentric(point, delta=delta).T

        if delta == 0.0:
            w[np.isnan(w)] = 0.0  # division by 0 in baricentric makes w = 0 nan.

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", message="invalid value encountered in less_equal"
            )
            barycentric_bools = (
                ((v <= 1.0) & (v >= 0.0)) & ((u <= 1.0) & (u >= 0.0)) & ((v + u <= 1.0))
            )
            if all(~barycentric_bools):
                return barycentric_bools
            if min_dist_method:
                orthogonal_acceptance = np.full(
                    barycentric_bools.shape, False, dtype=bool
                )
                closest_indices = np.argmin(abs(w)[barycentric_bools])
                # transform the indices to the whole array, not only the
                # barycentric_bools selection
                closest_indices = np.arange(len(barycentric_bools))[barycentric_bools][
                    closest_indices
                ]
                orthogonal_acceptance[closest_indices] = True
            else:
                orthogonal_acceptance = abs(w) <= 1

        return np.array(barycentric_bools & orthogonal_acceptance)

    def in_triangles(
        self,
        tensors,
        delta: typing.Optional[float] = 0.0,
        assign_multiple: bool = False,
    ) -> typing.Union[typing.List[typing.List[int]], np.array]:
        """
        Barycentric method to obtain, which tensors are containes in any of the triangles

        Args:
            tensors (Points3D instance)

            optional:
            delta:
                :obj:`float`: Normal distance to a triangle, that the points
                    are concidered to be contained in the triangle.
                :obj:`None`: Find the minimum distance.
                Default is 0.
            assign_multiple: If True, one point may belong to multiple
                triangles at the same time. In the other case the first
                occurence will be True the other False

        Returns:
            list: [index(or indices if assign_multiple) of triangle for point in tensors]
        """
        indices = np.full(tensors.shape[0], -1, dtype=int)
        if self.ntriangles() == 0:
            if assign_multiple:
                return [[-1] * len(indices)]
            else:
                return indices

        with tensors.tmp_transform(self.coord_sys):
            for i, point in enumerate(iter(tensors)):
                mask = self._in_triangles(point, delta)
                if np.any(mask):
                    if assign_multiple:
                        index = np.argwhere(mask == np.amax(mask))
                        index.flatten().tolist()
                        indices.append(index)
                    else:
                        indices[i] = np.argmax(mask)
                else:
                    if assign_multiple:
                        indices.append([-1])
                    else:
                        indices[i] = -1
        return indices

    def _on_edges(self, point):
        """
        Determine whether a point is on the edge / side ray of a triangle

        TODO:
            on_edges like in_triangles

        Returns:
            np.array: boolean mask which is true, if point is on one side ray
            of a triangle

        Examples:
            >>> m = tfields.Mesh3D([[0,0,0], [1,0,0], [-1,0,0], [0,1,0], [0,0,1]],
            ...                    faces=[[0, 1, 3],[0, 2, 3],[1,2,4]]);

            Corner points are found

            >>> assert np.array_equal(
            ...     m.triangles()._on_edges(tfields.Points3D([[0,1,0]])),
            ...     np.array([ True,  True, False], dtype=bool))

            Side points are found, too

            >>> assert np.array_equal(
            ...     m.triangles()._on_edges(tfields.Points3D([[0.5,0,0.5]])),
            ...     np.array([False, False,  True], dtype=bool))

        """
        u, v, w = self._baricentric(point, 1.0).T

        orthogonal_acceptance = w == 0  # point should lie in triangle
        barycentric_bools = (
            (((0.0 <= v) & (v <= 1.0)) & (u == 0.0))
            | (((0.0 <= u) & (u <= 1.0)) & (v == 0.0))
            | (v + u == 1.0)
        )
        return np.array(barycentric_bools & orthogonal_acceptance)

    def _weights(self, weights, rigid=False):
        """
        transformer method for weights inputs.

        Args:
            weights (np.ndarray | int | None):
                If weights is integer it will be used as index for fields and fields are
                used as weights.
                If weights is None it will
                Otherwise just pass the weights.

        Returns:

        TODO: Better docs
        """
        # set weights to 1.0 if weights is None
        if weights is None:
            weights = np.ones(self.ntriangles())
        return super(Triangles3D, self)._weights(weights, rigid=rigid)


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
