import numpy as np


class Space:
    def __init__(self, bounds, pbc):
        # bounds = [[lowest_crd1, lowest_crd2,...], [highest1, highest2, ...]]
        # pbc = [is_dim1_periodic, is_dim2_periodic, ...]
        self.dim = len(bounds[0])
        self.bounds = bounds
        self.bounds = self.bounds.astype(np.float)
        self.pbcdims = np.array(range(self.dim))[np.array(pbc)]
        self.nonpbcdims = np.array(range(self.dim))[np.logical_not(pbc)]

    def vec(self, to, frompt):
        # calculate vector1 (to) - vector2 (frompt) accounting for pbc
        result = to - frompt
        for j in self.pbcdims:
            a = -(self.bounds[1][j] - self.bounds[0][j]) / 2
            l = self.bounds[1][j] - self.bounds[0][j]
            result[j] = (result[j] - a) % l + a

        return result

    def crds(self, points):
        # replace any points outside of range of a nonpbc dim with nan
        # project any points outside of range of a pbc dim to within bounds
        for j in self.nonpbcdims:
            points[points[:, j] < self.bounds[0][j], :] = np.nan
            points[points[:, j] > self.bounds[1][j], :] = np.nan

        for j in self.pbcdims:
            a = self.bounds[0][j]
            l = self.bounds[1][j] - a
            points[:, j] = (points[:, j] - a) % l + a

        return points

    def trace(self, start, target, bo, eps, max_e):
        direction = self.vec(target, start)
        length = np.linalg.norm(direction)
        if length < eps:
            return target
        for i in range(1, int(length / eps)):
            test_point = start + i * eps * direction / np.linalg.norm(direction)
            test_point = self.crds(np.array([test_point]))[0]
            energy = bo.get_mu(np.vstack(np.atleast_2d(test_point)))[0, 0]
            if energy > max_e:
                l = np.linalg.norm(direction)
                prev_point = start + (i - 1) * eps * direction / l
                prev_point = self.crds(np.array([prev_point]))[0]
                return prev_point
        return target
