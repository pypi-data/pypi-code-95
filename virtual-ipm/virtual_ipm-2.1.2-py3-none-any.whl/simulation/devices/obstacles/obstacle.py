from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import trimesh


class Obstacle:
    def collide(self, positions: np.ndarray) -> np.ndarray:
        """Determine which of the given positions collide with the obstacle.

        Parameters
        ----------
        positions : np.ndarray of shape (3, N)
            The three-dimensional positions of N particles.

        Returns
        -------
        np.ndarray of shape (N,)
            A boolean array with an entry for each particle: True if the particle
            collided with the obstacle and False otherwise.
        """
        raise NotImplementedError


class Box(Obstacle):
    """A three-dimensional box with faces perpendicular to the coordinate axes.

    Parameters
    ----------
    center : tuple[float, float, float]
        The xyz-coordinates of the box' center.
    size : tuple[float, float, float]
        The xyz-edge lengths of the box.
    """

    def __init__(
        self,
        *,
        center: tuple[float, float, float],
        size: tuple[float, float, float],
    ):

        super().__init__()
        self.center = np.asarray(center)[:, np.newaxis]
        self.half_size = np.asarray(size)[:, np.newaxis] / 2

    def collide(self, positions: np.ndarray) -> np.ndarray:
        positions = positions - self.center
        return np.all(
            positions == np.clip(positions, -self.half_size, self.half_size),
            axis=0,
        )


class MultilayerObstacle(Obstacle):
    def __init__(self, obstacles: Sequence[Obstacle]):
        self.obstacles = obstacles

    def collide(self, positions: np.ndarray) -> np.ndarray:
        mask = np.ones(positions.shape[1], dtype=bool)
        for obstacle in self.obstacles:
            mask[mask] = obstacle.collide(positions[:, mask])
        return mask


class STLObstacle(Obstacle):
    """Create an obstacle from a .STL file."""

    def __init__(self, filepath: str):
        self.mesh = trimesh.load_mesh(filepath)
        self.corners = trimesh.bounds.corners(self.mesh.bounding_box.bounds)
        self.sides = self.mesh.bounding_box.primitive.extents

    def collide(self, positions: np.ndarray) -> np.ndarray:
        if positions.shape[1] > 0:
            signed_distance = trimesh.proximity.signed_distance(self.mesh, positions.T)
            return np.asarray(signed_distance >= 0)
        return np.array([], dtype=bool)
