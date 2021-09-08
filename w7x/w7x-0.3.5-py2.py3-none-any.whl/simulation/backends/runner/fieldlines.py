#!/usr/bin/env  # pylint: disable=too-many-ancestors
"""
    >>> import w7x.simulation.flt

    Either:
    >>> node = w7x.simulation.flt.FieldLineTracer(backend='local')

    Or:
    >>> node = w7x.simulation.flt.FieldLineTracer()
    >>> node.backend = 'local'

Timo notes #### delete ####

### QUESTIONS ###
additional shifts?
config.Defaults.Cylindricalgrid.numR/numZ equal to xfieldlines nr/nz

# TODO-1(@dboe,@timt) refactor -> what to keep
### TODO ###
 1. unittests
 2. line_diffusion
    2.1 calc velocity form temperature
 3. rst documentation


fit marker of poincare plot to number of fieldlines or make smaller in general

### NOTES ###

"""
import os
import copy
import logging
import typing
import uuid
from multiprocessing import cpu_count

import numpy as np

import rna
import tfields
import w7x
import w7x.simulation.flt

from w7x.simulation.backends.runner.base_stellopt import (
    BiotSavartArgs,
    FldArgs,
    calc_iota,
    read_fieldlines,
)


class SeedPoints:
    """
    22.12.2020
        seed points in cylinder coordinates should start at phi=0 (or same phi-plane) (for now)
        todo: why?
    """

    def __init__(self, points: tfields.Points3D, **kwargs):

        self.points = points
        self.phi_end = kwargs.pop("phiend", 6283.2)
        self.phi_end = [self.phi_end] * len(self.points)
        # r_start for mu
        self.r_start = []
        self.input_str = self._to_input_str()

    @classmethod
    def from_poincare(cls, fieldlines_output_path: str):
        # or fieldlines_output_path: rna.Path
        raise NotImplementedError

    @classmethod
    def from_points3d(cls, init_points: tfields.Points3D):
        # todo
        #   assert init_points.coord_sys == tfields.bases.CYLINDER

        return cls(points=init_points)

    @classmethod
    def from_distribution(cls, num_points, dist):
        raise NotImplementedError

    @classmethod
    def default(cls):
        points = tfields.Points3D(
            [[5.95, 0.0, 0.0], [6.50, 0.0, 0.0], [6.25, 0.0, 0.0]]
        )  # default 3 points
        return cls(points=points)

    def get_phi_end(self):
        return self.phi_end

    def _to_input_str(self):
        r_start = ""
        z_start = ""
        phi_start = ""
        phi_end = ""
        for p in self.points:
            assert p[1] == 0, f"phi has to equal 0 for xfieldlines run at point {p}"
            self.r_start.append(p[0])
            r_start += str(p[0]) + " "
            z_start += str(p[2]) + " "
            phi_start += str(p[1]) + " "
            phi_end += str(self.phi_end[0]) + " "

        input_str = "  R_START = " + r_start
        input_str += "\n  Z_START = " + z_start
        input_str += "\n  PHI_START = " + phi_start
        input_str += "\n  PHI_END = " + phi_end

        return input_str

    def __eq__(self, other):
        if not isinstance(other, SeedPoints):
            raise NotImplementedError(f"Cannot compare with {type(other)}")
        return self.input_str == other.input_str


class VmecInput:
    """
    # TODO(@timt,@dboe,@amerlo?)-2 replace with vmec-code input class -> Daniel/amerlo

    Object handling the vmec input format for xfieldlines
    """

    implemented_modes = ("biot_savart", "fld")

    def __init__(
        self,
        state,
        **kwargs,
    ):

        # todo
        self.mode = "biot_savart"
        logging.warning("only biot_savart implemented currently")

        seed = kwargs.pop("seed", None)

        if (seed is None) or (not isinstance(seed, tfields.Points3D)):
            logging.info("Using default seed")
            seed = w7x.Defaults.Poincare.seeds

        self.seed = SeedPoints.from_points3d(init_points=seed)

        self.velocity = kwargs.pop("velocity", w7x.model.PlasmaParameters.velocity)
        self.diffusion = kwargs.pop(
            "diffusion", w7x.model.PlasmaParameters.diffusion_coeff
        )

        npoinc = kwargs.pop("npoinc", 72)
        nfp = kwargs.pop("nfp", 5)

        self.grid = {
            "NR": w7x.Defaults.CylindricalGrid.numR,
            "NZ": w7x.Defaults.CylindricalGrid.numZ,
            "NPHI": w7x.Defaults.CylindricalGrid.numPhi,
            "RMIN": w7x.Defaults.CylindricalGrid.RMin,
            "RMAX": w7x.Defaults.CylindricalGrid.RMax,
            "ZMIN": w7x.Defaults.CylindricalGrid.ZMin,
            "ZMAX": w7x.Defaults.CylindricalGrid.ZMax,
            "NPOINC": int(npoinc),
            # number of toroidal points per-period for field lines output 360/5=72=npoinc one per
            # tor degree
            "PHIMIN": 0,
            "PHIMAX": 1.2566370614,  # default in w7x example inputs
        }

        self.vmec_in = {"NFP": nfp}  # periodicity

        self.currents = state.coil_set.coil_currents("Aw")

        # field line integration type
        self._integrator_type = "'LSODE'"

        self.input_str = self._to_input()

    def _to_input(self) -> str:  # , mgrid: bool = True

        assert (
            self.mode in self.implemented_modes
        ), f"{self.mode} not in {self.implemented_modes}"

        if self.mode != "biot_savart":
            raise NotImplementedError

        # https://princetonuniversity.github.io/STELLOPT/VMEC.html
        # if mgrid:
        #     self.vmec_in.update({'LFREEB': 'T'}) # if mgrid->free boundary run
        #     self.vmec_in.update({'NVACSKIP': 6}) # how often to update vac solution
        #     self.vmec_in.update({'NZETA': 180})  # number planes on which mgrid was calculated
        # self.mu = self._calc_mu()

        vmec_input = "&INDATA\n"
        for key, item in self.vmec_in.items():
            vmec_input += f"  {key} = {item}\n"

        vmec_input += "  EXTCUR = "
        for c in self.currents:
            if c:
                vmec_input += f"{str(-c)} "

        vmec_input += "\n/\n&FIELDLINES_INPUT\n"

        for key, item in self.grid.items():
            vmec_input += f"  {key} = {item}\n"

        vmec_input += f"  INT_TYPE  = {self._integrator_type}\n"

        vmec_input += self.seed.input_str
        vmec_input += "\n/"

        return vmec_input

    def _calc_mu(self) -> float:

        # mu=sqrt(D*tau*2)
        # TAU=<PHI_END*R_START>/V_PART; V_PART is the velocity of a particle
        # (assumed) and the operator <> means average

        assert self.mode == "fld", "Mu only needed for fld"

        tau = (
            np.average(
                [phi * r for phi, r in zip(self.seed.phi_end, self.seed.r_start)]
            )
            / self.velocity
        )
        mu = np.sqrt(self.diffusion * tau * 2)

        return mu

    def __eq__(self, other):
        if not isinstance(other, VmecInput):
            raise NotImplementedError(f"Cannot compare with {type(other)}")
        return self.input_str == other.input_str


class XFieldlinesSettings:
    vmec_input: VmecInput
    arguments: typing.Union[BiotSavartArgs, FldArgs]

    # TODO-2
    #  add coil file (deformed, ideal, as_built) init with w7x.core.State.CoilSet
    #   -> raise NotImplemented
    #  add vessel file (assembly) init with w7x.core.State.Machine (mm_ids)
    #   -< raise NotImplemented

    def __init__(
        self,
        state: w7x.core.State,
        arguments: typing.Union[BiotSavartArgs, FldArgs],
        **kwargs,
    ):

        self.vmec_input = VmecInput(state, **kwargs)
        self.arguments = arguments

    def __eq__(self, other):
        if not isinstance(other, XFieldlinesSettings):
            raise NotImplementedError(f"Cannot compare with {type(other)}")
        return all(
            [self.vmec_input == other.vmec_input, self.arguments == other.arguments]
        )


class XFieldlinesResult:
    # todo build getter for Points3D
    def __init__(self, result_path: str):
        self._data = read_fieldlines(result_path)

    def data(self):
        return self._data.copy()

    def iota(self):
        return calc_iota(self._data)

    def l_lines(self):
        return copy.deepcopy(self._data["L_lines"])


class XFieldlinesExec:
    """
    wraps xfiedlines run = settings(inputs) + results(outputs)
    TODO-2
        slurm script for cluster
        executable wrapped ? - mpi/srun cluster location and so on
        hashs for cached runs, delete all temporary folders on object deletion
    """

    # store arguments for different run schemas
    # 1. poincare, 2. fld, 3. poincare init for fld (lazerson branch)

    def __init__(
        self,
        state: w7x.core.State,
        executable_path: str = "~/bin/xfieldlines",
        scheduler: str = "mpirun",
    ):

        self.exec_path = rna.path.resolve(executable_path)
        self.scheduler = scheduler
        self.state = state

        # TODO-2 make dynamic and / or raise NotImplementedError
        self.coil_file_path = os.path.join(
            os.path.dirname(__file__), "data/coils/coils.w7x_mc_sc_tc_15_nfp5"
        )

    def find_lcfs(self, *args) -> tfields.Points3D:
        # todo return a single point on the lcfs

        npoinc = 1

        # use the -full option to auto calculate axis and edge maximum resolution and overwrite
        # seedpoints
        lcfs_arg = BiotSavartArgs(
            vmec="infile",
            coil=self.coil_file_path,
        )
        lcfs_arg + {"full": True}

        settings = XFieldlinesSettings(
            state=self.state, arguments=lcfs_arg, npoinc=npoinc
        )

        res_lcfs = self._run(settings)

        # res_lcfs = XFieldlinesResult(f"./cache/fieldlines_infile.h5")

        iota_out = res_lcfs.iota()
        data = res_lcfs.data()

        # rho slowly increases to lcfs, then large steps in stochastic regions
        fieldline_no = np.min(np.where(abs(np.diff(iota_out["rho"])) > 0.1))

        # lcfs, no diffusion
        nsteps = data["nsteps"]
        points = tfields.Points3D(
            np.vstack(
                (
                    data["R_lines"][0 : nsteps - 1 : npoinc, fieldline_no],
                    np.full(
                        shape=(len(range(0, nsteps - 1, npoinc)),), fill_value=0
                    ),  # phi = 0
                    data["Z_lines"][0 : data["nsteps"] - 1 : npoinc, fieldline_no],
                )
            ).T,
            coord_sys=tfields.bases.CYLINDER,
        )  # r, phi, z
        return points

    def trace_surface(self, lcfs_point, n_start, *args, **kwargs) -> tfields.Points3D:
        # todo dont't take equidistant lcfs_point n_start times, lcfs_point is already a surface
        # todo trace surface and save every n metres/phis

        indices = np.round(np.linspace(0, len(lcfs_point) - 1, n_start)).astype(int)
        lcfs_point_ret = lcfs_point[indices]
        return lcfs_point_ret

    def line_diffusion(self, start_points):
        # todo how to properly save the result using npoinc?

        npoinc = 72  # for now

        fld_arg = FldArgs(
            vmec="infile",
            coil="/home/IPP-HGW/timt/xfieldlines/W7X_FILES/coils/coils.w7x_mc_sc_tc_15_nfp5",
            vessel="/home/IPP-HGW/timt/xfieldlines/W7X_FILES/vessel/w7x_full_highres.dat",
        )

        settings = XFieldlinesSettings(
            state=self.state, arguments=fld_arg, npoinc=npoinc, seed=start_points
        )

        res_fld = self._run(settings)

        print(res_fld)

    def poincare_in_phi_plane(
        self, phi_list_rad: typing.List[float], seed: tfields.Points3D = None
    ) -> typing.List[tfields.Points3D]:

        # todo implement more fine-grained npoinc, what to do about irrational phi?

        phi_list_grad = [phi * 180 / np.pi for phi in phi_list_rad]

        if not all(phi % 1 == 0 for phi in phi_list_grad):
            raise NotImplementedError("Only integer degrees for now")

        phi_list_grad = [int(phi) for phi in phi_list_grad]

        # TODO-1(@timt): comment reason for the below
        npoinc = 72 / np.gcd.reduce(phi_list_grad)
        if npoinc % 1 != 0:
            npoinc = 72
        npoinc = int(npoinc)

        res = self._run(
            XFieldlinesSettings(
                state=self.state,
                arguments=BiotSavartArgs(
                    vmec="infile",
                    coil=self.coil_file_path,
                ),
                seed=seed,
                npoinc=npoinc,
                # nfp = nfp
            )
        )

        data = res.data()
        nsteps = data["nsteps"]

        surfaces = []
        for phi in phi_list_grad:
            npoint = phi * npoinc / 72
            assert npoint % 1 == 0
            npoint = int(npoint)

            surf = tfields.Points3D(
                np.vstack(
                    (
                        data["R_lines"][npoint : nsteps - 1 : npoinc, :].flatten(),
                        np.full(
                            shape=(len(range(npoint, nsteps - 1, npoinc)))
                            * data["nlines"],
                            fill_value=phi,
                        ),
                        data["Z_lines"][npoint : nsteps - 1 : npoinc, :].flatten(),
                    )
                ).T,
                coord_sys=tfields.bases.CYLINDER,
            )

            surfaces.append(surf)
        return surfaces

    def _run(
        self, settings: XFieldlinesSettings, no_cpu: typing.Optional[int] = None
    ) -> XFieldlinesResult:

        if no_cpu is None:
            logging.info(f"Using maximal available cpu count: {cpu_count()}")
            no_cpu = cpu_count()

        # NOTE: Cacheing?
        #   -> maybe dont delete?
        #       -> new option: cashe?
        #       -> requires search function
        path = rna.path.resolve(
            w7x.config.get_option("cache", "path", path=True),
            "fieldlines",
            str(uuid.uuid4()),
        )
        logging.debug("Working directory: %s", path)
        rna.path.mkdir(path, is_dir=True)
        with rna.path.cd_tmp(path):
            # make this less boilerplate?
            vmec_infile_name = settings.arguments.args["vmec"].path

            # be in folder of input.infile, all others paths absolute
            with open(f"input.{vmec_infile_name}", "a") as out:
                out.write(settings.vmec_input.input_str + "\n")

            call = (
                f"{self.scheduler} -np {no_cpu} "
                f"{self.exec_path} {settings.arguments}"
            )
            rna.process.execute(call, level=logging.DEBUG)

            result = XFieldlinesResult(f"fieldlines_{vmec_infile_name}.h5")
        rna.path.rm(path, recursive=True)

        return result

    def conn_length(self, seed: tfields.Points3D = None, **kwargs):
        # https://github.com/lazersos/matlabVMEC/blob/master/FIELDLINES/plot_fieldlines_conn_length.m

        diffusion = kwargs.pop("diffusion", None)

        vmec_infile = "infile"
        coil_file = "/home/thuni/ipp/prog/datastore/coils.w7x_mc_sc_tc_15"

        if diffusion is None:
            argument = BiotSavartArgs(
                vmec=vmec_infile,
                coil=coil_file,
            )
        else:
            # argument = FldArgs(
            #         vmec=vmec_infile,
            #         coil=coil_file
            # )
            raise NotImplementedError

        logging.debug("Running forward flt")
        res1 = self._run(
            XFieldlinesSettings(
                state=self.state,
                arguments=argument,
                seed=seed,
            )
        )
        lines = res1.l_lines()

        # this can be made more beautiful ( argument.add_arg('reverse') )
        argument + {"reverse": True}

        logging.debug("Running backward flt")
        res2 = self._run(
            XFieldlinesSettings(
                state=self.state,
                arguments=argument,
                seed=seed,
            )
        )
        lines.extend(res2.l_lines())

        # TODO-2(@timt) map to mm_ids
        connection_lengths = np.array(lines)

        return connection_lengths


class FieldLineTracerStelloptBackend(w7x.simulation.fieldlines.FieldLineTracerBackend):
    """
    # TODO-2(@timt)
        xfieldlines .h5 file to simulation/fieldlines.py/FieldLinesResult
        vessel wrapper
        coils wrapper - both wrapper init by state and go to input file
        more run options using sams knowledge
        this class could be replaced by XFieldlinesExec or used to pre-check args
    """

    _executable = None  # TODO-2 where to put this

    @property
    def executable(self):
        if self._executable is None:
            self._executable = XFieldlinesExec(state=self.state)
        return self._executable

    @w7x.simulation.fieldlines.FieldLinesBackend.state.setter
    def state(self, state):
        super().state.fset(self, state)

    def find_lcfs(self, step=0.1) -> tfields.Points3D:  # pylint:disable=unused-argument
        """
        Returns:
            The Id of the fieldline traced which is closest to the lcfs

        Examples:
            >>> from w7x.simulation import FieldLines
            >>> run = FieldLines()
            >>> run.STRATEGY_DEFAULT='local'
            >>> lcfs_point = run.find_lcfs(0.1)  # Long lasting -> large step size for demo only.
            >>> assert lcfs_point[0, 0] > 6.2
            >>> assert lcfs_point[0, 0] < 6.21

        """
        # lcfs -> poincare run, then what? (Fit Fourier coeffs ?)
        # todo step not needed as equation of motion is going in phi, not t
        return self.executable.find_lcfs()

    def trace_diffusion(self, start_points):
        """
        Args:
            start_points(Points3D):
                Points3D: full start point set that should be traced
            diffusion (float): perp. diffusion coefficient
        Returns:
            tuple:
                ConnectionLength:
                ComponentLoad:
                Points3D: start points lying on lcfs
        Examples:
            >>> import tfields
            >>> import w7x
            >>> from w7x.simulation import FieldLines

            Triangle approximating the bean plane
            >>> mesh = tfields.Mesh3D([[5.4,0,-1], [5.4,0,1], [6.5,0,0]],
            ...                       faces=[[0,1,2]], coord_sys='cylinder')

            Machine constitued from bean plane triangle and divertor
            >>> assembly = w7x.model.Assembly(
            ...     groups=[w7x.model.AssemblyGroup(
            ...         components=[w7x.model.Component(id=165),
            ...                     w7x.model.Component(mesh=mesh)
            ...     ])
            ... ])
            >>> node = FieldLines(assembly)

            Initial point starting very close to the triangle
            >>> initial_points = tfields.Points3D([[6.0,0.0001,0]], coord_sys='cylinder')
            >>> conn_len, comp_load, start_points = node.trace_diffusion(initial_points)
            >>> assert initial_points.equal(start_points,atol=1e-9)

            As expected, the triangle was hit only
            >>> conn_len.parts
            [0, 0]

            The mm_id 1000 is added automatically
            >>> conn_len.mm_ids
            [1000, 165]
        """
        # calc mu
        # run
        # pass back terminating comps, faces, areas and connection lengths
        raise NotImplementedError

        # n_start = None
        # launch_points_path = None
        # if type(start_points) is int:
        #     n_start = start_points
        #     start_points = None
        # elif type(start_points) is str:
        #     launch_points_path = start_points
        #     start_points = None
        # elif isinstance(start_points, tfields.Points3D):
        #     n_start = start_points.shape[0]
        #     if not isinstance(start_points, Points3D):
        #         start_points = Points3D(start_points)
        # # elif isinstance(start_points, StelloptPoincare):
        # #     start_points = None

        # return result

    def poincare(
        self,
        *args,
        **kwargs,
    ) -> typing.List[tfields.Points3D]:
        return self.executable.poincare_in_phi_plane(*args, **kwargs)

    def trace_surface(
        self, lcfs_point: tfields.Points3D, n_start: int, *args, **kwargs
    ) -> tfields.Points3D:

        return self.executable.trace_surface(lcfs_point, n_start, *args, **kwargs)

    def trace(self, start_points: tfields.Points3D) -> tfields.Points3D:
        raise NotImplementedError

    def connection_length(
        self,
        *args,
        **kwargs,
    ):
        """
        Args:
            points: Points3D
            **kwargs:
                limit (float): lenght limit of line tracing
                diffusion (field_line_server.type.LineDiffusion()): add diffusion
                    to the tracing

        Returns:
            ConnectionLength

        """
        return self.executable.conn_length(*args, **kwargs)


if __name__ == "__main__":

    def test_poincare():
        import matplotlib.pyplot as plt
        import rna
        from w7x.plotting.poincare import plot_poincare_surfaces

        flt_s = w7x.simulation.fieldlines.FieldLines()
        flt_s.backend = "local"

        phi_list = [0, 18, 36]
        # todo set title, set markersize
        surfaces = flt_s.poincare(phi_list_rad=[a * np.pi / 180 for a in phi_list])

        fig = plt.figure()
        axes = fig.add_subplot()
        axes.grid(color="lightgrey")
        axes.set_title("phi")
        plot_poincare_surfaces(
            surfaces, axes=axes, rMin=5.7, rMax=6.15, zMin=-0.5, zMax=0.5
        )
        fig.show()

        rna.plotting.save("poincare phi", "pdf")

    def test_conn_len():
        flt_s = w7x.simulation.fieldlines.FieldLineTracer()
        # flt_s = FieldLineTracerStelloptBackend()
        flt_s.backend = "local"
        conn_len = flt_s.connection_length()
        return conn_len

    def test_plot_lcfs():
        import matplotlib.pyplot as plt
        import rna
        from w7x.plotting.poincare import plot_poincare_surfaces

        flt_s = w7x.simulation.FieldLineTracer()
        flt_s.backend = "local"
        abc = flt_s.find_lcfs()
        surf = flt_s.trace_surface(abc, 100)

        fig = plt.figure()
        axes = fig.add_subplot()
        axes.grid(color="lightgrey")
        axes.set_title("phi")
        plot_poincare_surfaces([surf], axes=axes, rMin=5, rMax=7, zMin=-1.5, zMax=1.5)
        fig.show()
        rna.plotting.save("poincare lcfs phi", "pdf")

    def test_fld():
        flt_s = w7x.simulation.FieldLineTracer()
        flt_s.backend = "local"
        abc = flt_s.find_lcfs()
        surf = flt_s.trace_surface(abc, 300)  # NOQA

    # test_plot_lcfs()
    test_poincare()
