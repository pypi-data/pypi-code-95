"""
Equilibrium Node with abstract backend.

Tasks
-----

TODO-1(@amerlo): improve docstrings.
"""

from abc import abstractmethod
import copy
import dataclasses
from enum import Enum
import logging
import os
import typing

from netCDF4 import Dataset
import numpy as np

from rna.pattern.link import Link
import w7x
import w7x.plotting.poincare
from w7x.core import Code, Backend, State, StateComponent
from w7x.simulation.flavors.equilibrium import EquilibriumMixin
from w7x.lib.equilibrium import TensorSeries, Cos, Sin, Fourier, FourierTerm
from w7x.lib.profiles import Profile, PowerSeries
from w7x.lib.utils import gen_run_id


class Status(Enum):
    """Status of the vmec run."""

    SUCCESS = 0  # VMEC execution terminated normally without erros nor warnings
    BOUNDARY = -1  # Plasma Boundary exceeded Vacuum Grid Size
    NOT_STARTED = -2  # VMEC has not been started yet
    INCREASE_NITER = -3  # VMEC does not converge within given NITER
    BAD_JACOBIAN = -4  # The jacobian was non-definite
    TIMEOUT = -5  # VMEC has been halted (e.g., by LURM) due to time limite
    UNKNOWN = -6


LOGGER = logging.getLogger(__name__)


def get_indata_line(key: str, value: str, new_line: bool = True) -> str:
    """
    Create a vmec input line.
    """

    line = key

    if isinstance(value, str):
        value = f"'{value}'"
    elif isinstance(value, bool):
        value = "T" if value else "F"
    elif hasattr(value, "__len__"):
        value = " ".join([str(v) for v in value])
    else:
        value = str(value)

    line += " = " + value

    if new_line:
        line += "\n"

    return line


def get_vmec_profile_type(profile: Profile, kind: str) -> str:
    """
    Establish vmec profile type.
    """

    supported_profile_kind = ["pressure", "current", "current_density", "iota"]

    if kind not in supported_profile_kind:
        raise ValueError("%r kind of profile is not supported" % kind)

    profile_class = profile.__class__.__name__

    if profile_class == "PowerSeries":
        return "power_series"

    if profile_class == "TwoPower":
        return "two_power"

    if profile_class == "SumAtan":
        return "sum_atan"

    if profile_class == "CubicSpline" or profile_class == "GaussianProcess":
        if kind == "current":
            return "cubic_spline_I"
        elif kind == "current_density":
            return "cubic_spline_Ip"
        else:
            return "cubic_spline"

    raise ValueError("%r is not supported" % type(profile))


def get_indata_profile_lines(profile: Profile, kind: str, n: int) -> str:
    """
    Get vmec indata profile lines.
    """

    if profile is None:
        return ""

    if kind == "pressure":
        type_key = "PMASS_TYPE"
        aux_f_key = "AM_AUX_F"
        aux_s_key = "AM_AUX_S"
        coef_key = "AM"
    elif kind in ["current", "current_density"]:
        type_key = "PCURR_TYPE"
        aux_f_key = "AC_AUX_F"
        aux_s_key = "AC_AUX_S"
        coef_key = "AC"
    elif kind == "iota":
        type_key = "PIOTA_TYPE"
        aux_f_key = "AI_AUX_F"
        aux_s_key = "AI_AUX_S"
        coef_key = "AI"
    else:
        raise ValueError("%r kind profile is not supported" % kind)

    lines = get_indata_line(
        type_key,
        get_vmec_profile_type(profile, kind=kind),
    )
    profile_type = profile.__class__.__name__
    if profile_type in ["CubicSpline", "GaussianProcess"]:
        #  TODO-1(@amerlo): support tensor series
        aux_s, aux_f = profile.linspace(n=n, domain=[0, 1])
        lines += get_indata_line(aux_f_key, aux_f)
        lines += get_indata_line(aux_s_key, aux_s)
    elif profile_type in ["PowerSeries", "TwoPower", "SumAtan"]:
        lines += get_indata_line(coef_key, profile.coefficients)

    return lines


def get_indata_axis_lines(axis: TensorSeries) -> str:
    """
    Get vmec indata axis lines.
    """

    def get_coef(series: FourierTerm) -> list:
        """
        Extract the m=0, n >= 0 series coefficients.
        """
        return list(series.coef[0, 0, series.ntor :])

    lines = ""

    if axis.dims[0].cos is not None:
        lines += get_indata_line("RAXIS_CC", get_coef(axis.dims[0].cos))

    if axis.dims[0].sin is not None:
        lines += get_indata_line("RAXIS_CS", get_coef(axis.dims[0].sin))

    if axis.dims[1].cos is not None:
        lines += get_indata_line("ZAXIS_CC", get_coef(axis.dims[1].cos))

    if axis.dims[1].sin is not None:
        lines += get_indata_line("ZAXIS_CS", get_coef(axis.dims[1].sin))

    return lines


def get_indata_boudary_lines(boundary: TensorSeries) -> str:
    """
    Get vmec indata boundary lines.
    """

    lines = ""

    for mi, m in enumerate(boundary.dims[0].cos.poloidal_modes):
        for ni, n in enumerate(boundary.dims[0].cos.toroidal_modes):

            if boundary.dims[0].cos is not None:
                lines += get_indata_line(
                    f"RBC({n},{m})",
                    boundary.dims[0].cos.coef[0, mi, ni],
                    new_line=False,
                )
                lines += " "

            if boundary.dims[0].sin is not None:
                lines += get_indata_line(
                    f"RBS({n},{m})",
                    boundary.dims[0].sin.coef[0, mi, ni],
                    new_line=False,
                )
                lines += " "

            if boundary.dims[1].cos is not None:
                lines += get_indata_line(
                    f"ZBC({n},{m})",
                    boundary.dims[1].cos.coef[0, mi, ni],
                    new_line=False,
                )
                lines += " "

            if boundary.dims[1].sin is not None:
                lines += get_indata_line(
                    f"ZBS({n},{m})",
                    boundary.dims[1].sin.coef[0, mi, ni],
                    new_line=False,
                )

            lines += "\n"

    return lines


def get_indata_file_name(vmec_id: str) -> str:
    """
    Generate default VMEC input file name based on vmec id.
    """
    return f"input.{vmec_id}"


def get_run_status_from_threed1(threed1: str) -> Status:
    """
    Retrieve VMEC run status from threed1 file.

    TODO-1(@amerlo): check for TIMEOUT
    TODO-2(@amerlo): how to treat boundary warning just as a warning?
    """

    if (
        "Plasma Boundary exceeded Vacuum Grid Size" in threed1
        and "EXECUTION TERMINATED NORMALLY" not in threed1
    ):
        status = Status.BOUNDARY
    elif "Try increasing NITER" in threed1:
        status = Status.INCREASE_NITER
    elif "The jacobian was non-definite!" in threed1:
        status = Status.BAD_JACOBIAN
    elif "EXECUTION TERMINATED NORMALLY" in threed1:
        status = Status.SUCCESS
    else:
        #  If none of the above are in file, assume timeout or execution halted
        status = Status.UNKNOWN

    return status


def is_status_ready(status: Status) -> bool:
    """
    Define ready statuses.
    """
    return status in [
        w7x.simulation.vmec.Status.SUCCESS,
        w7x.simulation.vmec.Status.INCREASE_NITER,
        w7x.simulation.vmec.Status.BAD_JACOBIAN,
        w7x.simulation.vmec.Status.TIMEOUT,
        w7x.simulation.vmec.Status.BOUNDARY,
    ]


def is_status_successful(status: Status) -> bool:
    """Define successful statuses."""
    return status == Status.SUCCESS


def validate_force_tolerance_levels(ftol: list) -> list:
    """
    Validate force tolerance levels.
    """
    if len(ftol) <= 1:
        return ftol
    if ftol[-1] > ftol[-2]:
        return ftol[:-1] + [ftol[-2]]
    return ftol


def _converge_suggest(
    state,
    kwargs,
    wout,
    phi_edge_factor=2.0 / 3.0,
    force_update_on_boundary_warning=True,
    niter_step=10000,
    force_tolerance_factor=1e2,
):
    """
    Heuristic to update state attribute and VMEC kwargs to coverge.

    TODO-2(@amerlo): add magnetic axis shift.

    Args:
        state (w7x.State): state from where to run VMEC.
        kwargs (dict): kwargs to pass to VMEC.
        wout (Wout): wout file to check for converge.

    Returns:
        Tuple fo state attributes.
        Kwargs to pass to VMEC.
    """

    vmec_input = VmecInput.from_state(state, **kwargs)

    #  State attribute to update
    equi = state.equilibrium

    #  Kwargs to update
    num_iter = vmec_input.num_iter
    ftol = vmec_input.force_tolerance_levels

    if wout.status == Status.SUCCESS:
        pass
    elif wout.status == Status.BOUNDARY and force_update_on_boundary_warning:
        equi.phi *= phi_edge_factor
        LOGGER.info(
            "Plasma Boundary exceeded Vacuum Grid Size. "
            f"Reducing phi edge by {phi_edge_factor}"
        )
    elif wout.status == Status.INCREASE_NITER:
        num_iter = vmec_input.num_iter + niter_step
        LOGGER.info(f"Increase niter from {vmec_input.num_iter} to {num_iter}.")
    elif wout.status == Status.TIMEOUT:
        ftol = vmec_input.force_tolerance_levels[:-1] + [
            vmec_input.force_tolerance_levels[-1] * force_tolerance_factor
        ]
        ftol = validate_force_tolerance_levels(ftol)
        LOGGER.info(
            "VMEC did not converge in time, "
            f"reduce force tolerance level from {vmec_input.force_tolerance_levels[-1]} "
            f"to {ftol[-1]}."
        )

    kwargs.update({"num_iter": num_iter, "force_tolerance_levels": ftol})
    return (equi,), kwargs


def validate_phi_edge(
    major_radius: float,
    plasma_volume: float,
    phi: list,
    iota: list,
    min_volume: float = 25,
    max_volume: float = 30,
    island_width: float = 0.075,
    iota_islands: list = None,
    deg: int = 4,
):
    """
    Get estimate for phi_edge.

    TODO-1(@amerlo): improve docstring.

    Args:
        min_volume: min volume in m^3
        max_volume: max volume in m^3
        island_width: radial width of the major islands in m.
            It is needed to find the maximal radius in order to
            find flux surfaces that are not bound by major islands.

    Returns:
        Phi edge value.
    """

    if len(phi) != len(iota):
        raise ValueError(
            "Length of given phi values %d is different from length of given iota values %d"
            % (len(phi), len(iota))
        )

    if min_volume > max_volume:
        raise ValueError(
            "Min volume %f is greater then max volume %f" % (min_volume, max_volume)
        )

    ns = len(phi)

    # Fit iota(r) with known plasma volume -> V = 2 pi^2 R r^2
    max_r_from_vol = np.sqrt(plasma_volume / (2 * np.pi ** 2 * major_radius))
    rs = np.linspace(0.0, 1.0, num=ns) * max_r_from_vol

    r_vs_iota = np.polynomial.polynomial.Polynomial.fit(iota, rs, deg=deg)

    # Find max r
    #     -> greater than min_volume
    #     -> smaller than max_volume
    #     -> not bound by major islands
    max_r_from_user = np.sqrt(max_volume / (2 * np.pi ** 2 * major_radius))
    min_r_from_user = np.sqrt(min_volume / (2 * np.pi ** 2 * major_radius))
    if max_r_from_vol < min_r_from_user:
        # Pick an average r
        max_r = (max_r_from_user + min_r_from_user) / 2
    else:
        max_r = min(max_r_from_vol, max_r_from_user)

    # Use main island chains
    if iota_islands is None:
        iota_islands = [4.0 / 5.0, 5.0 / 5.0, 6.0 / 5.0]

    # Move max_r away from major islands
    r_islands = [r_vs_iota(i) for i in iota_islands]
    for ri in r_islands:
        # TODO-1(@amerlo) jump in the middel of two islands in case of overlap.
        # TODO-2(@amerlo) replace island_widht parameter by calculation?
        if abs(max_r - ri) < 0.5 * island_width:
            max_r = ri - 0.5 * island_width
            break

    # If the given minor radius is ok, return same phi edge
    if max_r == max_r_from_vol:
        return phi[-1]

    # phi vs r is linear by definition
    return phi[-1] * max_r / max_r_from_vol


def _get_p0_vs_beta(
    pressure: list,
    beta: list,
    I1: typing.Union[float, list] = None,
    deg: int = 1,
    #: If return_inverse is True, return beta(p0)
    return_inverse: bool = False,
) -> callable:
    """
    Return p0(beta) fit.

    If empty lists are given, return educated guess based on EJM+252 scaling.
    """

    # TODO-2(@amerlo): evaluate to use values from web_service standard configuration
    if pressure is None:
        assert I1 is not None and type(I1) is not list
        #  Use values from EJM+252 config
        pressure = [2e5]
        beta = [0.03]
        #  Scale beta first based on I1
        beta = [b * (13067 / I1) ** 2 for b in beta]
        return _get_p0_vs_beta(
            pressure=pressure,
            beta=beta,
            I1=[13067] * len(pressure),
            deg=deg,
            return_inverse=return_inverse,
        )

    if not isinstance(I1, list):
        I1 = [I1] * len(pressure)

    #  Use values with same I1, pick last one in list
    valid_indices = [i for i, v in enumerate(I1) if v == I1[-1]]

    pressure = [0] + [pressure[i] for i in valid_indices]
    beta = [0] + [beta[i] for i in valid_indices]

    if return_inverse:
        return np.polynomial.polynomial.Polynomial.fit(pressure, beta, deg=deg)

    return np.polynomial.polynomial.Polynomial.fit(beta, pressure, deg=deg)


def _magnetic_config_suggest(
    state,
    kwargs,
    beta,
    beta_threshold=0.001,
    b_axis=None,
    b_axis_threshold=0.01,
    trials=None,
    min_ftol=1e-10,
):
    """
    Suggest state attributes and kwargs to reach target magnetic configuration.

    Steps:
        1. Change p0 and phi_edge till target beta is reached
        2. Change p0/I1 for target b_axis
        3. Increase resolution

    Args:
        state (w7x.State): w7x state.
        kwargs: VMEC kwargs.
        trials (list): list of (state, kwargs, wout) tuple from previous trials.
        beta (float): target beta to reach.
        b_axis (float): target magnetic field on axis to reach.

    Returns:
        Tuple of (coil, equi, plasma) state attriubutes.
        Kwargs argument for vmec._compute.

    Note:
        Here we assume the last trial as the best one, this has to be assured by the user.

    TODO-2(@amerlo): abstract to generic suggest algorithm.
    TODO-2(@amerlo): add domain information.
    TODO-1(@amerlo): add phi_edge estimate to not intercept islands.
    """

    assert beta is not None

    kwargs = copy.deepcopy(kwargs)
    vmec_input = VmecInput.from_state(state, **kwargs)

    #  State attributes to update
    coil = state.coil_set
    equi = state.equilibrium
    plasma = state.plasma_parameters

    coil_currents = coil.coil_currents("A")
    p0 = plasma.pressure_profile(0.0)

    #  Kwargs to update
    ftol = vmec_input.force_tolerance_levels

    if trials is None or len(trials) == 0:
        #  Use educated guess from EJM+252 scaling
        p0 = _get_p0_vs_beta(pressure=None, beta=None, I1=coil_currents[0])(beta)
        ftol = validate_force_tolerance_levels(ftol[:-1] + [min_ftol])
        LOGGER.info("First trial, use educated guess from EJM+252 scaling.")
    elif np.abs(trials[-1]["wout"].get_betatotal() - beta) > beta_threshold:
        #  The target beta has not been reached yet
        p0 = _get_p0_vs_beta(
            pressure=[
                t["state"].plasma_parameters.pressure_profile(0.0) for t in trials
            ],
            beta=[t["wout"].get_betatotal() for t in trials],
            I1=[t["state"].coil_set.coil_currents("A")[0] for t in trials],
        )(beta)
        ftol = validate_force_tolerance_levels(ftol[:-1] + [min_ftol])
        LOGGER.info("Target beta not achieved yet.")
    elif (
        b_axis is not None
        and np.abs(trials[-1]["wout"].b_axis(0.0) - b_axis) > b_axis_threshold
    ):
        #  The target magnetic field on axis has not been reached yet
        f = b_axis / trials[-1]["wout"].b_axis(0.0)
        coil_currents = [i * f for i in trials[-1]["state"].coil_set.coil_currents("A")]
        p0 = f ** 2 * trials[-1]["state"].plasma_parameters.pressure_profile(0.0)
        LOGGER.info("Target magnetic field on axis not achieved yet.")
    else:
        LOGGER.info("Everything looks fine, use requested force tolerance.")

    LOGGER.info(f"Propose p0: {p0:3.2e} I1: {coil_currents[0]:.0f} ftol: {ftol}")

    plasma.pressure_profile = plasma.pressure_profile * (
        p0 / plasma.pressure_profile(0.0)
    )
    coil = w7x.config.CoilSets.Ideal.from_currents(*coil_currents, unit="A")

    kwargs["force_tolerance_levels"] = ftol

    return (coil, equi, plasma), kwargs


@dataclasses.dataclass
class VmecInput:
    """
    A generic vmec input object.

    TODO-2(@amerlo): VmecInput could be returned and shoudl be a File

    Examples:
        >>> from w7x.simulation.vmec import VmecInput
        >>> vmec_input = VmecInput()
        >>> vmec_input.gamma
        0

        >>> vmec_input.num_field_periods = 5
        >>> vmec_input.num_field_periods
        5

        >>> vmec_input.num_modes_poloidal
        12

        >>> vmec_input.free_boundary
        True

        >>> vmec_input.to_string().startswith("&INDATA")
        True

        A unique vmec id is generated at init time
        >>> vmec_input.vmec_id is not None
        True

        But you could also define one
        >>> my_vmec_input = VmecInput(vmec_id="my_vmec_run")
        >>> my_vmec_input.vmec_id
        'my_vmec_run'

    """

    vmec_id: str = None

    # TODO-1(@amerlo): should we strictly use the names from VMEC indata file? -> VMEC
    free_boundary: bool = True
    mgrid_path: str = None
    coil_currents: typing.List[float] = dataclasses.field(
        default_factory=lambda: [  # TODO-1(@amerlo) remove this rather specific default
            1.384814e04,
            1.384814e04,
            1.384814e04,
            1.384814e04,
            1.384814e04,
            8.308887e03,
            8.308887e03,
        ]
    )
    magnetic_axis: TensorSeries = None
    boundary: TensorSeries = None

    pressure_profile: Profile = None
    pressure_scale: float = 1.0
    spres_ped: float = 1.0
    gamma: float = 0
    bloat: float = 1.0
    toroidal_current_profile: Profile = None
    total_toroidal_current: float = 0.0
    iota_profile: Profile = None

    force_tolerance_levels: typing.List[float] = dataclasses.field(
        default_factory=lambda: [1e-3, 1e-5, 1e-9, 1e-15]
    )
    num_iter: int = 40000
    num_step: int = 100
    num_vac_skip: int = 6
    num_conv_out: int = 100
    phi_edge: float = -2.0
    num_field_periods: int = 5
    num_grid_points_radial: typing.List[float] = dataclasses.field(
        default_factory=lambda: [4, 9, 28, 99]
    )
    num_grid_points_poloidal: int = 32
    num_grid_points_toroidal: int = 36
    num_modes_poloidal: int = 12
    num_modes_toroidal: int = 12
    tcon0: float = 2.0
    time_step: float = 0.9

    #  TODO-2(@amerl0): implement me in __post_init__ method.
    #  Retrieve magneticAxis and boundary from W7-X function parametrization
    #  http://webservices.ipp-hgw.mpg.de/docs/w7xfp.html
    # if use_initial_guess:
    #     magnetic_axis, boundary = (None, None)
    #     if getInitialGuess:
    #         (magneticAxis, boundary) = get_initial_from_w7xfp(
    #             coil_currents=magnetic_config.coil_currents("A"),
    #             pressure=pressure_profile,
    #             current=current_profile,
    #         )

    def __post_init__(self):
        if self.vmec_id is None:
            self.vmec_id = gen_run_id(self, code="vmec", unique=True)

    @classmethod
    def _validate_kwargs(cls, kwargs: dict) -> dict:
        """
        Validate kwargs to subset of cls attributes.
        """
        return {k: v for k, v in kwargs.items() if k in cls.__dataclass_fields__}

    @classmethod
    def default(cls):
        """
        Method for fast creation of a VMEC input with a proper default.
        """
        return cls.from_state(
            w7x.config.CoilSets.Ideal(),
            w7x.config.Plasma.Vacuum(),
            w7x.config.Equilibria.InitialGuess(),
        )

    @classmethod
    def from_state(cls, *args: typing.Union[State, StateComponent], **kwargs):
        """
        Factory method for building a VMEC input from state.

        Examples:
            >>> import w7x
            >>> vmec_input = w7x.simulation.vmec.VmecInput.from_state(
            ...     w7x.config.CoilSets.Ideal(), w7x.config.Plasma.Vacuum(),
            ...     w7x.config.Equilibria.InitialGuess(),
            ...     force_tolerance_levels=[1e-3, 1e-5, 1e-9, 1e-12])
            >>> vmec_input.gamma
            0

            >>> vmec_input.coil_currents[:5]
            [13200.0, 13200.0, 13200.0, 13200.0, 13200.0]
            >>> vmec_input.coil_currents[5:]
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

            >>> vmec_input.pressure_profile.coefficients
            [1e-06, -1e-06]

            >>> vmec_input.force_tolerance_levels
            [0.001, 1e-05, 1e-09, 1e-12]
        """

        vmec_input = cls(**cls._validate_kwargs(kwargs))
        state = w7x.State.merged(*args)

        vmec_input.coil_currents = state.coil_set.coil_currents(unit="A")

        if state.has(w7x.model.Equilibrium):

            vacuum_field_link = state.equilibrium.get_ref("vacuum_field")
            if vacuum_field_link is not None:
                vmec_input.mgrid_path = vacuum_field_link.path

            if state.equilibrium.field_period is not None:
                vmec_input.num_field_periods = state.equilibrium.field_period

            if state.equilibrium.phi is not None:
                vmec_input.phi_edge = state.equilibrium.phi_edge

            if state.equilibrium.magnetic_axis is not None:
                vmec_input.magnetic_axis = state.equilibrium.magnetic_axis

            if state.equilibrium.lcfs is not None:
                vmec_input.boundary = state.equilibrium.lcfs

        if state.has(w7x.model.PlasmaParameters):

            if state.plasma_parameters.pressure_profile is not None:
                vmec_input.pressure_profile = state.plasma_parameters.pressure_profile

            if state.plasma_parameters.current_profile is not None:
                vmec_input.toroidal_current_profile = (
                    state.plasma_parameters.current_profile
                )

            if state.plasma_parameters.iota_profile is not None:
                vmec_input.iota_profile = state.plasma_parameters.iota_profile

            if state.plasma_parameters.total_toroidal_current is not None:
                vmec_input.total_toroidal_current = (
                    state.plasma_parameters.total_toroidal_current
                )

        return vmec_input

    def to_string(self):
        """
        Returns vmec input as string.

        Note: possibly transcoding could be used here, too
        """

        indata = "&INDATA\n"
        indata += get_indata_line("LFREEB", self.free_boundary)
        indata += get_indata_line(
            "MGRID_FILE",
            self.mgrid_path if self.mgrid_path else None,
        )
        indata += get_indata_line("EXTCUR", self.coil_currents)
        indata += get_indata_line("NVACSKIP", self.num_vac_skip)
        indata += get_indata_line("DELT", self.time_step)
        indata += get_indata_line("TCON0", self.tcon0)
        indata += get_indata_line("NITER", self.num_iter)
        indata += get_indata_line("NSTEP", self.num_step)
        indata += get_indata_line("FTOL_ARRAY", self.force_tolerance_levels)
        indata += get_indata_line("PHIEDGE", self.phi_edge)
        indata += get_indata_line("NFP", self.num_field_periods)
        indata += get_indata_line("MPOL", self.num_modes_poloidal)
        indata += get_indata_line("NTOR", self.num_modes_toroidal)
        indata += get_indata_line("NZETA", self.num_grid_points_toroidal)
        indata += get_indata_line("NTHETA", self.num_grid_points_poloidal)
        indata += get_indata_line("NS_ARRAY", self.num_grid_points_radial)
        indata += get_indata_line("NCURR", 0 if self.iota_profile else 1)
        indata += get_indata_line("GAMMA", self.gamma)
        indata += get_indata_line("BLOAT", self.bloat)
        indata += get_indata_line("PRES_SCALE", self.pressure_scale)
        indata += get_indata_line("SPRES_PED", self.spres_ped)

        # TODO-1(@amerlo): where to define wether current or current density?
        indata += get_indata_profile_lines(
            self.pressure_profile, kind="pressure", n=self.num_grid_points_radial[-1]
        )
        indata += get_indata_profile_lines(
            self.toroidal_current_profile,
            kind="current",
            n=self.num_grid_points_radial[-1],
        )
        indata += get_indata_profile_lines(
            self.iota_profile, kind="iota", n=self.num_grid_points_radial[-1]
        )

        indata += get_indata_line("CURTOR", self.total_toroidal_current)

        if self.magnetic_axis is not None:
            indata += get_indata_axis_lines(self.magnetic_axis)

        if self.boundary is not None:
            indata += get_indata_boudary_lines(self.boundary)

        indata += "/\n"
        return indata


@dataclasses.dataclass
class Wout(w7x.model.File):
    """
    Object to handle vmec wout  files.
    """

    # TODO-1(@dboe,@amerlo): move to model. E.g. extender requires the same

    status: Status = None

    def __update__(self, other):
        """
        Method required for Saveable polymorphism
        """
        self.__init__(other.asdict())

    @classmethod
    def from_vmec_id(self, vmec_id: str):
        """
        Args:
            vmec_id
        """

    @classmethod
    def _load_nc(cls, file_path: str, **kwargs):
        """
        Read a vmec output file.
        """

        data = Dataset(file_path, mode="r")

        if "file_id" not in kwargs:
            import re

            match = re.search(r"^wout_(.*)\.nc$", os.path.basename(file_path))
            if match:
                vmec_id = match.group(1)
            else:
                vmec_id = None

        return cls(data=data, path=file_path, file_id=vmec_id, **kwargs)

    def _save_nc(self, file_path: str):
        """
        Save a vmec output to netCDF4 file.
        """

        with self.data as src, Dataset(file_path, mode="w") as dst:

            for name, dimension in src.dimensions.items():
                dst.createDimension(
                    name, len(dimension) if not dimension.isunlimited() else None
                )

            for name, variable in src.variables.items():
                dst.createVariable(name, variable.datatype, variable.dimensions)
                dst.variables[name][:] = src.variables[name][:]

    def to_state(self) -> w7x.State:
        """
        Create a state with equilibrium set from a wout file.
        """

        if self.data is None:
            return w7x.State.merged(
                w7x.model.Equilibrium(), w7x.model.Resources([self])
            )

        mgrid = w7x.model.MGrid(path=self.get_mgrid_file())
        equi = w7x.model.Equilibrium(
            vacuum_field=Link(ref=mgrid, fget=w7x.model.MGrid.to_numpy),
            field_period=Link(ref=self, fget=Wout.get_nfp),
            phi=Link(ref=self, fget=Wout.get_phi_as_profile),
            flux_surfaces=Link(ref=self, fget=Wout.get_flux_surfaces),
            plasma_volume=Link(ref=self, fget=Wout.get_volume_p),
            beta=Link(ref=self, fget=Wout.get_betatotal),
            b_axis=Link(ref=self, fget=Wout.b_axis),
            iota=Link(ref=self, fget=Wout.get_iota_as_profile),
        )
        return w7x.State.merged(equi, w7x.model.Resources([self, mgrid]))

    def b_axis(self, phi: float = 0.0) -> float:
        """
        Magnetic field on axis.

        TODO-2(@amerlo): implement this from `bdotb` as suggested by Jonathan.
                         look into the jxbforce()
        """

        ss = np.linspace(0, 1, num=self.data["ns"][:].item())
        points = [[s, 0, phi] for s in ss]

        #  Use only the values closest to the axis
        max_ns = 4
        B = self.get_magnetic_field_strength()(points[1:max_ns])
        B_fit = PowerSeries.fit(x=ss[1:max_ns], y=B, deg=2)

        return B_fit(0)

    def get_magnetic_field_strength(self) -> TensorSeries:
        """
        The magnetic field strength as Fourier series.
        """

        nfp = int(self.data["nfp"][:])

        mpol = int(self.data["xm"][-1].item()) + 1
        ntor = int(self.data["xn"][-1].item() / nfp)
        if "xm_nyq" in self.data.variables:
            mpol = int(self.data["xm_nyq"][-1].item()) + 1
            ntor = int(self.data["xn_nyq"][-1].item() / nfp)

        bmnc = self.data["bmnc"][:]
        bmnc = np.insert(bmnc, 0, np.zeros((ntor, bmnc.shape[0])), axis=1)

        shape = (bmnc.shape[0], mpol, 2 * ntor + 1)
        bcos = Cos(list(bmnc.reshape(shape)), num_field_periods=nfp)

        return TensorSeries(Fourier(cos=bcos))

    def get_nfp(self):
        """
        Number of field periods.
        """
        return self.data["nfp"][:].item()

    def get_betatotal(self):
        """
        The total volume averaged beta.
        """
        return self.data["betatotal"][:].item()

    def get_phi(self):
        """
        Toroidal flux on full mesh.
        """
        return self.data["phi"][:]

    def get_iotaf(self):
        """
        Iota on full mesh.
        """
        return self.data["iotaf"][:]

    def get_iota_as_profile(self):
        """
        Iota as PowerSeries profile.
        """
        s = np.linspace(0, 1, num=self.data["ns"][:])
        return PowerSeries.fit(x=s, y=self.data["iotaf"][:], deg=4)

    def get_phi_as_profile(self):
        """
        Toroidal flux on full mesh as linear profile.
        """
        s = np.linspace(0, 1, num=self.data["ns"][:])
        return PowerSeries.fit(x=s, y=self.data["phi"][:], deg=1)

    def get_mgrid_file(self) -> str:
        """
        The mgrid file used in the computation.
        """
        mgrid_file = self.data["mgrid_file"][:].tolist()
        mgrid_file = "".join([x.decode("UTF-8") for x in mgrid_file]).strip()
        return mgrid_file

    def get_volume_p(self) -> float:
        """
        The plasma volume.
        """
        return self.data["volume_p"][:].item()

    def get_rmajor_p(self) -> float:
        """
        The plasma major radius.
        """
        return self.data["Rmajor_p"][:].item()

    def get_aminor_p(self) -> float:
        """
        The plasma minor raiuds.
        """
        return self.data["Aminor_p"][:].item()

    def get_flux_surfaces(self) -> TensorSeries:
        """
        The flux surfaces description as Fourier series.
        """

        # TODO-2(@amerlo): add the other components for a non-stellarator symmetry.

        nfp = int(self.data["nfp"][:])

        mpol = int(self.data["xm"][-1].item()) + 1
        ntor = int(self.data["xn"][-1].item() / nfp)

        rmnc = self.data["rmnc"][:]
        zmns = self.data["zmns"][:]
        rmnc = np.insert(rmnc, 0, np.zeros((ntor, rmnc.shape[0])), axis=1)
        zmns = np.insert(zmns, 0, np.zeros((ntor, rmnc.shape[0])), axis=1)

        shape = (rmnc.shape[0], mpol, 2 * ntor + 1)

        rcos = Cos(list(rmnc.reshape(shape)), num_field_periods=nfp)
        zsin = Sin(list(zmns.reshape(shape)), num_field_periods=nfp)

        return TensorSeries(Fourier(cos=rcos), Fourier(sin=zsin))


class VmecBackend(Backend):
    """
    Backend base class to be subclassed for Vmec code.
    """

    @staticmethod
    @abstractmethod
    def _compute(state, **kwargs) -> Wout:
        pass


# pylint: disable=abstract-method
class Vmec(Code, EquilibriumMixin):  # pylint: disable=abstract-method
    """
    High level Vmec object.

    Examples:
        >>> import w7x
        >>> from w7x.simulation.vmec import Vmec
        >>> state = w7x.State(w7x.config.CoilSets.Ideal(),
        ...     w7x.config.Plasma.Vacuum(), w7x.config.Equilibria.InitialGuess())

        Use the web service by default
        >>> vmec = Vmec()

        To not pollute the web service.
        # >>> state = vmec.free_boundary(state)

    """

    STRATEGY_TYPE = VmecBackend
    STRATEGY_DEFAULT = w7x.config.get_option("vmec", "backend")

    @w7x.node()
    # @w7x.dependencies.extends(EquilibriumMixin.free_boundary)
    @w7x.dependencies(
        w7x.config.CoilSets.Ideal,
        w7x.config.Plasma.Vacuum,
        w7x.config.Equilibria.InitialGuess,
        free_boundary=True,
        dry_run=False,
    )
    def free_boundary(self, state, **kwargs):
        # # TODO-0(@amerlo,@dboe): If distribute is true, and w7x.config.Equilibria.InitialGuess()
        # is passed (no implicit from dependency) state.equilibrium.flux_surfaces.dims is empty in
        # free_boundary instead of two Fourier()
        wout = self._converge(state, **kwargs)
        return wout.to_state()

    @w7x.node()
    @w7x.dependencies.extends(EquilibriumMixin.fixed_boundary)
    def fixed_boundary(self, state, **kwargs):
        wout = self._converge(state, **kwargs)
        return wout.to_state()

    #####################
    # CODE ONLY METHODS #
    #####################

    # TODO-2(@amerlo) implement method
    # @w7x.node()
    # @w7x.dependencies.extends()
    # def find_closest(self, state, **kwargs):
    #     return

    @w7x.node()
    @w7x.dependencies.extends(
        EquilibriumMixin.free_boundary,
        beta_threshold=0.001,
        b_axis=None,
        b_axis_threshold=0.01,
        max_evals=10,
    )
    def search(self, state, **kwargs):
        """
        Search for target magnetic configuration in term of beta and magnetic field
        on axis.

        TODO-2(@amerlo): add ranges of tunable parameters here.
        TODO-2(@amerlo): how to cast as a generic optimization?
        """

        max_evals = kwargs.pop("max_evals")
        beta = kwargs.pop("beta")
        b_axis = kwargs.pop("b_axis")
        beta_threshold = kwargs.pop("beta_threshold")
        b_axis_threshold = kwargs.pop("b_axis_threshold")

        LOGGER.info("Start magnetic config search. Targets:")
        LOGGER.info("{:10s} {:5.4f}".format("beta", beta))
        if b_axis is not None:
            LOGGER.info("{:10s} {:5.4f}".format("b_axis", b_axis))

        trials = []
        for i in range(max_evals):
            # TODO-2(@amerlo,@dboe): use node inside instead of decorated /or additionally?
            args, kwargs_ = _magnetic_config_suggest(
                state,
                kwargs,
                beta=beta,
                beta_threshold=beta_threshold,
                b_axis=b_axis,
                trials=trials,
            )
            state = w7x.State.merged(state, *args)
            trial = {"state": state, "kwargs": copy.deepcopy(kwargs_)}
            wout = self._converge(state, **kwargs_)
            trial["wout"] = wout
            trials.append(trial)

            LOGGER.info(
                "Iteration: {:3s} beta: {:5.4f} b_axis: {:5.4f}".format(
                    str(i), wout.get_betatotal(), wout.b_axis(0.0)
                )
            )

            if (np.abs(wout.get_betatotal() - beta) < beta_threshold) and (
                b_axis is None or np.abs(wout.b_axis(0.0) - b_axis) < b_axis_threshold
            ):
                LOGGER.info(
                    f"Found {wout.get_betatotal():5.4f} beta "
                    f"with {wout.b_axis(0.0):3.2f} magnetic field on axis."
                )
                break

        return wout.to_state()

    ###################
    # PRIVATE METHODS #
    ###################

    @w7x.dependencies.stateless(
        num_iter=40000,
        iterations=1,
        force_tolerance_levels=[1e-3, 1e-5, 1e-9, 1e-15],
    )
    def _converge(self, state, **kwargs):
        """
        Call VMEC backend till convergence.
        """

        iterations = kwargs.pop("iterations")

        for i in range(iterations):
            LOGGER.info(
                f"Call the VMEC backend {type(self.backend).__name__} for the {i} iteration."
            )
            wout = self.backend._compute(state, **kwargs)

            if wout.status == Status.SUCCESS or i == iterations - 1:
                break

            args, kwargs = _converge_suggest(state, kwargs, wout)
            state = w7x.State.merged(state, *args)

        return wout
