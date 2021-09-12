import numpy as np


class Path:
    def __init__(self, space, crds=None, i=None, j=None, energy=None):
        """
        connection  ...
        space       (Space) The Space class defines boundaries and periodicity.
        """
        self.mi = i
        self.mj = j
        self.space = space
        self.crds = crds
        self.energy = energy
        self.maxe = np.max(energy)

    def initFromConnection(self, connection):
        # Indexes of the minima that this path connects
        self.mi, self.mj = [connection[0].name, connection[1].name]

        # combine a path from the two trees
        end_node_A, end_node_B = connection
        parents_A = end_node_A.get_all_parents()
        parents_B = end_node_B.get_all_parents()
        parents_A.reverse()
        crds = np.array([]).reshape(0, end_node_A.coords.shape[0])
        for node in parents_A:
            crds = np.vstack((crds, node.coords))
        crds = np.vstack((crds, end_node_A.coords, end_node_B.coords))
        for node in parents_B:
            crds = np.vstack((crds, node.coords))
        self.crds = crds

    def reform(self, eps):
        """
        Reform with points at eps distance from another

        Parameters:
        eps         (float) Separation of points in the new path.
        """
        newpath = np.atleast_2d(self.crds[0, :])
        next_i = 1
        prev_pt = self.crds[0, :]  # point from where to find next
        direction = self.space.vec(self.crds[next_i, :], self.crds[next_i - 1, :])
        nextdist = np.linalg.norm(direction)  # dist to next point in orig path
        direction = direction / nextdist  # (make it a unit vector)
        prevdist = 0  # dist from prev point in new path
        while True:
            # Starting from first point in path, go along the path, adding
            # points at eps distance from another
            if nextdist >= (eps - prevdist):
                # A new point needs to be added before encountering the next
                # point in the old path
                newpoint = prev_pt + (eps - prevdist) * direction
                newpoint = self.space.crds(np.array([newpoint]))[0]
                newpath = np.vstack((newpath, newpoint))
                prev_pt = newpoint
                nextdist = nextdist - (eps - prevdist)
                prevdist = 0
            else:
                # Next point in old path encountered before a new point can be
                # added: change direction and remember how much distance was
                # covered before this direction change
                if next_i == self.crds.shape[0] - 1:  # if next point is the last
                    newpath = np.vstack((newpath, self.crds[next_i, :]))
                    self.crds = newpath
                    return
                d = np.linalg.norm(
                    self.space.vec(
                        newpath[newpath.shape[0] - 1, :], self.crds[next_i, :]
                    )
                )
                prevdist = d
                prev_pt = self.crds[next_i, :]
                next_i += 1
                direction = self.space.vec(
                    self.crds[next_i, :], self.crds[next_i - 1, :]
                )
                nextdist = np.linalg.norm(direction)
                direction = direction / nextdist
