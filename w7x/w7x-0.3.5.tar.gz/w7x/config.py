#!/usr/bin/env  # pylint: disable=missing-class-docstring,too-few-public-methods,abstract-method
"""
Settings and constants for the w7x module. They are all put directly into the w7x package namespace
TODO: rearrange config. Add config file possibility. Maybe make every class a module. That makes
namespace without caps

TODO(@amerlo, @dboe): Should we add the magnetic configs here?
"""

import os
import pathlib
import typing
import configparser
import re
import numpy as np

import rna
import rna.pattern.link
import tfields

import w7x.lib.dataclasses as dataclasses
from w7x.lib.equilibrium import Fourier, TensorSeries
from w7x.lib.profiles import Profile, PowerSeries
from w7x.model import (
    Assembly,
    Component,
    CoilSet,
    Coil,
    Equilibrium,
    PlasmaParameters,
    MGrid,
)
import w7x.merge

CONFIG_CACHE = {}  # Cache of already loaded .cfg files
DYNAMIC_OPTIONS = {}  # This is a memory on options set by the user with set_option


def get_config(config_path) -> configparser.ConfigParser:
    """
    Retrieve a .cfg config file
    """
    if config_path not in CONFIG_CACHE:
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            CONFIG_CACHE[config_path] = config
        else:
            CONFIG_CACHE[config_path] = None
    return CONFIG_CACHE[config_path]


VARIABLES = dict(
    HOME=str(pathlib.Path.home()),
    W7X_PACKAGE=os.path.dirname(__file__),
)
VARIABLES["W7X_HOME"] = os.path.join(VARIABLES["W7X_PACKAGE"], "..")
VARIABLES["W7X_RESOURCES"] = os.path.join(VARIABLES["W7X_HOME"], "tests/resources")
REGEX = r"[^${\}]+(?=})"


def get_option(section: str, option: str, fallback=False):
    """
    Retrieve option from section.
    """
    if section in DYNAMIC_OPTIONS and option in DYNAMIC_OPTIONS[section]:
        # set_option was active
        return DYNAMIC_OPTIONS[section][option]

    config_resolve_order = [
        rna.path.resolve("~", ".w7x", "local.cfg"),
        rna.path.resolve("~", ".w7x", "config.cfg"),
        rna.path.resolve(os.path.dirname(__file__), "config.cfg"),
    ]
    val = None
    for config_path in config_resolve_order:
        config = get_config(config_path)
        if config is None:
            continue
        try:
            val = config.get(section, option)
        except (configparser.NoOptionError, configparser.NoSectionError):
            val = None

        if val is not None:
            break

    if val is not None:
        # replace explicit mentions of VARIABLES
        for env_var, env_value in VARIABLES.items():
            val = val.replace("$" + env_var, env_value)

        # replace by regex with recursive get_option
        matches = re.finditer(REGEX, val)
        for match in reversed(list(matches)):
            start, end = match.span()
            # recursively replace the match by get_option
            val = (
                val[: start - 2]
                + get_option(*match.group().rsplit(".", 1))
                + val[end + 1 :]
            )
    elif val is None and fallback:
        val = get_option(section.rpartition(".")[0], option, fallback=fallback)

    return val


def set_option(section: str, option: str, value: any):
    if section not in DYNAMIC_OPTIONS:
        DYNAMIC_OPTIONS[section] = {}
    DYNAMIC_OPTIONS[section][option] = value


def unset_option(section: str, option: str):
    del DYNAMIC_OPTIONS[section][option]


def get_mgrid_options(return_type=None):
    """
    Reads the [mgrid] options and returns base vectors and iter_order (see MGrid or
    tfields.TensorGrid)

    Args:
        return_type: if not None, cast directly to type
    """
    nfp = int(w7x.config.get_option("mgrid", "nfp"))
    base_vectors = []
    iter_order = []
    for var in ["r", "phi", "z"]:
        xmin = w7x.config.get_option("mgrid." + var, "min")
        xmin = float(xmin) if xmin != "None" else 0
        xmax = w7x.config.get_option("mgrid." + var, "max")
        xmax = float(xmax) if xmax != "None" else 2 * np.pi / nfp
        num = complex(w7x.config.get_option("mgrid." + var, "num") + "j")
        base_vectors.append((xmin, xmax, num))
        iter_order.append(int(w7x.config.get_option("mgrid." + var, "iter")))

    if return_type is not None:
        if issubclass(return_type, tfields.TensorGrid):
            grid = tfields.TensorGrid.empty(
                *base_vectors,
                coord_sys=tfields.bases.CYLINDER,
                iter_order=iter_order,
            )
            return grid
        else:
            raise NotImplementedError(f"return_type {return_type} not yet implemented")
    return base_vectors, iter_order, nfp


class CoilTypes:
    @dataclasses.dataclass
    class NonPlanar(Coil):
        n_windings: int = 108

    @dataclasses.dataclass
    class Planar(Coil):
        n_windings: int = 36

    @dataclasses.dataclass
    class IslandControl(Coil):
        """
        Also known as control coil or sweep coil
        """

        n_windings: int = 8

    @dataclasses.dataclass
    class TrimA(Coil):
        n_windings: int = 46

    @dataclasses.dataclass
    class TrimB(Coil):
        n_windings: int = 72


class CoilGroups:
    """
    Non planar coils are initalized with 13.2 kA current.
    """

    # Abstract base Groups
    @dataclasses.dataclass
    class NonPlanar(CoilSet):
        shared_supply: typing.List[typing.Tuple[int]] = dataclasses.field(
            default_factory=lambda: [
                tuple((id_ for id_ in range(50) if id_ % 5 == 0)),
                tuple((id_ for id_ in range(50) if id_ % 5 == 1)),
                tuple((id_ for id_ in range(50) if id_ % 5 == 2)),
                tuple((id_ for id_ in range(50) if id_ % 5 == 3)),
                tuple((id_ for id_ in range(50) if id_ % 5 == 4)),
            ]
        )

    @dataclasses.dataclass
    class Planar(CoilSet):
        shared_supply: typing.List[typing.Tuple[int]] = dataclasses.field(
            default_factory=lambda: [
                tuple((id_ for id_ in range(20) if id_ % 2 == 0)),
                tuple((id_ for id_ in range(20) if id_ % 2 == 1)),
            ]
        )

    @dataclasses.dataclass
    class IslandControl(CoilSet):
        stellarator_symmetric_shared_supply: typing.ClassVar[
            typing.List[typing.Tuple[int]]
        ] = [
            tuple((id_ for id_ in range(10) if id_ % 2 == 0)),
            tuple((id_ for id_ in range(10) if id_ % 2 == 1)),
        ]
        shared_supply: typing.List[typing.Tuple[int]] = dataclasses.field(
            default_factory=lambda: CoilGroups.IslandControl.stellarator_symmetric_shared_supply
        )

        @property
        def stellarator_symmetric(self) -> bool:
            """
            Controls if the shared_supply emulates stellarator symmetric control
            """
            return self.shared_supply == self.stellarator_symmetric_shared_supply

        @stellarator_symmetric.setter
        def stellarator_symmetric(self, stel_sym: bool):
            if stel_sym:
                self.shared_supply = self.stellarator_symmetric_shared_supply
            else:
                self.shared_supply = None

    @dataclasses.dataclass
    class Trim(CoilSet):
        pass

    # Concrete base Groups
    @dataclasses.dataclass
    class IdealNonPlanar(NonPlanar):
        name: str = "ideal non planar coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.NonPlanar(id=id_, current=13.2e3)  # = 1.43e6 / 108
                for id_ in range(160, 210)
            ],
        )

    @dataclasses.dataclass
    class IdealPlanar(Planar):
        name: str = "ideal planar coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.Planar(id=id_) for id_ in range(210, 230)
            ],
        )

    @dataclasses.dataclass
    class IdealIslandControl(IslandControl):
        name: str = "ideal island control coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.IslandControl(id=id_) for id_ in range(230, 240)
            ],
        )

    @dataclasses.dataclass
    class IdealTrim(Trim):
        name: str = "ideal trim coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.TrimA(id=350),
                CoilTypes.TrimB(id=241),
                CoilTypes.TrimA(id=351),
                CoilTypes.TrimA(id=352),
                CoilTypes.TrimA(id=353),
            ],
        )

    @dataclasses.dataclass
    class DeformedNonPlanar(NonPlanar):
        name: str = "deformed non planar coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.NonPlanar(id=id_, current=13.2e3)  # = 1.43e6 / 108
                for id_ in range(1012, 1062)
            ]
        )

    @dataclasses.dataclass
    class DeformedPlanar(Planar):
        name: str = "deformed planar coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.Planar(id=id_) for id_ in range(1062, 1082)
            ],
        )

    @dataclasses.dataclass
    class AsBuiltNonPlanar(NonPlanar):
        name: str = "as built non planar coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.NonPlanar(id=id_, current=13.2e3)  # = 1.43e6 / 108
                for id_ in range(1152, 1202)
            ],
        )

    @dataclasses.dataclass
    class AsBuiltPlanar(Planar):
        name: str = "as built planar coils"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilTypes.Planar(id=id_) for id_ in range(1202, 1222)
            ],
        )


class CoilSets:
    @dataclasses.dataclass
    class Ideal(CoilSet):
        name: str = "ideal w7x coil set"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilGroups.IdealNonPlanar(),
                CoilGroups.IdealPlanar(),
                CoilGroups.IdealIslandControl(),
                CoilGroups.IdealTrim(),
            ],
        )

    @dataclasses.dataclass
    class Deformed(CoilSet):
        name: str = "deformed w7x coil set"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilGroups.DeformedNonPlanar(),
                CoilGroups.DeformedPlanar(),
                CoilGroups.IdealIslandControl(),  # There is no model for 'deformed ic'
                CoilGroups.IdealTrim(),  # There is no model for 'deformed trim'
            ],
        )

    @dataclasses.dataclass
    class AsBuilt(CoilSet):
        name: str = "deformed w7x coil set"
        info: str = "coils calculated by T. Andreva. Asbuilt with deformations"
        coils: typing.List[Coil] = dataclasses.children_alias(
            default_factory=lambda: [
                CoilGroups.AsBuiltNonPlanar(),
                CoilGroups.AsBuiltPlanar(),
                CoilGroups.IdealIslandControl(),  # There is no model for 'deformed ic'
                CoilGroups.IdealTrim(),  # There is no model for 'deformed trim'
            ],
        )


class AssemblyGroups:  # fomerly MeshedModelsIds(object):
    """
    ids of meshed models (PFCs etc) reffering to the mesh server
    """

    @dataclasses.dataclass
    class MeshEnd(Assembly):
        name: str = "mesh end"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [Component(id=164, color="black")],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Divertor(Assembly):
        name: str = "divertor"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="firebrick") for id_ in range(165, 170)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class DivertorKisslinger(Assembly):
        name: str = "divertor plane by kisslinger"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="firebrick") for id_ in range(30, 70)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Baffle(Assembly):
        name: str = "baffle"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="black") for id_ in range(320, 325)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Tda(Assembly):
        name: str = "tda"
        color: str = "dimgrey"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [Component(id=id_) for id_ in range(325, 330)],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Shield(Assembly):
        name: str = "heat shield"
        info: str = "Wall protection with carbon tiles"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="slategrey") for id_ in range(330, 335)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Panel(Assembly):
        name: str = "panel"
        info: str = "Wall protection with stainless steel"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="grey") for id_ in range(335, 340)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Vessel(Assembly):
        name: str = "vessel"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="dimgrey") for id_ in range(340, 344)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Scraper(Assembly):
        name: str = "scraper element"
        color: str = "darkslateblue"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="darkslateblue") for id_ in range(349, 359)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Limiter(Assembly):
        name: str = "limiter(OP1.1)"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="firebrick")
                for id_ in [489, 488, 487, 486, 485]
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class LimiterKisslinger(Assembly):
        name: str = "limiter(OP1.1)"
        info: str = "EPS2014 here the tiles are not existing. one greate plane"
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                Component(id=id_, color="firebrick") for id_ in range(479, 484)
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )


class Assemblies:
    """
    Compilations of CAD assemblies
    """

    @dataclasses.dataclass
    class PfcsOp11(Assembly):
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                AssemblyGroups.Limiter(),
                AssemblyGroups.Vessel(),
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )

    @dataclasses.dataclass
    class Pfcs(Assembly):
        components: typing.List[
            typing.Union[Component, "Assembly"]
        ] = dataclasses.children_alias(
            default_factory=lambda: [
                AssemblyGroups.Divertor(),
                AssemblyGroups.Baffle(),
                AssemblyGroups.Tda(),
                AssemblyGroups.Shield(),
                AssemblyGroups.Panel(),
                AssemblyGroups.Vessel(),
                AssemblyGroups.MeshEnd(),
            ],
            metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
        )


class Plasma:
    """
    Generic easy to use plasma parameters configuration.

    TODO-2(@amerlo, @dboe): I am here without further thinking, what should we have:
                            * vacuum state?
                            * easy to access beta configuration?
                            * later on we should have a PlasmaParameters.from_discharge
    """

    # pylint:disable=too-many-instance-attributes
    @dataclasses.dataclass
    class Vacuum(PlasmaParameters):
        """
        Careful when you work with this class. The name implies this is only one special kind of
        PlasmaParameters but it is allow to change the attributes afterwards. It is only here
        for STARTING the state at Vacuum. It can be modified as liked.

        TODO-2(@dboe): this is not beatuiful. Also things under Equilibria should actually be
        a function. This requires changes in dependencies
        """

        plasma_beta: float = 0.0
        bootstrap_current: float = 0.0

        t_e: Profile = PowerSeries(coefficients=[0.0, 0.0], domain=[0, 1])
        t_i: Profile = PowerSeries(coefficients=[0.0, 0.0], domain=[0, 1])
        n_e: Profile = PowerSeries(coefficients=[0.0, 0.0], domain=[0, 1])
        n_i: Profile = PowerSeries(coefficients=[0.0, 0.0], domain=[0, 1])

        pressure_profile: Profile = PowerSeries(
            coefficients=[1e-6, -1e-6], domain=[0, 1]
        )
        current_profile: Profile = PowerSeries(coefficients=[0.0, 0.0], domain=[0, 1])
        iota_profile: Profile = None

        pressure_scale: float = 0.0
        total_toroidal_current: float = 0.0


def _get_mgrid_path():
    """Get mgrid path from config.cfg"""
    backend = get_option("vmec", "backend", fallback=True)
    return get_option(f"vmec.{backend}", "mgrid", fallback=True)


class Equilibria:
    """
    Default equilibrium states.
    """

    @dataclasses.dataclass
    class InitialGuess(Equilibrium):
        """
        Good candidate as initial equilibrium.
        """

        field_period: int = 5
        vacuum_field: tfields.TensorGrid = rna.pattern.link.Link(
            ref=MGrid(path=_get_mgrid_path()),
            fget=MGrid.to_numpy,
        )
        flux_surfaces: TensorSeries = TensorSeries(
            Fourier.from_coefficients(
                cos=[0.0, 0.0, 0.0, 0.0, 5.5496e00, 4.3857e-1, 0.0, 0.0, 0.0]
                + [0.0] * 36
                + [
                    1.8275e-03,
                    1.6341e-03,
                    1.2163e-03,
                    3.0809e-03,
                    5.5289e00,
                    2.6718e-01,
                    -2.1739e-03,
                    -2.8507e-04,
                    -1.8275e-03,
                    1.6341e-03,
                    1.2163e-03,
                    3.0809e-03,
                    3.4528e-02,
                    4.4872e-01,
                    -2.7085e-01,
                    -4.9284e-03,
                    4.9911e-04,
                    6.5184e-05,
                    4.8734e-04,
                    1.4054e-03,
                    4.8047e-03,
                    1.5134e-02,
                    3.5687e-02,
                    4.9779e-02,
                    6.5200e-02,
                    -1.1350e-02,
                    -1.6119e-03,
                    1.0339e-04,
                    -3.2332e-04,
                    -3.4468e-04,
                    -1.5729e-03,
                    -2.0611e-03,
                    -1.4756e-02,
                    -1.9949e-02,
                    -8.5802e-03,
                    3.8516e-03,
                    1.1352e-04,
                    3.6285e-04,
                    2.4647e-04,
                    6.2828e-04,
                    2.7421e-03,
                    4.9943e-03,
                    7.4223e-03,
                    -5.0041e-04,
                    -5.9196e-04,
                ],
                mpol=4,
                ntor=4,
                num_field_periods=5,
            ),
            Fourier.from_coefficients(
                sin=[0.0, 0.0, 0.0, 0.0, 0.00000, -3.0789e-01, 0.0, 0.0, 0.0]
                + [0.0] * 36
                + [
                    4.5363e-04,
                    3.1625e-04,
                    3.5963e-04,
                    8.3725e-03,
                    -0.0000e00,
                    -2.0666e-01,
                    -4.1458e-03,
                    -1.9493e-03,
                    2.0185e-03,
                    3.4400e-03,
                    7.7506e-03,
                    1.4961e-02,
                    4.0227e-02,
                    5.6892e-01,
                    2.0596e-01,
                    -5.7604e-03,
                    -5.6140e-03,
                    -4.2485e-03,
                    4.5363e-04,
                    3.1625e-04,
                    3.5963e-04,
                    8.3725e-03,
                    1.1405e-03,
                    2.3889e-02,
                    -6.0502e-02,
                    8.9796e-03,
                    9.1004e-04,
                    -3.7464e-04,
                    -4.2385e-05,
                    5.3668e-04,
                    -1.7563e-03,
                    -4.2733e-03,
                    -4.4707e-03,
                    9.5155e-03,
                    1.0233e-02,
                    -2.8137e-03,
                    1.2480e-04,
                    -8.7567e-05,
                    7.6525e-05,
                    6.1672e-04,
                    3.6261e-03,
                    -2.8280e-03,
                    7.3549e-03,
                    -5.6303e-03,
                    -2.8346e-04,
                ],
                mpol=4,
                ntor=4,
                num_field_periods=5,
            ),
        )


class MagneticConfig:
    """
    Reference magnetic configurations for W7-X operations.

    TODO(@amerlo,@dboe)-1: should experimental configurations given in rw? I should
                           say in A. Should we add the "_a" suffix there, even if these
                           are experimental configurations, so it is implicit that
                           are given in A.
    TODO(@amerlo)-2: include more experimental configurations.

    Examples:
        >>> import w7x

        Use relative windings representation of reference configurations
        >>> coil_set = w7x.config.CoilSets.Ideal.from_currents(
        ...     *w7x.config.MagneticConfig.standard_rw,
        ...     unit="rw")
        >>> coil_set.coil_currents("rw")[:7]
        [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0]

        Or use experimental ids
        >>> coil_set = w7x.config.CoilSets.Ideal.from_currents(
        ...     *w7x.config.MagneticConfig.ejm_252,
        ...     unit="A")
        >>> coil_set.coil_currents("A")[:7]
        [13068, 13068, 13068, 13068, 13068, -700, -700]
    """

    #  Magnetic configurations in relative windings
    standard_rw = [1.0, 1.0, 1.0, 1.0, 1.0] + [0.0] * (2 + 2 + 5)
    high_iota_rw = [1.0, 1.0, 1.0, 1.0, 1.0, -0.23, -0.23] + [0.0] * (2 + 5)
    low_iota_rw = [1.0, 1.0, 1.0, 1.0, 1.0, 0.25, 0.25] + [0.0] * (2 + 5)
    inward_shifted_rw = [0.96, 0.95, 0.97, 1.07, 1.08, 0.1, -0.2] + [0.0] * (2 + 5)
    outward_shifted_rw = [1.04, 1.04, 1.01, 0.96, 0.96, -0.14, 0.14] + [0.0] * (2 + 5)
    low_mirror_rw = [0.94, 0.98, 0.98, 1.06, 1.06] + [0.0] * (2 + 2 + 5)
    high_mirror_rw = [1.08, 1.05, 1.0, 0.95, 0.92] + [0.0] * (
        2 + 2 + 5
    )  # TODO(@dboe): here rw false
    low_shear_rw = [1.13, 1.12, 1.05, 0.85, 0.84, -0.2, 0.2] + [0.0] * (2 + 5)
    limiter_case_rw = [1.07, 1.10, 1.02, 0.92, 0.89, -0.1, 0.2] + [0.0] * (2 + 5)
    high_iota_a_rw = [1.0, 1.0, 1.0, 1.0, 1.0, -0.25, 0.0] + [0.0] * (2 + 5)
    high_iota_b_rw = [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, -0.25] + [0.0] * (2 + 5)
    low_iota_a_rw = [1.0, 1.0, 1.0, 1.0, 1.0, 0.25, 0.0] + [0.0] * (2 + 5)
    low_iota_b_rw = [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.25] + [0.0] * (2 + 5)

    #  Experimental configurations
    #  From: Magnetic configurations for W7-X operation, 1-JDB00-T0001.1
    #  Standard configuration
    ejm_252 = [13068, 13068, 13068, 13068, 13068, -700, -700] + [0.0] * (2 + 5)
    eim_252 = [12989, 12989, 12989, 12989, 12989, 0, 0] + [0.0] * (2 + 5)
    eim_261 = [13470, 13470, 13470, 13470, 13470, 0, 0] + [0.0] * (2 + 5)
    #  High iota configuration
    ftm_252 = [14199, 14199, 14199, 14199, 14199, -9797, -9797] + [0.0] * (2 + 5)
    #  High mirror configuration
    kjm001_252 = [12871, 13123, 13897, 11965, 10845, 0, 0] + [0.0] * (2 + 5)
    #  Limiter configuration
    eem_260 = [12780, 12780, 12780, 12780, 12780, 4980, 4980] + [0.0] * (2 + 5)
