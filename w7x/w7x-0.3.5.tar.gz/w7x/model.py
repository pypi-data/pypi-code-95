# pylint: disable=too-many-instance-attributes,too-many-lines
"""
Abstract State Attributes defining input and output namespace of models

Zen:
    * As flat as possible, as nested as necessary

"""

import logging
import typing
import numpy as np

import tfields
import rna.pattern.link

from w7x.compatibility import sqlalchemy, declared_attr
from w7x.lib import dataclasses
from w7x.lib.equilibrium import (
    Cos,
    Sin,
    Fourier,
    TensorSeries,
)
from w7x.lib.profiles import Profile
from w7x.state import Entry, StateComposite, StateLeaf, State
import w7x.merge


# TODO-2(@dboe): resolve conflict between dask and sqlalchemy,
#                pk field with init=False is primary_key
# from sqlalchemy.orm import registry
# mapper_registry = registry()


@dataclasses.dataclass
class PlasmaParameters(StateLeaf):
    """
    Plasma parameters
    """

    #  Required by field line tracer.
    #  TODO-1(@dobe): replace velocity by temperature.
    #: velocity at edge [m/s] (10 - 200 eV  -> 140000 m/s) mendler,gao: 200000, with reversal 1e6/3
    velocity: float = 140000
    #: electron temperature profile
    t_e: typing.Union[tfields.TensorFields, Profile] = None
    # TODO-1(@dboe,@amerlo): document
    t_i: typing.Union[tfields.TensorFields, Profile] = None
    n_e: typing.Union[tfields.TensorFields, Profile] = None
    n_i: typing.Union[tfields.TensorFields, Profile] = None
    pressure_profile: typing.Union[tfields.TensorFields, Profile] = None

    diffusion_coeff: float = 1.0  # [m^2/s]

    current_profile: typing.Union[tfields.TensorFields, Profile] = None
    total_toroidal_current: float = None
    bootstrap_current: float = None
    iota_profile: typing.Union[tfields.TensorFields, Profile] = None


@dataclasses.dataclass
class NamedElement(Entry):
    """
    Generic element

    Args:
        name (str)
        info (str)
        id (str)
    """

    # pylint: disable=invalid-name
    id: int = dataclasses.field(
        default=None,
        metadata={"sa": sqlalchemy.Column(sqlalchemy.Integer, unique=True)},
    )
    name: str = dataclasses.field(
        default=None,
        metadata={"sa": sqlalchemy.Column(sqlalchemy.String(50), nullable=True)},
    )
    info: str = dataclasses.field(
        default=None,
        metadata={"sa": sqlalchemy.Column(sqlalchemy.String(200), nullable=True)},
    )


@dataclasses.dataclass
class DBExtension(NamedElement):
    """
    Extension of an extisting data base. id is the reference to the other db key.
    """

    custom_id: typing.Optional[int] = dataclasses.field(
        default=None, metadata={"sa": sqlalchemy.Column(sqlalchemy.Integer)}
    )

    @declared_attr
    # pylint:disable=no-self-argument
    def __table_args__(cls):
        return (sqlalchemy.UniqueConstraint("id", "custom_id"),)


@dataclasses.dataclass
class CoilSet(NamedElement, StateComposite):
    """
    Args:
        coils (typing.List[Coil]): single coils
        shared_supply (typing.List[typing.Tuple[int]]): integers per tuple refer to shared power
            supply. This determines the number of independent currents to be set.
            If it is None, assume one supply per coil.

    Examples:
        >>> import w7x
        >>> cs = w7x.model.CoilSet(coils=[w7x.model.Coil(id=42)])
        >>> assert 'coils' not in cs.__dict__
        >>> assert '_children' in cs.__dict__
        >>> assert cs.coils == cs._children
        >>> assert len(cs.coils) == 1
        >>> assert cs.coils[0] == w7x.model.Coil(id=42, n_windings=1, current=0.0)

    """

    coils: typing.List[typing.Union["CoilSet", "Coil"]] = dataclasses.children_alias(
        default_factory=lambda: []
    )
    shared_supply: typing.Optional[typing.List[typing.Tuple[int]]] = None
    # TODO(@dboe): virutal_supply for e.g. ic or trim coils?

    def get_coils(self, *args, groups: bool = False, **kwargs):
        """
        Recursively run through coils and coil_sets and join them recursively

        Args:
            *args and **kwargs forwarded to ::meth::`rna.pattern.composite.Composite.get_leaves`
            supply_groups: If supply_groups is True, do not flatten the

        Examples:
            >>> import w7x
            >>> cs = w7x.model.CoilSet(coils=[w7x.model.Coil(id=42), w7x.model.Coil(id=84)])
            >>> [c.id for c in cs.get_coils()]
            [42, 84]

            >>> nested_cs = w7x.model.CoilSet()
            >>> nested_cs.add(w7x.model.Coil(id=21))
            >>> nested_cs.add(cs)
            >>> coils = nested_cs.get_coils()
            >>> assert coils[0].id == 21
            >>> assert coils[1][0].id == 42
            >>> assert coils[1][1].id == 84
            >>> [c.id for c in nested_cs.get_coils(flat=True)]
            [21, 42, 84]

            Get (sub-)coil sets with just one level of leaves
            >>> coil_set = w7x.config.CoilSets.Ideal()
            >>> [type(cg).__name__ for cg in coil_set.get_coils(groups=True, flat=True)]
            ['IdealNonPlanar', 'IdealPlanar', 'IdealIslandControl', 'IdealTrim']
        """
        if groups:
            assert kwargs.get(
                "flat"
            ), "The 'groups' argument is only valid with 'flat' == True."

            def apply_composite(leaves, component, **forwarded_kwargs):
                composite_bools = [leaf.is_composite() for leaf in leaves]
                if not any(composite_bools):
                    # we are in flat, so it will be extended.
                    return [component]
                composites = []
                collect_coil_set = CoilSet()
                for is_composite, leaf in zip(composite_bools, leaves):
                    if is_composite:
                        composites.append(
                            leaf.get_coils(supply_groups=True, **forwarded_kwargs)
                        )
                    else:
                        collect_coil_set.add(leaf)
                if collect_coil_set.children:
                    composites.append(collect_coil_set)
                return composites

            return self.get_leaves(*args, apply_composite=apply_composite, **kwargs)
        return self.get_leaves(*args, **kwargs)

    def get_currents(
        self, independent: bool = False, flat: bool = False, **kwargs
    ) -> typing.List[float]:
        """
        Corrisponing counterpart to set_currents.

        Args:
            independent: if true, only return currents of independent power supplies
            flat: see get_leaves
            **kwargs: forwarded to coil.get_current recursively

        Examples:
            >>> import w7x
            >>> cs = w7x.model.CoilSet(coils=[w7x.model.Coil(id=42), w7x.model.Coil(id=84)])
            >>> cs.get_currents()
            [0.0, 0.0]

            >>> ideal = w7x.config.CoilSets.Ideal()
            >>> assert len(ideal.get_currents(flat=True)) == len(ideal.get_coils(flat=True))

            You can pass the attributes of Coil.get_current
            >>> high_iota = w7x.config.MagneticConfig.high_iota_rw
            >>> ideal_hm = w7x.config.CoilSets.Ideal.from_currents(
            ...     *high_iota[:7], 8/108, 8/108, unit="rw"
            ... )
            >>> ideal_hm.get_currents(unit='rw', independent=True, flat=True)[:7]
            [1.0, 1.0, 1.0, 1.0, 1.0, -0.23, -0.23]
            >>> high_iota[:7]
            [1.0, 1.0, 1.0, 1.0, 1.0, -0.23, -0.23]
            >>> ideal_hm.get_currents(unit='r', independent=True)[2]
            [1.0, 1.0]
            >>> ideal_hm.get_currents(unit='Aw', independent=True)[0]
            [1425600.0, 1425600.0, 1425600.0, 1425600.0, 1425600.0]
        """
        unit = kwargs.get("unit", "A")
        reference_coil = kwargs.get("reference_coil", None)
        if "r" in unit and reference_coil is None:
            kwargs["reference_coil"] = self.coils[0].coils[0]

        if independent and self.shared_supply is not None:
            # if shared_supply given coils need to be flat.
            coils = []
            for shared_indices in self.shared_supply:
                coils.append(self.coils[shared_indices[0]])
        else:
            coils = self.coils

        currents = []
        for component in coils:
            if component.is_composite():
                # coil_set
                if flat:
                    currents.extend(
                        component.get_currents(
                            independent=independent, flat=flat, **kwargs
                        )
                    )
                else:
                    currents.append(
                        component.get_currents(
                            independent=independent, flat=flat, **kwargs
                        )
                    )
            else:
                # coil
                currents.append(component.get_current(**kwargs))
        return currents

    def set_currents(self, currents: typing.List[float], **kwargs):
        """
        Coil current setter respecting shared power supply and unit

        Args:
            current (typing.List[float]): currents in unit (default 'A')
            **kwargs: see Coil.set_current

        Examples:
            >>> import w7x
            >>> npcs = w7x.config.CoilGroups.DeformedNonPlanar()
            >>> npcs.set_currents(
            ...     [1., 0.9, 0.9, 1.1, 1.2],
            ...     unit='rw', reference_coil=npcs.coils[0])

            >>> len(npcs.get_currents(unit='A'))
            50
            >>> [round(v) for v in npcs.get_currents(unit='A', independent=True)]
            [13200, 11880, 11880, 14520, 15840]

        """
        if self.shared_supply:
            for shared_indices, current in zip(self.shared_supply, currents):
                for i in shared_indices:
                    self.coils[i].set_current(current, **kwargs)
            return

        for coil, current in zip(self.coils, currents):
            coil.set_current(current, **kwargs)

    @classmethod
    def from_currents(cls, *currents, **kwargs):
        """
        Factory method for vacuum magnetic field construction with biot-savart.

        TODO-0(@dboe, @amerlo): scale kwargs is not implemented.

        Args:
            *currents (float):
                first 5 currents -> non planar currents
                optional:
                    next 2 currents -> planar currents
                    next 2 | 10 currents -> sweep coil currents
                        If 2 currents are given, assume equal current drive
                        in all upper and lower sweep coils respectively
                    next 5 -> trim coils
            **kwargs:
                unit (str):
                    The currents given have the unit Aw like in the web service
                    input for magnetic configs (see coil_currents method
                    docstring)
                scale (float): For all relative units ('rw', 'r'), the 'scale'
                    attribute is active. The default is
                    w7x.MagneticConfig.n_windings_npcs in 'rw'
                coils_ids: specify the coils by picking their ids from the
                    database.
                    NOTE: The order of the coils is not arbitrary. The coil ids
                        have to be given in the order:
                            1. 50 non planar coils NPC1-NPC5,NPC1-NPC5,...
                            2. 20 planar coils PCA,PCB,PCA,PCB,...
                            3. 10 sweep coils in the order of the half modules
                                (hm10, hm11,...)
                        Some coils_ids are already compiled into a list in
                        w7x.MagneticConfig.coils_ids

        Examples:
            >>> import w7x

            Build a low iota configuration from relative winding currents
            >>> m = w7x.config.CoilSets.Ideal.from_currents(
            ...     1, 1, 1, 1, 1, -0.23, -0.23, 0.001, 0.001,
            ...     unit='rw')

            Build the same config with any other unit combination
            >>> units = ['rw', 'r', 'Aw', 'A']
            >>> for unit in units:
            ...     m_tmp = w7x.config.CoilSets.Deformed.from_currents(
            ...         *m.coil_currents(unit=unit),
            ...         unit=unit, scale=None)

            or with pre-defined configurations
            >>> m_alternative = w7x.config.CoilSets.AsBuilt.from_currents(
            ...     *w7x.config.MagneticConfig.low_iota_rw,
            ...     unit='rw')

        """
        obj = cls()

        if not obj.coils:
            return obj

        unit = kwargs.pop("unit", "rw")
        if "r" in unit:
            reference_coil = obj.coils[0].coils[0]
        else:
            reference_coil = None

        current_index = 0
        for group in obj.coils:
            n_currents = len(group.get_currents(independent=True))
            group.set_currents(
                currents[current_index : current_index + n_currents],
                unit=unit,
                reference_coil=reference_coil,
            )
            current_index += n_currents

        return obj

    def coil_currents(self, unit="rw"):
        """
        Retrieve the coil currents ([c.current for c in self.coils]) in units of choice. This
        method is the opposite to tfields.MagneticConfig.from_currents.

        Args:
            **kwargs: see Coil.get_current

        Examples:
            >>> import w7x
            >>> import numpy as np

            >>> m = w7x.config.CoilSets.Ideal.from_currents(
            ...     1, 1, 1, 1, 1, 0.23, 0.23, 0, 0)
            >>> assert np.array_equal(
            ...     [round(x, 2) for x in m.coil_currents('rw')],
            ...      [1.0, 1.0, 1.0, 1.0, 1.0, 0.23, 0.23] + [0.0] * 7)
            >>> assert np.array_equal(
            ...     [round(x, 2) for x in m.coil_currents('r')],
            ...     [1.0, 1.0, 1.0, 1.0, 1.0, 0.69, 0.69] + [0.0] * 7)
            >>> assert np.array_equal(
            ...     [round(x) for x in m.coil_currents('Aw')],
            ...     [1425600.0] * 5 + [327888.0] * 2 + [0.0] * 7)
            >>> assert np.array_equal([round(x) for x in m.coil_currents('A')],
            ...                       [13200.0] * 5 + [9108.0] * 2 + [0.0] * 7)

        """
        return self.get_currents(unit=unit, flat=True, independent=True)

    def geiger_string(self) -> str:
        """
        Returns:
            str: string representation of the magnetic field

        Examples:
            >>> import w7x
            >>> w7x.config.CoilSets.Ideal().geiger_string()
            '1000_1000_1000_1000_+0000_+0000'

        """
        return "{0:-04d}_{1:-04d}_{2:-04d}_{3:-04d}_{4:0=+5d}_{5:0=+5d}".format(
            *[int(x * 1000) for x in self.coil_currents(unit="rw")[1:8]]
        )


@dataclasses.dataclass
class Coil(NamedElement, StateLeaf):
    """
    Args:
        id (int): coil id
        n_windings (int): number of conductor windings
        current (float): coil current [A]
    """

    PARENT_TYPE = CoilSet  # pylint:disable=invalid-name
    n_windings: int = 1
    current: float = 0.0  # [A] always!

    def set_current(
        self,
        current: float,
        unit: str = "A",
        reference_coil: typing.Optional["Coil"] = None,
    ):
        """
        Args:
            current (float): current in unit specified by keyword argument
            **kwargs: see get_current
        """
        # sanity checks
        if reference_coil is None:
            if "r" in unit:
                raise ValueError(
                    "Requiring reference_coil for converting relative unit to 'A'."
                )
        else:
            if "A" in unit:
                logging.warning(
                    "Unexpected argument reference_coil for absolute current."
                )

        if unit == "A":
            self.current = current
        elif unit == "Aw":
            self.current = current / self.n_windings
        elif unit == "rw":
            self.current = (
                current
                * (reference_coil.current * reference_coil.n_windings)
                / (self.n_windings)
            )
        elif unit == "r":
            self.current = current * reference_coil.current
        else:
            raise NotImplementedError(unit)

    def get_current(
        self, unit: str = "A", reference_coil: typing.Optional["Coil"] = None
    ):
        """
        Args:
            unit (str): what spec
                'A': the current that is actually applied to the coil set
                'Aw': in A * winding number - the current that is applied if
                    there would be just 1 winding. Non planar coils have 108
                    windings each, planar coils, 36 and control coils 8
                    windings each. The trim coils have 46 or 72 windings,
                    depending on the coil type.
                'rw': 'Aw' normalized by (i.e. relative to - hence 'r') the
                    first non planar coil
                'r': 'A' normalized by (i.e. relative to - hence 'r') the first
                    non planar coil
            reference_coil (Coil): coil object used as reference for normalization
        """
        # sanity checks
        if reference_coil is None:
            if "r" in unit:
                raise ValueError(
                    "Requiring reference_coil for converting 'A' to relative unit."
                )
        else:
            if "A" in unit:
                logging.warning(
                    "Unexpected argument reference_coil for absolute current."
                )

        if unit == "A":
            return self.current
        if unit == "Aw":
            return self.current * self.n_windings
        if unit == "rw":
            return (self.current * self.n_windings) / (
                reference_coil.current * reference_coil.n_windings
            )
        if unit == "r":
            return self.current / reference_coil.current
        raise NotImplementedError(unit)


@dataclasses.dataclass
class Resources(StateComposite):
    """
    Args:
        items: File objects describing the resources that were collected during the creation of
            this state

    """

    items: typing.List[typing.Union["Resources", "File"]] = dataclasses.children_alias(
        default_factory=lambda: [],
    )


@dataclasses.dataclass
class File(StateLeaf, rna.pattern.link.Reference):
    """
    Base class of a file (local, url or other). Objects of this type can be referenced
    with the Reference pattern as links.
    """

    PARENT_TYPE = Resources  # pylint:disable=invalid-name

    #: _references is usually set by Reference.__init__
    _references: typing.List[rna.pattern.link.Link] = dataclasses.field(
        default_factory=lambda: [],
        compare=False,
    )
    #: cache for data, not compared on __eq__ and not to be saved. All information is in path
    data: any = dataclasses.field(
        default=None,
        compare=False,
        metadata=dict(merged=w7x.merge.merge_discard),
    )
    #: path (or multiple paths) to the resource
    path: typing.Optional[typing.Union[typing.List[str], str]] = None
    #: identificator of the file. This could e.g. be a vmec_id
    file_id: str = None

    def __getstate__(self):
        """
        Required for pickling
        """
        res = {k: v for k, v in self.__dict__.items() if k != "data"}
        return res


def _fget_alias(alias):
    """
    Trigger self.load() which will have to set the attribute of the alias.
    """

    def fget(self):
        val = getattr(self, alias)
        if val is None:
            self.load()
            val = getattr(self, alias)
        return val

    return fget


@dataclasses.dataclass
class MGrid(File):
    """
    Magnetic grid files which are output of e.g., Makegrid (input to VMEC) and EXTENDER.
    """

    #: base vectors. Required, if MGrid is only partial (not e.g. TensorGrid)
    base_vectors: typing.Optional[typing.Tuple[tuple]] = dataclasses.alias_field(
        "_base_vectors",
        fget=_fget_alias("_base_vectors"),
        default=None,
    )
    #: iter_order. Required, if MGrid is only partial (not e.g. TensorGrid)
    iter_order: typing.Optional[typing.List[int]] = dataclasses.alias_field(
        "_iter_order",
        fget=_fget_alias("_iter_order"),
        default=None,
    )

    def to_numpy(self) -> tfields.TensorFields:
        """
        Return the TensorFields representation of the mgrid.
        """
        data = self.load()
        if isinstance(data, (tfields.TensorFields, tfields.TensorGrid)):
            return data
        if isinstance(data, (tfields.Tensors, np.ndarray)):
            # TODO(@dboe): default base_vectors and iter order if not given
            return tfields.TensorGrid.empty(
                *self.base_vectors,
                fields=[data],
                iter_order=self.iter_order,
                coord_sys=tfields.bases.CYLINDER,
            )
        raise NotImplementedError(f"Conversion of {type(data)} to tfields.TensorFields")

    def load(self):
        """
        Load and cache data on request
        """
        if self.data is None:
            extension = rna.path.extension(self.path)
            if extension in ("npz", "datc"):
                self.data = tfields.TensorGrid.load(self.path)
            if extension == "dat":
                self.data = tfields.Tensors.load(
                    self.path, coord_sys=tfields.bases.PHYSICAL_CYLINDER
                )
        if isinstance(self.data, tfields.TensorGrid):
            self.base_vectors = self.data.base_num_tuples()
            self.iter_order = self.data.iter_order
        return self.data

    def to_state(self, field_name="field") -> "State":
        """
        Create a state with equilibrium set from this file.
        """
        equi_dict = {field_name: rna.pattern.link.Link(ref=self, fget=MGrid.to_numpy)}
        equi = w7x.model.Equilibrium(**equi_dict)
        return w7x.State.merged(equi, w7x.model.Resources([self]))


@dataclasses.dataclass
class Equilibrium(StateLeaf):
    """
    Information about the magnetic field. This includes vacuum and equilibrium field compoents.

    TODO-2(@amerlo): lambda and phi might not be so descriptive. beta is an exception.
                     Specific for vmec
    """

    vacuum_field: tfields.TensorGrid = None
    field: tfields.TensorGrid = None
    plasma_field: tfields.TensorGrid = None
    field_period: int = None  # number of field periods TODO-2(@amerlo): rename

    #: toroidal magnetic flux profile till LCFS
    phi: typing.Union[tfields.TensorFields, Profile] = None
    #: effective radius till LCFS
    reff: typing.Union[tfields.TensorFields, Profile] = None
    #: enclosed plasma volume till LCFS
    plasma_volume: typing.Union[tfields.TensorFields, Profile] = None

    kinetic_energy: float = None
    #: volume averaged beta
    beta: float = None
    b_axis: float = None  # TODO-2(@amerlo): should be property

    flux_surfaces: TensorSeries = None
    lambda_: TensorSeries = None
    iota: typing.Union[tfields.TensorFields, Profile] = None

    # TODO-2(@amerlo): Names of the below?
    #: magnetic field strength
    b_mod: TensorSeries = None
    #: covariant magnetic field
    b_sup: TensorSeries = None
    #: contravariant magnetic field
    b_sub: TensorSeries = None
    # TODO-2(@amerlo) rename
    j: TensorSeries = None

    jacobian: TensorSeries = None

    def get_reff_at(
        self, locations: typing.Union[tfields.Points3D, typing.List[tfields.Points3D]]
    ) -> typing.Union[float, typing.List[float]]:
        """
        Get the effective radius at given locations.
        """
        raise NotImplementedError()

    # pylint:disable=invalid-name
    def get_flux_surfaces_at(
        self,
        s: typing.Union[float, typing.List[float]],
        phi: typing.Union[float, typing.List[float]],
        num_points: int = 36,
    ) -> typing.List[tfields.Points3D]:
        """
        Get flux surfaces locations.
        """
        raise NotImplementedError()

    def get_magnetic_axis_at_phi(
        self, phi: typing.Union[float, typing.List[float]]
    ) -> typing.Union[tfields.Points3D, typing.List[tfields.Points3D]]:
        """
        Get magnetic axis at given toroidal angles.
        """
        raise NotImplementedError()

    @property
    def magnetic_axis(self) -> TensorSeries:
        """
        The magnetic axis representation.
        """
        if self.flux_surfaces is not None:
            return TensorSeries(
                Fourier(
                    cos=Cos(
                        coef=self.flux_surfaces.dims[0].cos.coef[:1],
                        num_field_periods=self.flux_surfaces.dims[
                            0
                        ].cos.num_field_periods,
                    ).truncated(mpol=0, ntor=1),
                ),
                Fourier(
                    sin=Sin(
                        coef=self.flux_surfaces.dims[1].sin.coef[:1],
                        num_field_periods=self.flux_surfaces.dims[
                            1
                        ].sin.num_field_periods,
                    ).truncated(mpol=0, ntor=1),
                ),
            )
        return None

    @property
    def lcfs(self) -> TensorSeries:
        """
        The last closed flux surface representation.
        """
        if self.flux_surfaces is not None:
            return TensorSeries(
                Fourier(cos=Cos(self.flux_surfaces.dims[0].cos.coef[-1:])),
                Fourier(sin=Sin(self.flux_surfaces.dims[1].sin.coef[-1:])),
            )
        return None

    @property
    def phi_edge(self) -> float:
        """
        Total toroidal enclosed magnetic flux.
        """
        return self.phi(1.0)

    @property
    def lcfs_volume(self) -> float:
        """
        Total volume enclosed by the plasma.
        """
        return self.plasma_volume(1.0)


@dataclasses.dataclass
class Assembly(StateComposite, NamedElement):
    """
    Top level container for Assembly Groups.
    Information about CAD assemblies such as plasma facing components

    Examples:
        >>> import w7x
        >>> ag = w7x.config.AssemblyGroups.Divertor()
        >>> [c.id for c in ag.get_components(flat=True)]
        [165, 166, 167, 168, 169]

        >>> import w7x
        >>> pfcs = w7x.config.Assemblies.Pfcs()
        >>> [group.name for group in pfcs.components]
        ['divertor', 'baffle', 'tda', 'heat shield', 'panel', 'vessel', 'mesh end']
    """

    components: typing.List[
        typing.Union["Assembly", "Component"]
    ] = dataclasses.children_alias(
        default_factory=lambda: [],
        metadata=dict(merged=w7x.merge.merge_children_structure_preserving),
    )

    @classmethod
    def from_component_ids(cls, component_ids: list, **kwargs):
        """
        Factory method for creation of NON-nested AssemblyGroup from Components
        """
        components = []
        for id_ in component_ids:
            components.append(Component(id=id_))
        return cls(components=components, **kwargs)

    def get_components(self, flat: bool = False):
        """
        Recursively run through assembly components and assemblies and join component ids

        Args:
            flat (bool): flatten nested sub assemblies
        """
        return self.get_leaves(flat=flat)


# @mapper_registry.mapped  # creates problem since it directly assignes a value to the primary key
@dataclasses.dataclass
class Component(StateLeaf, DBExtension):
    """
    A Component is the lowermost abstraction of a CAD element. E.g. a divertor finger or tile
    """

    PARENT_TYPE = Assembly  # pylint:disable=invalid-name
    #: CAD representation of this component. TODO: put design load as maps.fields
    mesh: typing.Optional[tfields.Mesh3D] = dataclasses.field(
        default=None,
        compare=False,
        metadata=dict(merged=w7x.merge.merge_value_or_none),
    )
    #: Keys: phi, values: 2D slices through the component
    slices: typing.Optional[typing.Dict[float, tfields.Tensors]] = dataclasses.field(
        default=None,
        compare=False,
        metadata=dict(merged=w7x.merge.merge_dicts),
    )
    color: typing.Optional[str] = dataclasses.field(default=None, compare=False)


@dataclasses.dataclass
class Pwi(StateComposite):
    """
    Plasma-wall interactions
    """

    components: typing.List[
        typing.Optional[typing.Union["Pwi", "PlasmaComponentInteraction"]]
    ] = dataclasses.children_alias(
        default_factory=lambda: [],
        metadata=dict(merged=w7x.merge.merge_children_cumulative),
    )

    origin_points: typing.Optional[tfields.Tensors] = dataclasses.field(
        default=None,
        metadata=dict(
            merged=lambda *pts: pts[0]
        ),  # TODO(@dboe) we need more complex merge here!
    )

    def connection_lengths(self) -> tfields.TensorFields:
        """

        Examples:
        """
        if not self.components:
            return tfields.TensorFields([])
        first_direction = self.components[0].inverse_field
        cl = tfields.TensorFields(self.origin_points)  # pylint:disable=invalid-name
        lengths = tfields.Tensors(np.full((len(cl),), np.nan))
        for pci in filter(
            lambda c: c.inverse_field == first_direction, self.components
        ):
            lengths[pci.origin_point_indices] = pci.connection_lengths
        for pci in filter(
            lambda c: c.inverse_field != first_direction, self.components
        ):
            lengths[pci.origin_point_indices] += pci.connection_lengths
        cl.fields.append(lengths)
        return cl

    def get_pcis(
        self, *components: Component
    ) -> typing.List["PlasmaComponentInteraction"]:
        """
        Returns the pcis indexing the given components

        Args:
            *components: selection of components to consider
        """
        pcis = []
        for pci in self.components:
            for comp in components:
                if pci.component == comp:
                    pcis.append(pci)
        return pcis

    def hit_points(self, *components: Component) -> tfields.Tensors:
        """
        Return the hit_points of requested components.

        Args:
            *components: select which components to get the hit_points from
        """
        pcis = self.get_pcis(*components)

        if not pcis:
            return None

        hit_points = w7x.merge.merge_dataclasses_field(*pcis, field="hit_points")[
            "hit_points"
        ]

        return hit_points

    def power_density(self, component: Component) -> tfields.TensorFields:
        """
        Returns:
            mesh with number of hits and number of hits per area set

        # TODO(@dboe): unify *components?
        """
        pcis = self.get_pcis(component)

        if not pcis:
            return None

        # get the state component
        component = pcis[0].component
        n_hits = w7x.merge.merge_dataclasses_field(*pcis, field="n_hits")["n_hits"]
        areas = w7x.merge.merge_dataclasses_field(*pcis, field="areas")["areas"]

        if component.mesh is None:
            return dict(
                n_hits=n_hits,
                areas=areas,
                n_hits_per_area={k: n_hits[k] / areas[k] for k in n_hits},
            )

        mesh = component.mesh.copy()
        field_indices = list(sorted(n_hits.keys()))

        # n_hits_field
        n_hits_field = tfields.Tensors(np.zeros(len(mesh.faces)))
        n_hits_field[field_indices] = np.array([n_hits[key] for key in field_indices])
        n_hits_field.name = "n_hits"
        mesh.faces.fields.append(n_hits_field)

        # n_hits_per_area_field
        # Note: calculation of the area from mesh is rather slow. Hence I use the cached areas (1)
        #   Options:
        #       0: mesh.triangles().areas()
        #       1: cache areas
        #       2: cache triangles3d when cacheing mesh3D
        #       3: __getitem__ magic problem with areas? This is too slow
        # Option 0:
        # n_hits_per_area_field = tfields.Tensors(
        #     n_hits_field / mesh.triangles().areas()
        # )
        # mesh.faces.fields.append(n_hits_per_area_field)
        # TODO(@mendler,@sboz) areas are not exactly the same as ws (1-2 %)
        areas = mesh.triangles().areas()
        # Option 1:
        n_hits_per_area_field = tfields.Tensors(np.zeros(len(mesh.faces)))
        n_hits_per_area_field[field_indices] = np.array(
            [n_hits[key] / areas[key] for key in field_indices]
        )
        n_hits_field.name = "n_hits / area [1/m^2]"
        mesh.faces.fields.append(n_hits_per_area_field)
        return mesh


@dataclasses.dataclass
class PlasmaComponentInteraction(StateLeaf):
    """
    Plasma-wall interactions for a specific component
    """

    PARENT_TYPE = Pwi  # pylint:disable=invalid-name

    # properties to infer the origin of the results
    #: reference to the component (assuming 'frozen' Assemblies!). None if no component referenced
    component_index: int
    #: indicactes in what direction the trace has been calculated
    inverse_field: bool
    #: indices of the Pwi.origin_points indicating the origin of the hit_points
    origin_point_indices: typing.List[int]

    #: spatial hit location of the particles on the wall
    hit_points: typing.Optional[tfields.Tensors] = None
    #: indices of the faces of the component mesh on which the hit_points are terminated spatially
    hit_points_faces: typing.Optional[typing.List[int]] = None
    #: number of hits on a triangle of the component.
    #     dict refers with keys to face indices of the mesh and values to number of hits
    #     on that face
    n_hits: typing.Optional[
        typing.Union[typing.Dict[int, int], tfields.Tensors]
    ] = dataclasses.field(
        default=None,
        metadata=dict(merged=w7x.merge.merge_dicts_add_values),
    )
    #: areas of the faces of a triangle of the component.
    #     dict refers with keys to face indices of the mesh and values to area
    areas: typing.Optional[
        typing.Union[typing.Dict[int, float], tfields.Tensors]
    ] = dataclasses.field(
        default=None,
        metadata=dict(merged=w7x.merge.merge_dicts_assert_equal),
    )
    #: lenght of the trace from the origin point to the hit_point
    connection_lengths: typing.Optional[tfields.Tensors] = None

    @property
    def component(self) -> Component:
        """
        Returns:
            component reffering to this instance (by component_index)
        """
        if self.component_index is None:
            return None

        state = self
        while not isinstance(state, State):
            state = state.parent
            if state is None:
                raise ValueError("Component not found")

        comp = state.assembly.get_components(flat=True)[self.component_index]
        return comp


@dataclasses.dataclass
class Traces(StateLeaf):
    """
    Class collecting traces of e.g. electron guns or simulation traces of field line tracers.
    """

    lcfs_point: typing.Optional[tfields.Points3D] = None
    trajectories: typing.Optional[typing.List[tfields.Points3D]] = None
    surface: typing.Optional[tfields.Points3D] = None
    poincare_surfaces: typing.Optional[typing.List[tfields.Points3D]] = None


if __name__ == "__main__":
    pass
