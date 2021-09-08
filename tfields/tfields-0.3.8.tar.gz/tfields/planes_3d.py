#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
"""
import tfields
import sympy
import numpy as np
import rna


class Planes3D(tfields.TensorFields):
    """
    Point-NormVector representaion of planes

    Examples:
        >>> import tfields
        >>> points = [[0, 1, 0]]
        >>> norms = [[0, 0, 1]]
        >>> plane = tfields.Planes3D(points, norms)
        >>> plane.symbolic()[0]
        Plane(Point3D(0, 1, 0), (0, 0, 1))

    """

    def symbolic(self):
        """
        Returns:
            list: list with sympy.Plane objects
        """
        return [
            sympy.Plane(point, normal_vector=vector)
            for point, vector in zip(self, self.fields[0])
        ]

    def plot(self, **kwargs):  # pragma: no cover
        """
        forward to Mesh3D plotting
        """
        artists = []
        centers = np.array(self)
        norms = np.array(self.fields[0])
        for i in range(len(self)):
            artists.append(rna.plotting.plot_plane(centers[i], norms[i], **kwargs))
        return artists


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
