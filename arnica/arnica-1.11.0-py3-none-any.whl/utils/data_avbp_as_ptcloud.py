""" module loading avbp h5py into numpy arrays,
limited to point cloud (connectivity sucks, mark my word, really) """
import warnings
import h5py
import numpy as np
from arnica.utils.vector_actions import renormalize



class AVBPAsPointCloud:
    """ class handling mesh and solutions as point cloud
    *no connectivity asked* """

    warnings.warn("This tool is deprecated, see the mesh_utils.py tools in pyavbp",
                  DeprecationWarning)

    def __init__(self, meshfile):
        """ startup class"""
        self.mesh = {}
        self.solavg = {}
        self.origins = {}
        self.origins["meshfile"] = meshfile
        self.origins["solavgfile"] = None

    # @timing
    def load_mesh_bulk(self):
        """ load the bulk of the mesh, withound the boundaries """

        with h5py.File(self.origins["meshfile"], "r") as fin:
            self.mesh["bulk"] = {}
            self.mesh["bulk"]["xyz"] = np.stack(
                (
                    fin["/Coordinates/x"][()],
                    fin["/Coordinates/y"][()],
                    fin["/Coordinates/z"][()],
                ),
                axis=1,
            )

    # @timing
    def load_mesh_bnd(self, patchlist=None):
        #pylint: disable=too-many-locals
        """ load only the boundaries. Load all patches,
        unless a subset of patch is provided with opt keyword patchlist """

        with h5py.File(self.origins["meshfile"], "r") as fin:
            self.mesh["Patches"] = {}

            patches_readable = fin["/Boundary/PatchLabels"][()]
            bnode_normal = fin["/Boundary/bnode->normal"][()]
            bnode_lidx = fin["/Boundary/bnode_lidx"][()].astype(int)
            bnode_gnode = fin["/Boundary/bnode->node"][()].astype(int)

            patches_readable = [pname.decode('UTF-8').strip() for pname in
                                patches_readable if pname is not None]

            if patchlist is None:
                patchlist = patches_readable
            else:
                for patch in patchlist:
                    if patch not in patches_readable:
                        raise IOError(
                            "No patch "
                            + patch
                            + " among :\n"
                            + "\n".join(patches_readable)
                        )

            for patchlabel in patchlist:
                self.mesh["Patches"][patchlabel] = {}

            for i, patchlabel in enumerate(patches_readable):
                if patchlabel in patchlist:
                    self.mesh["Patches"][patchlabel]["xyz"] = np.stack(
                        (
                            fin["/Patch/" + str(i + 1) + "/Coordinates/x"][()],
                            fin["/Patch/" + str(i + 1) + "/Coordinates/y"][()],
                            fin["/Patch/" + str(i + 1) + "/Coordinates/z"][()],
                        ),
                        axis=1,
                    )

                    shape = self.mesh["Patches"][patchlabel]["xyz"].shape
                    start = 0
                    end = int(3 * bnode_lidx[i])
                    if i >= 1:
                        start = int(3 * bnode_lidx[i - 1])
                    part_bnode_normal = bnode_normal[start:end].reshape(shape)
                    self.mesh["Patches"][patchlabel]["surf"] = np.linalg.norm(
                        part_bnode_normal, axis=-1
                    )
                    self.mesh["Patches"][patchlabel]["normal"] = renormalize(
                        part_bnode_normal
                    )
                    gnodes = (bnode_gnode[int(start / 3): int(end / 3)])
                    self.mesh["Patches"][patchlabel]["gnodes"] = gnodes

    # @timing
    def load_avgsol(self, solavgfile, *extra_vars):
        """ load a solution
        AVBP avg for the moment"""
        self.origins["solavgfile"] = solavgfile
        with h5py.File(self.origins["solavgfile"], "r") as fin:
            for var in ["T", "rho", "u", "v", "w"] + list(extra_vars):
                self.solavg[var] = fin["/Average/" + var][()]

    def get_skinpts(self, listpatch):
        """ return a dict of numpy array [x, y ,z]
        coordinates of a subset of patches """

        skin = np.concatenate(
            [self.mesh["Patches"][patchlabel]["xyz"] for patchlabel in
             listpatch])
        return skin
