import numpy as np
from boss.mep.forest import Forest
from boss.mep.neb import neb
from boss.mep.node import Node
from boss.mep.path import Path


class MEP:
    def __init__(
        self,
        bo,
        space,
        min_points,
        precision=25,
        rrtsteps=10000,
        nebsteps=10,
        maxE=None,
    ):
        """
        Parameters:
        bo          The surrogate model class.
        space       (Space) The Space class defines boundaries and periodicity.
        min_points  (2d numpy array) Local minima of the surrogate model.
        precision   (float, optional) How many points would be in the returned
                    path, if it went from start to end of the shortest edge of
                    the space. Assumed to be 100.
        rrtsteps    (int, optional) Maximum number of RRT steps, assumed to be
                    1000. More equals better resolution for the algorithm and
                    longer runtime.
        nebsteps    (int, optional) Maximum number of NEB steps, assumed to be
                    1000. More doesn't necessarily improve performance, as the
                    NEB optimization should converge before this is reached.
        maxE        (float, optional) Global maximum energy of the model. If
                    not specified defaults to the highest observed energy.
        """
        self.bo = bo
        self.space = space
        self.precision = precision
        self.rrtsteps = rrtsteps
        self.nebsteps = nebsteps
        self.eps = (
            1 / precision * np.min(self.space.bounds[1, :] - self.space.bounds[0, :])
        )
        self.min_points = self.space.crds(np.atleast_2d(min_points))
        if min_points.shape[0] < 2:
            raise Exception("At least two minima needed to find paths.")

        e = self.bo.get_mu(self.min_points)[:, 0]
        e.sort()
        self.e_start = e[1]  # Second lowest local minimum
        if maxE == None:
            maxE = np.max(self.bo.get_y())

        self.maxE = maxE
        e_range = maxE - e[1]
        self.stepsize = e_range / rrtsteps

    def run_mep(self, main_output):
        main_output.mep_start(self)

        main_output.progress_msg("Running RRT:s", 1)
        self.get_connections()

        main_output.progress_msg(
            "Running NEB for " + str(len(self.connections)) + " paths.", 1
        )
        self.get_paths()

        main_output.mep_result(self)

    def get_connections(self):
        max_e = self.e_start
        connections = []
        forests = []
        for i in range(self.min_points.shape[0]):
            forests.append(Forest([Node(self.min_points[i, :], None, i)]))

        while len(forests) > 1:
            i = 0
            while i < len(forests):
                forests[i].grow(self.bo, self.eps, max_e, self.space)
                j = i + 1
                while j < len(forests):
                    end_nodes = forests[i].test_connectivity_once(
                        forests[j], self.bo, self.space, self.eps, max_e
                    )
                    if end_nodes != None:
                        connections.append(end_nodes)
                        forests[i].merge(forests[j])
                        forests.remove(forests[j])
                    else:
                        j += 1
                i += 1
            max_e += self.stepsize

        self.connections = connections

    def get_paths(self):
        # extend and optimize with NEB
        paths = []
        I = 0
        for connection in self.connections:
            I += 1
            path = Path(self.space)
            path.initFromConnection(connection)
            ns = int(self.nebsteps / 2)
            for i in range(2):
                path.reform(self.eps)
                path.crds = neb(path.crds, self.bo, self.space, ns)
            paths.append(path)
        self.paths = np.array(paths)

        # get paths from each minima to each other minima
        self.fullpaths = []
        for i in range(self.min_points.shape[0]):
            for j in range(self.min_points.shape[0]):
                if i < j:
                    crds = self.get_fullcrds(i, j)
                    energy = self.bo.get_mu(crds)
                    path = Path(self.space, crds, i, j, energy)
                    self.fullpaths.append(path)

    def get_fullcrds(self, i, j, notchecked=None):
        if i == j:
            return None
        if np.any(notchecked == None):
            notchecked = np.array(np.ones(self.paths.shape[0], dtype=bool))

        has_i = [path.mi == i or path.mj == i for path in self.paths]
        check = np.logical_and(has_i, notchecked)
        checkind = np.array(range(self.paths.shape[0]))[check]
        notchecked = np.logical_and(notchecked, np.logical_not(check))
        if checkind.shape[0] == 0:
            return None

        found = [path.mi == j or path.mj == j for path in self.paths[checkind]]
        if np.any(found):
            path = self.paths[checkind[found]][0]
            if path.mj == j:
                return path.crds
            else:
                return np.flipud(path.crds)
        else:
            for ind in checkind:
                if self.paths[ind].mi == i:
                    newi = self.paths[ind].mj
                else:
                    newi = self.paths[ind].mi
                fullcrds = self.get_fullcrds(newi, j, notchecked)
                if np.all(fullcrds != None):
                    path = self.paths[ind]
                    if self.paths[ind].mi == i:
                        return np.vstack((path.crds, fullcrds))
                    else:
                        return np.vstack((np.flipud(path.crds), fullcrds))
