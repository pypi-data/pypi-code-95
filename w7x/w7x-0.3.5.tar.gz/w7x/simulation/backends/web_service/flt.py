#!/usr/bin/env  # pylint: disable=too-many-ancestors
"""
Field line tracer specifics
author: daniel.boeckenhoff@ipp.mpg.de
"""
import typing
import logging
import os
import subprocess
import pathlib
import numpy as np

import rna
import tfields
import w7x
import w7x.simulation.flt
from w7x.simulation.backends.web_service import (
    get_server,
    run_service,
    OsaType,
    to_osa_type,
    to_tfields_type,
)
from w7x.simulation.backends.web_service.components import MeshedModel


WS_SERVER = w7x.config.get_option("flt.web_service", "server")
LOGGER = logging.getLogger(__name__)


class Base(OsaType):
    """
    Field Line Server Base
    """

    ws_server = WS_SERVER


class CylindricalGrid(Base):
    """
    Order of grid in the ws is
    for phi
        for r
            for z
    i.e. iter_order = [1, 0, 2]
    """

    @classmethod
    def from_base_vectors(
        cls, base_vectors: typing.Tuple[typing.Tuple[float, float, complex]]
    ):
        """
        Args:
            base_vectors: orthogonal base_vectors. Each determined by tuple (min, max, 0 + num * j)
                see :fun:`tfields.lib.grid.ensure_complex`
        """
        minima = []
        maxima = []
        nums = []
        for base_vector in base_vectors:
            minima.append(base_vector[0])
            maxima.append(base_vector[1])
            num = base_vector[2]
            if isinstance(num, complex):
                if num.real != 0:
                    raise ValueError("Base vector spacing number must be complex only")
                num = int(num.imag)
            else:
                raise ValueError("Base vector spacing number must be complex")
            nums.append(int(num))
        # if minima[1] == 0:
        #     # phi min
        #     minima[1] = None
        # if np.isclose(maxima[1], 2 * np.pi):
        #     maxima[1] = None
        return cls(
            RMin=minima[0],
            # PhiMin=minima[1],  PhiMin = None always. None means: figure out period from nfp
            ZMin=minima[2],
            RMax=maxima[0],
            # PhiMax=maxima[1],  PhiMax = Non always. None means: figure out period from nfp
            ZMax=maxima[2],
            numR=nums[0],
            numPhi=nums[1],
            numZ=nums[2],
        )

    prop_defaults = dict(
        RMin=4.05,
        RMax=6.75,
        ZMin=-1.35,
        ZMax=1.35,
        numR=181,
        numZ=181,
        #: phi is complicated. Periodicity of the grid is normalized to 0 ... 2*np.pi
        #   If you want to upsample the grid from nfp=5 to nfp=1 with originally numPhi=96,
        #   you need to use a new numPhi = 96 * 5 + 1. @mendler and @geiger do not know why '+ 1'.
        #   TODO(@boz) why + 1?
        numPhi=96,
        PhiMin=None,  # i.e. 0.0
        PhiMax=None,  # i.e. 2*π
    )


class CartesianGrid(Base):
    """
    Order of grid in the ws is
    for phi
        for r
            for z
    """

    prop_defaults = dict(
        numX=500,
        numY=500,
        numZ=100,
        ZMin=-1.5,
        ZMax=1.5,
        XMin=-7,
        XMax=7,
        YMin=-7,
        YMax=7,
    )


# pylint:disable=line-too-long
class Grid(Base):
    """
    see http://webservices.ipp-hgw.mpg.de/docs/fieldlinetracer.html#Grid
    Examples:
        >>> from w7x.simulation.backends.web_service.flt import CylindricalGrid, Grid
        >>> cyl = CylindricalGrid(numPhi=49)
        >>> afsFilePath = "/fieldline/w7x/field_mfbe181x181x96.w7x.1000_1000_1000_1000_+0000_+0000.dboe_01.v_00_pres_00_it_12.dat"  # noqa
        >>> grid = Grid(cylindrical=cyl, afsFileName=afsFilePath)
        >>> grid.as_input()  # noqa
        (Grid){
            cylindrical = (CylindricalGrid){
                              RMin = 4.05
                              RMax = 6.75
                              ZMin = -1.35
                              ZMax = 1.35
                              numR = 181
                              numZ = 181
                              PhiMin = None (float)
                              PhiMax = None (float)
                              numPhi = 49
                          }
            hybrid = None (CylindricalGrid)
            afsFileName = /fieldline/w7x/field_mfbe181x181x96.w7x.1000_1000_1000_1000_+0000_+0000.dboe_01.v_00_pres_00_it_12.dat
            gridField = None (Points3D)
            fieldSymmetry = 5
        }

    """

    prop_defaults = {
        "cylindrical": None,
        "hybrid": None,
        "afsFileName": None,
        "gridField": None,
        "fieldSymmetry": 5,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Do not use the hybrid unless you know what you are doing
        if self.hybrid is not None:  # pylint: disable=no-member
            raise AttributeError("You should not use the hybrid grid.")
        if self.cylindrical is None:  # pylint: disable=access-member-before-definition
            self.cylindrical = CylindricalGrid()


class Machine(Base):
    """
    Object to closely lie above web service Machine object
    Examples:
        >>> from w7x.simulation.backends.web_service.flt import Machine
        >>> a = Machine.from_state(
        ...     w7x.State(w7x.model.Assembly(components=[w7x.config.AssemblyGroups.Divertor()]))
        ... )
        >>> a.as_input()
        (Machine){
            meshedModels[] = None (MeshedModel)
            meshedModelsIds[] = [
                                 165,
                                 166,
                                 167,
                                 168,
                                 169
                                 ]
            assemblyIds[] = None (int)
            grid = (CartesianGrid){
                       XMin = -7
                       XMax = 7
                       YMin = -7
                       YMax = 7
                       ZMin = -1.5
                       ZMax = 1.5
                       numX = 500
                       numY = 500
                       numZ = 100
                   }
        }

    """

    prop_defaults = {
        "meshedModels": None,
        "meshedModelsIds": None,
        "assemblyIds": None,
        "grid": CartesianGrid(),
    }
    ws_class_args = [1]

    @classmethod
    def from_state(cls, state):
        """
        Factory method for building this class from a state
        """
        components = state.assembly.get_components(flat=True)
        return cls(
            meshedModelsIds=[c.id for c in components if c.id is not None] or None,
            meshedModels=[
                MeshedModel(c.mesh)
                for c in components
                if c.id is None and c.mesh is not None
            ]
            or None,
        )


# pylint:disable=line-too-long
class MagneticConfig(Base):
    """
    Object to closely lie above web service MagneticConfig object
    Examples:
        >>> import numpy as np
        >>> import w7x
        >>> from w7x.simulation.backends.web_service.flt import MagneticConfig
        >>> path = w7x.config.get_option("extender.test", "example_dat")

        Example dat has an uncommon grid
        >>> base_vectors = (
        ...     (3.81, 6.87, 173j),
        ...     (0, 2*np.pi / 5, 280j),
        ...     (-1.45, 1.45, 170j),
        ... )
        >>> mgrid = w7x.model.MGrid(
        ...     path=path, base_vectors=base_vectors, iter_order=[1, 0, 2],
        ... )
        >>> state = mgrid.to_state()

        >>> config = MagneticConfig.from_state(state)
        >>> config.as_input()  # doctest: +ELLIPSIS
        (MagneticConfig){
            coils[] = None (PolygonFilament)
            coilsCurrents[] = None (float)
            coilsIds[] = None (int)
            coilsIdsCurrents[] = None (float)
            configIds[] = None (int)
            grid = (Grid){
                       cylindrical = (CylindricalGrid){
                                         RMin = 3.81
                                         RMax = 6.87
                                         ZMin = -1.45
                                         ZMax = 1.45
                                         numR = 173
                                         numZ = 170
                                         PhiMin = None (float)
                                         PhiMax = None (float)
                                         numPhi = 280
                                     }
                       hybrid = None (CylindricalGrid)
                       afsFileName = /fieldline/w7x/field_dboe_id_1000_1000_1000_1000_+0000_+0000_v_00_pres_00_it_12.dat
                       gridField = None (Points3D)
                       fieldSymmetry = 5
                   }
            inverseField = None (bool)
        }

    """

    prop_defaults = {
        "coils": None,
        "coilsCurrents": None,
        "coilsIds": None,
        "coilsIdsCurrents": None,
        "configIds": None,
        "grid": None,
        "inverseField": None,
    }

    @classmethod
    def from_state(cls, state):
        """
        Factory method for building this class from a state
        """
        if state.has(w7x.model.Equilibrium):
            grid_file = state.equilibrium.get_ref("field")
            if grid_file is not None:
                LOGGER.debug("Grid file found. Passing the file via CIFS")
                # use the linked grid file
                cyl = CylindricalGrid.from_base_vectors(grid_file.base_vectors)
                grid = Grid(
                    cylindrical=cyl,
                )
                return cls.from_mgrid_file(
                    grid_file.path,
                    grid=grid,
                )
            elif state.equilibrium.field is not None:
                LOGGER.info(
                    "Uploading the field points explicitly via the GridField attribute."
                    " If you use the same field over and over again, think of saving as .datc"
                )
                # upload the field as is
                grid = state.equilibrium.field
                assert isinstance(grid, tfields.TensorGrid)
                if not grid.base_vectors.coord_sys == tfields.bases.CYLINDER:
                    raise ValueError(
                        "I could do the transform but heasitate because non-cylinder bases are"
                        " uncommon and usually a faulty usage."
                    )
                assert grid.rank == 1
                cyl = CylindricalGrid.from_base_vectors(
                    state.equilibrium.field.base_num_tuples()
                )
                grid.transform_field(tfields.bases.PHYSICAL_CYLINDER)
                grid_field = grid.fields[0]
                assert grid_field.dim == 3
                # Grid field requires Bphi, BR, Bz
                grid_field[:, [1, 0]] = grid_field[:, [0, 1]]
                grid = Grid(
                    cylindrical=cyl,
                    gridField=to_osa_type(grid_field, ws_server=WS_SERVER),
                )
                return cls(
                    grid=grid,
                )
            raise NotImplementedError(f"{state.equilibrium} without grid field")

        # no grid field provided. Build vacuum field from Biot-Savart
        LOGGER.debug(
            "No grid field provided. Building the vacuum field from Biot-Savart."
        )
        grid = Grid()  # grid=None will calculate for ever but not fail
        coil_ids = [coil.id for coil in state.coil_set.get_coils(flat=True)]
        coil_ids_currents_rw = state.coil_set.get_currents(unit="Aw", flat=True)
        return cls(
            coilsIds=coil_ids,
            coilsIdsCurrents=coil_ids_currents_rw,
            grid=grid,
        )

    @classmethod
    def from_afs_file(cls, file_path, **kwargs):
        """
        set AFS BField file
        Args:
            file_path (str): afs file path
            **kwargs: forwarded to constructor of cls

        """
        if "grid" not in kwargs:
            raise AttributeError("Please specify a grid.")
        # create Grid with afsFileName and hybrid grid if existing.
        kwargs["grid"] = kwargs.pop("grid", Grid())
        # check that file is afs file
        if file_path.startswith(
            w7x.config.get_option("flt.web_service", "network_share")
        ):
            file_path = file_path.lstrip(
                w7x.config.get_option("flt.web_service", "network_share")
            )
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        if not file_path.startswith(
            "/"
            + w7x.config.get_option(
                "flt.web_service", "network_share_relative_path"
            ).split("/")[0]
        ):
            raise TypeError("File must be shared on network drive.")
        kwargs["grid"].afsFileName = file_path

        return cls(**kwargs)

    @classmethod
    def from_mgrid_file(
        cls,
        file_path,
        network_share=w7x.config.get_option("flt.web_service", "network_share"),
        network_share_mount=w7x.config.get_option(
            "flt.web_service", "network_share_mount"
        ),
        network_share_relative_path=w7x.config.get_option(
            "flt.web_service", "network_share_relative_path"
        ),
        **kwargs,
    ):
        """
        Copy file to afs and return the instance with afsFile

        Args:
            file_path: file path to the local file or network share
            network_share: network share server domain
            network_share_mount: local mount point of the network share
            network_share_relative_path: base directory of all files relative to network_share
            **kwargs: see :meth:`from_afs_file` and :meth:`__init__`

        Examples:
            >>> import w7x
            >>> from w7x.simulation.backends.web_service.flt import CylindricalGrid, Grid, MagneticConfig
            >>> magnetic_grid_file_name=w7x.config.get_option("extender.test", "example_dat")
            >>> cyl = CylindricalGrid(numR=60, numPhi=101, numZ=10)
            >>> grid = Grid(cylindrical=cyl)
            >>> m = MagneticConfig.from_mgrid_file(magnetic_grid_file_name, grid=grid)

        """
        file_path = rna.path.resolve(file_path)

        if file_path.startswith(network_share):
            LOGGER.info("Passing network share path to 'from_mgrid_file'.")
            network_file_path = file_path
            return cls.from_afs_file(network_file_path, **kwargs)
        if (
            pathlib.Path("/", network_share_relative_path).parts[1]
            == pathlib.Path("/", file_path).parts[1]
        ):
            # file_path starts with 'fieldlines', so relative path is given
            network_file_path = rna.path.resolve(network_share, file_path)
            return cls.from_afs_file(network_file_path, **kwargs)
        network_file_path = rna.path.resolve(
            network_share,
            network_share_relative_path,
            os.path.basename(file_path),
        )

        # locally mounted?
        local_mount_file_path = ""
        if os.name == "nt":
            local_mount_file_path = network_file_path
        if os.name == "posix":
            if os.path.exists(rna.path.resolve(network_share_mount)):
                local_mount_file_path = rna.path.resolve(
                    network_share_mount,
                    network_share_relative_path,
                    os.path.basename(file_path),
                )

        # copy if not existing
        if os.path.exists(local_mount_file_path):
            # If file is on nas you have nothing to do
            LOGGER.info(
                "File %s is already existing. It is mounted as %s. I will not copy.",
                network_file_path,
                local_mount_file_path,
            )
        elif local_mount_file_path:
            # nas is locally mounted but the file does not exist. Copy file to nas
            LOGGER.info("Copy %s to %s", file_path, local_mount_file_path)
            rna.path.cp(file_path, local_mount_file_path)
        elif os.name == "posix":
            # Copy file to nas with smbclient.
            # Inspired by smbclient python package

            LOGGER.info("Copy %s to %s", file_path, network_file_path)
            remote_path = os.path.join(
                network_share_relative_path, os.path.basename(file_path)
            )
            remote_path = remote_path.replace("/", "\\")  # nt compatible
            smbclient_cmd = [
                "smbclient",
                network_share.rstrip("/"),
                "-k",  # kerberos!
            ]
            smbclient_cmd = [x.encode("utf8") for x in smbclient_cmd]
            command_list = ["put"]
            command_list.extend('"%s"' % arg for arg in [file_path, remote_path])
            command = " ".join(command_list)
            cmd = smbclient_cmd + [b"-c", command.encode("utf8")]

            # retry because sambaclient is buggy
            n_tries = 10
            attempts = 0
            while attempts < n_tries:
                pipe = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                result = pipe.communicate()[0].rstrip().decode("utf8")
                if pipe.returncode != 0:
                    LOGGER.warning(
                        "Attempting to copy by smbclient failed. Number of attemps: %s (cmd: %s)",
                        attempts,
                        (b" ".join(cmd).decode("utf8")),
                    )
                    attempts += 1
                else:
                    break

            else:
                raise OSError(
                    "Error on %r: %r" % (b" ".join(cmd).decode("utf8"), result)
                )

        return cls.from_afs_file(network_file_path, **kwargs)


def pwi_from_res(res, start_points, components, inverse_field) -> w7x.model.Pwi:
    """
    Used to transform web service results of type conenction_length and load to Pwi model
    """
    return_loads = hasattr(res, "loads")
    pwi = w7x.model.Pwi(origin_points=start_points)
    if res is None:
        pci = w7x.model.PlasmaComponentInteraction(
            component_index=None,
            inverse_field=inverse_field,
            origin_point_indices=list(range(len(start_points))),
        )
        pwi.add(pci)
        return pwi

    parts = set(c.part for c in res.connection)
    if None in parts:
        parts.discard(None)
        parts = [None] + sorted(parts)
    else:
        parts = sorted(parts)

    for i, con in enumerate(res.connection):
        # tmp_index refers to originating start point
        con.tmp_index = i

    for part in parts:
        component_index = part
        clrs = [c for c in res.connection if c.part == part]
        origin_point_indices = [c.tmp_index for c in clrs]
        hit_points = tfields.Points3D([[c.x, c.y, c.z] for c in clrs])

        if return_loads and res.loads is not None:
            for x in res.loads.components:
                if x.id == part:
                    load = x.elements
                    break
            else:
                load = []
            n_hits = {e.id: e.events for e in load}
            areas = {e.id: e.area for e in load}
        else:
            n_hits = None
            areas = None

        if component_index is not None:
            connection_lengths = tfields.Tensors([c.length for c in clrs])
            hit_points_faces = tfields.Tensors([c.element for c in clrs], dtype=int)
        else:
            connection_lengths = tfields.Tensors([np.inf] * len(clrs))
            hit_points_faces = None

        pci = w7x.model.PlasmaComponentInteraction(
            component_index=component_index,
            inverse_field=inverse_field,
            origin_point_indices=origin_point_indices,
            hit_points=hit_points,
            hit_points_faces=hit_points_faces,
            connection_lengths=connection_lengths,
            n_hits=n_hits,
            areas=areas,
        )
        pwi.add(pci)

    assert len(pwi.origin_points) == sum(
        [len(pci.origin_point_indices) for pci in pwi.components]
    )

    return pwi


@w7x.node
def magnetic_config_from_state(state):
    """
    Wrapper for dask.delayed config from state
    """
    config = to_osa_type(MagneticConfig.from_state(state))
    return config


class FieldLineTracerWebServiceBackend(w7x.simulation.flt.FieldLineTracerBackend):
    """
    Backend for the field line tracer from the web service
    """

    @staticmethod
    def _trace_poincare(state, **kwargs):
        phi = kwargs.pop("phi")
        try:
            iter(phi)
        except TypeError:
            phi_list_rad = [phi]
        else:
            phi_list_rad = phi
        seeds = kwargs.pop("seeds")
        n_points = kwargs.pop("n_points")
        errors = kwargs.pop("errors", [])
        step = kwargs.pop("step")

        assert n_points > 0, "n_points must be greater than 0"

        field_line_server = get_server(WS_SERVER)

        config = magnetic_config_from_state(state)

        # Poincare Task
        task = field_line_server.types.Task()
        # parameter controling the accurancy of the calculation.
        task.step = step
        task.poincare = field_line_server.types.PoincareInPhiPlane()
        task.poincare.numPoints = n_points
        # list of phi in radians or just one phi.
        task.poincare.phi0 = phi_list_rad

        @w7x.node
        def trace_poincare(seed_point, config, task, errors):
            res = run_service(
                field_line_server.service.trace,
                to_osa_type(seed_point, ws_server=WS_SERVER),
                config,
                task,
                errors=errors,
            )

            if res is None:
                LOGGER.warning("Seed point %s fail failed.", seed_point)
                return None
            surface_points = []
            for surf in res.surfs:
                # len(res.surfs) corresponds to number of phi given
                points = to_tfields_type(surf.points)
                points.transform(tfields.bases.CYLINDER)
                # phi is correct only with rounding precision before. This way
                # it is perfectly correct
                points[:, 1].fill(surf.phi0)
                surface_points.append(points)
            return tfields.Points3D.merged(*surface_points)

        poincare_flux_surfaces = []
        LOGGER.info("Running through Seeds. Tracing each seed for all given phi.")
        for i_seed in range(len(seeds)):
            seed_point = seeds[i_seed : i_seed + 1]
            poincare_flux_surfaces.append(
                trace_poincare(seed_point, config, task, errors)
            )

        return poincare_flux_surfaces

    @staticmethod
    def _magnetic_characteristics(state, **kwargs):
        points = kwargs.pop("points")
        step = kwargs.pop("step")
        return_type = kwargs.pop("return_type")

        field_line_server = get_server(WS_SERVER)
        # process input points
        points = tfields.Points3D(points)
        points.transform(tfields.bases.CARTESIAN)

        config = to_osa_type(MagneticConfig.from_state(state))

        # define task
        task = field_line_server.types.Task()
        task.step = step
        task.characteristics = field_line_server.types.MagneticCharacteristics()  # NOQA
        task.characteristics.axisSettings = (
            field_line_server.types.AxisSettings()
        )  # NOQA

        # run web service
        LOGGER.info("Retrieving MagneticCharacteristics with the points given.")
        # the None after 'task' can be machine boundary.
        result = run_service(
            field_line_server.service.trace,
            to_osa_type(points, ws_server=WS_SERVER),
            config,
            task,
            None,
            None,
        )

        if result is None:
            return None
        if return_type is list:
            return result.characteristics
        if issubclass(return_type, tfields.TensorFields):
            fields = [[], [], [], [], [], []]
            for x in result.characteristics:
                fields[0].append(x.iota)
                fields[1].append(x.diota)
                fields[2].append(x.reff)
                fields[3].append(x.dreff)
                fields[4].append(x.phi0)
                fields[5].append(x.theta0)
            return return_type(points, *fields)

    @staticmethod
    def _find_axis_at_phi(state, **kwargs):
        phi = kwargs.pop("phi", 0)
        step = kwargs.pop("step", 1e-2)

        config = to_osa_type(MagneticConfig.from_state(state))

        field_line_server = get_server(WS_SERVER)
        settings = field_line_server.types.AxisSettings(1)
        LOGGER.info("Finding axis at phi.")
        result = run_service(
            field_line_server.service.findAxisAtPhi,
            phi,
            step,
            config,
            settings,
        )
        return tfields.Points3D(result.points, coord_sys=tfields.bases.CARTESIAN)

    @staticmethod
    def _find_lcfs(state, **kwargs) -> tfields.Points3D:
        step = kwargs.pop("step")
        settings = None
        max_time = None

        field_line_server = get_server(WS_SERVER)
        if settings is None:
            settings = field_line_server.types.LCFSSettings(1)

        LOGGER.info("Retrieving Point on Last closed flux surface")

        config = to_osa_type(MagneticConfig.from_state(state))
        machine = to_osa_type(Machine.from_state(state))

        lcfs_point = run_service(
            field_line_server.service.findLCFS,
            step,
            config,
            machine,
            settings,
            max_time=max_time,
        )  # find last closed flux surface
        return tfields.Points3D([[lcfs_point.x, lcfs_point.y, lcfs_point.z]])

    @staticmethod
    def _trace_line(state, points, step=0.01, numSteps=300):
        """
        Args:
            points (Points3D)
            step (flota): step width of the tracer task
        """
        field_line_server = get_server(WS_SERVER)
        points = to_osa_type(points, ws_server=WS_SERVER)

        config = to_osa_type(MagneticConfig.from_state(state))

        task = field_line_server.types.Task()
        task.step = step
        task.lines = field_line_server.types.LineTracing()
        task.lines.numSteps = numSteps

        LOGGER.info("starting line tracing ...")
        res = field_line_server.service.trace(points, config, task, None)
        LOGGER.info("... done")
        return [tfields.Points3D(line.vertices) for line in res.lines]

    @staticmethod
    def _trace_surface(state, **kwargs):
        start_point = kwargs.pop("start_point")
        n_points = kwargs.pop("n_points")
        step = kwargs.pop("step")

        assert len(start_point) == 1
        field_line_server = get_server(WS_SERVER)
        trace_task = field_line_server.types.Task()
        trace_task.step = step
        line = field_line_server.types.LineTracing()
        line.numSteps = n_points - 1
        trace_task.lines = line

        config = to_osa_type(MagneticConfig.from_state(state))
        start_point.transform(tfields.bases.CARTESIAN)
        start_point = to_osa_type(start_point, ws_server=WS_SERVER)

        res = run_service(
            field_line_server.service.trace,
            start_point,
            config,
            trace_task,
            None,
            max_time=None,
        )
        surface_points = res.lines[0].vertices
        surface_points = to_tfields_type(surface_points)
        return surface_points

    @staticmethod
    def _trace_diffusion(state, **kwargs):
        start_points = kwargs.pop("start_points")
        step = kwargs.pop("step")  # [m]
        connection_limit = kwargs.pop("connection_limit")
        inverse_field = kwargs.pop("inverse_field")

        # pylint: disable=no-member
        diffusion_coeff = state.plasma_parameters.diffusion_coeff
        # pylint: disable=no-member
        velocity = state.plasma_parameters.velocity

        field_line_server = get_server(WS_SERVER)

        # define all setting inputs for diffusion
        task = field_line_server.types.Task()
        task.step = step
        # TODO-2(@dboe)
        # free path is not part of defaults because has to be set dynamic with diffusion ->
        free_path = kwargs.pop("free_path", 0.1)  # [m]
        line_diffusion = field_line_server.types.LineDiffusion()
        line_diffusion.diffusionCoeff = diffusion_coeff
        line_diffusion.freePath = free_path
        line_diffusion.velocity = velocity
        task.diffusion = line_diffusion
        task.connection = field_line_server.types.ConnectionLength()
        task.connection.limit = connection_limit
        task.connection.returnLoads = True

        config = to_osa_type(MagneticConfig.from_state(state))
        config.inverseField = inverse_field
        machine = to_osa_type(Machine.from_state(state))
        start_points.transform(tfields.bases.CARTESIAN)

        res = run_service(
            field_line_server.service.trace,
            to_osa_type(start_points, ws_server=WS_SERVER),
            config,
            task,
            machine,
            max_time=None,
        )

        components = state.assembly.get_components(flat=True)

        return pwi_from_res(res, start_points, components, inverse_field)

    @staticmethod
    def _trace_connection_length(state, **kwargs):
        start_points = kwargs.pop("start_points")
        step = kwargs.pop("step")
        connection_limit = kwargs.pop("connection_limit")
        inverse_field = kwargs.pop("inverse_field")

        field_line_server = get_server(WS_SERVER)

        task = field_line_server.types.Task()
        task.step = step
        task.connection = field_line_server.types.ConnectionLength()
        task.connection.limit = connection_limit
        task.connection.returnLoads = False

        config = to_osa_type(MagneticConfig.from_state(state))
        config.inverseField = inverse_field
        machine = to_osa_type(Machine.from_state(state))
        start_points.transform(tfields.bases.CARTESIAN)

        res = run_service(
            field_line_server.service.trace,
            to_osa_type(start_points, ws_server=WS_SERVER),
            config,
            task,
            machine,
        )

        components = state.assembly.get_components(flat=True)

        return pwi_from_res(res, start_points, components, inverse_field)

    @staticmethod
    def _magnetic_field(state, **kwargs):
        points = kwargs.pop("points")

        # assure points has the correct format and coord_sys
        assert isinstance(points, tfields.Tensors)
        points.transform(tfields.bases.CARTESIAN)

        field_line_server = get_server(WS_SERVER)
        LOGGER.debug("Evaluating magnetic field at points.")
        config = to_osa_type(
            MagneticConfig.from_state(state),
            ws_server=WS_SERVER,
        )
        result = run_service(
            field_line_server.service.magneticField,
            to_osa_type(points, ws_server=WS_SERVER),
            config,
        )
        return to_tfields_type(result.field, coord_sys=tfields.bases.CARTESIAN)

    @staticmethod
    def _line_phi_span(state, **kwargs):
        points = kwargs.pop("points")
        phi = kwargs.pop("phi")
        step = kwargs.pop("step")
        inverse_field = kwargs.pop("inverse_field")

        field_line_server = get_server(WS_SERVER)

        points = to_osa_type(points, ws_server=WS_SERVER)

        config = to_osa_type(MagneticConfig.from_state(state))
        config.inverseField = inverse_field
        machine = (
            to_osa_type(Machine.from_state(state))
            if state.has(w7x.model.Assembly)
            else None
        )

        task = field_line_server.types.Task()
        task.step = step
        task.linesPhi = field_line_server.types.LinePhiSpan()
        task.linesPhi.phi = phi

        LOGGER.info("starting line tracing ...")
        res = run_service(
            field_line_server.service.trace,
            points,
            config,
            task,
            machine,
        )
        LOGGER.info("... done")
        return [to_tfields_type(line.vertices) for line in res.lines]


if __name__ == "__main__":
    import w7x.simulation.flt

    flt = w7x.simulation.flt.FieldLineTracer()
