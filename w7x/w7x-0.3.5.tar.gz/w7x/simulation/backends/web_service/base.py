"""
abstract classes to work with the webservice revolving around the osa package
"""
import copy
import logging
from urllib.error import HTTPError

import numpy as np
from six import string_types

import osa
import rna
import tfields

import w7x.lib
from w7x.simulation.vmec import get_vmec_profile_type


LOGGER = logging.getLogger(__name__)


def compare_error_attributes(
    error, errors=None, attributes=None, **kwargs  # pylint: disable=unused-argument
):
    """
    Annotation:
        if you want a content in the msg, use args attribute.

    Returns:
        True if error.attributes == error_list.attributes else False

    Examples:
        >>> from urllib.error import HTTPError
        >>> from w7x.simulation.backends.web_service import compare_error_attributes
        >>> d = {'errors': [HTTPError(None, 500, None, None, None),
        ...                 HTTPError("ASDF", 600, None, None, None)],
        ...      'attributes': ['code']}
        >>> compare_error_attributes(HTTPError(None, 500, None, None, None), **d)
        [True, False]
        >>> e = {'errors': [RuntimeError("A special Message content"),
        ...                 HTTPError("ASDF", 600, None, None, None)],
        ...      'attributes': ['args']}
        >>> compare_error_attributes(RuntimeError("A special Message content"), **e)
        [True, False]

    """
    errors = errors or []
    attributes = attributes or ["code"]
    comparisons = []
    for inst in errors:
        return_bool = True
        if type(error) is not type(inst):  # must be same type ...
            return_bool = False
        else:
            for (
                attr
            ) in attributes:  # ... and contain the same requested attribute values
                if not hasattr(error, attr) or not hasattr(inst, attr):
                    return_bool = False
                    break
                if attr == "args":
                    if len(error.args) == 0:
                        raise TypeError("Length of args is not suiting.")
                    if not inst.args[0] in error.args[0]:
                        return_bool = False
                        break
                elif not getattr(error, attr) == getattr(inst, attr):
                    return_bool = False
                    break
        comparisons.append(return_bool)
    return comparisons


def run_service(fun, *args, **kwargs):  # pylint: disable=too-many-branches
    """
    Run a service function with the arguments args. Check for HTTPError
    occurence and redo if you get it.
    Kwargs:
        max_tries (int): Maximum tries, Default is 1
        max_time (int): Maximum time for the process [s]. Default is inf (<None> value)
        errors (list of dicts describing errors): Each dict has the
            keywords:
                'errors' (list of Error instances)
                'attributes' (list of attributes)
                'action' (str): 'retry' / 'skip'
            Perform action if error.attributes == errors.attributes for any
            error
    Returns:
        Result of service or function. None if Error from errorDict says skip
    """
    max_tries = kwargs.pop("max_tries", 1)
    if max_tries < 1:
        raise ValueError("max_tries needs to be 1 at minimum.")
    max_time = kwargs.pop("max_time", None)
    errors_default = [
        {
            "errors": [HTTPError(None, 500, None, None, None)],
            "attributes": ["code"],
            "action": "retry",
        },
        {
            "errors": [HTTPError(None, 404, None, None, None)],
            "attributes": ["code"],
            "action": "retry",
        },
        {
            "errors": [HTTPError(None, 413, None, None, None)],
            "attributes": ["code"],
            "action": "retry",
        },
        {
            "errors": [RuntimeError("Grid_CylLowendel")],
            "attributes": ["args"],
            "action": "skip",
        },
        {
            "errors": [RuntimeError("ThreadTracer failed.")],
            "attributes": ["args"],
            "action": "skip",
        },
        {
            "errors": [RuntimeError("zero field")],
            "attributes": ["args"],
            "action": "skip",
        },
    ]
    errors = kwargs.pop("errors", [])
    errors.extend(errors_default)

    result = None
    try_count = 1

    @w7x.lib.timeout.timeout(max_time)
    def run(fun, *args):
        return fun(*args)

    LOGGER.debug(
        "Calling function %s with arguments:\n\t%s",
        fun,
        "\n\t".join([str(a) for a in args]),
    )
    while result is None:
        try:
            result = run(fun, *args)  # run service with arguments
            if result is None:
                LOGGER.warning("Result is really None")
            break
        except TimeoutError:
            LOGGER.error("TimeoutError. Took more than %s seconds.", max_time)
            if try_count < max_tries:
                try_count += 1
                LOGGER.info("Retry service %s.", fun)
            else:
                raise  # Also allows result being <None>
        except Exception as err:
            LOGGER.error(err)
            skip = False
            retry = False
            for error_dict in errors:
                if any(compare_error_attributes(err, **error_dict)):
                    if error_dict["action"] == "retry":
                        retry = True
                    elif error_dict["action"] == "skip":
                        skip = True
                    else:
                        raise TypeError(
                            "%s is no allowed Action" % error_dict["action"]
                        ) from err
            if skip:
                LOGGER.info("Skip service %s.", fun)
                break
            if retry:
                if try_count < max_tries:
                    try_count += 1
                    LOGGER.info("Retry service %s.", fun)
                    continue
            raise
    return result


SERVERCACHE = {}


def get_server(address):
    """
    Cached method to retrieve osa.Client from adress.
    Timeout is implemented.
    Examples:
        >>> import w7x
        >>> from w7x.simulation.backends.web_service import get_server
        >>> addr = w7x.config.get_option("flt.web_service", "server")
        >>> addr in str(get_server(addr))
        True

    """
    if address in SERVERCACHE:
        return SERVERCACHE[address]

    server = None
    try:
        server = run_service(osa.Client, address, max_tries=1, max_time=1)
    except Exception:  # pylint: disable=broad-except
        LOGGER.error("Server at %s could not connect.", address)
    SERVERCACHE[address] = server
    return server


def get_ws_class(ws_server, ws_class):
    """
    Args:
        ws_server (str): address of webservice
        ws_class (str): name of webService type class

    Returns:
        server.types.ws_class
    """
    server = get_server(ws_server)
    return getattr(server.types, ws_class)


class OsaType(rna.polymorphism.Storable):
    """
    Base class wrapping osa types.

    Static Attrs:
        prop_defaults (dict): keys are attributes and values default values
        prop_order (list): order of osa type attributes. *args in __init__ are
            interpreted in this order
        ws_server (str): address of web service
        ws_class (type): osa type to be wrapped by this class. If this is not
            not set or None, it will default to ws_server.types.<cls.__name__>
        ws_class_args (list): args for instantiating ws_class object
        ws_class_kwargs (dict): kwargs for instantiating ws_class object
    """

    prop_defaults = None
    prop_order = None

    ws_server = None
    ws_class = None
    ws_class_args = None
    ws_class_kwargs = None

    def __init__(self, *args, **kwargs):
        self.prop_defaults = self.prop_defaults or {}
        self.prop_order = self.prop_order or []

        if len(args) == 1 and isinstance(
            args[0], (self.__class__, self.__class__.get_ws_class())
        ):
            # copy constructor from cls or related ws class
            other = args[0]
            if isinstance(other, self.get_ws_class()):
                for attr in self.prop_attrs():
                    if hasattr(other, attr):
                        kwargs[attr] = getattr(other, attr)
            else:
                kwargs = other.prop_dict(kwargs)
            if len(args) > 1:
                raise ValueError("More than one argument given in copy " "constructor.")
        else:
            # update kwargs with arguments defined in args
            for attr, arg in zip(self.prop_order, args):
                if attr in kwargs:
                    raise AttributeError(
                        "Attribute {attr} specified in args "
                        "and kwargs! I will use args!".format(**locals())
                    )
                kwargs[attr] = arg

        # default properties
        props = self.prop_dict()
        props.update(self.prop_defaults)
        # set attributes from kwargs or props
        for key, default in props.items():
            val = kwargs.pop(key, default)
            setattr(self, key, val)

        if len(kwargs) > 0:
            raise AttributeError("kwargs have unused arguments %s" % kwargs.keys())

    def prop_attrs(self):
        """
        Returns:
            list of str: properties that are occuring in the osa type input
        """
        try:
            attrs = dir(self.get_ws_class())
        except Exception:  # pylint: disable=broad-except
            LOGGER.warning(
                "could not connect to server and thus not dynamically "
                "get the property defaults."
            )
            if self.prop_defaults is not None:
                attrs = self.prop_defaults.keys()

        prop_attrs = []
        for attr in attrs:
            if attr.startswith("_"):
                continue
            if attr in ["from_file", "from_xml", "to_file", "to_xml"]:
                continue
            prop_attrs.append(attr)
        return prop_attrs

    def prop_dict(self, kwargs=None):
        """
        Dictionary of all properties, updating kwargs
        """
        kwargs = kwargs or {}
        for key in self.prop_attrs():
            kwargs[key] = getattr(self, key, None)
        return kwargs

    def __deepcopy__(self, memo):
        """
        copy with the copy constructor
        """
        kwargs = copy.deepcopy(self.prop_dict(), memo)
        return self.__class__(**kwargs)

    def copy(self):
        """
        copy with deepcopy
        """
        return copy.deepcopy(self)

    @classmethod
    def get_ws_class(cls):
        """
        Returns the osa class version of this class
        """
        ws_class = cls.ws_class or cls.__name__
        return get_ws_class(cls.ws_server, ws_class)

    def to_file(self, path):
        """
        Forward to xml.to_file(self, path)
        Examples:
            >>> from w7x.simulation.backends.web_service import to_osa_type
            >>> from w7x.simulation.backends.web_service.flt import MagneticConfig
            >>> import w7x
            >>> state = w7x.State(w7x.config.CoilSets.Ideal())
            >>> mc = MagneticConfig.from_state(state)
            >>> mc.to_file('/tmp/mc.xlm')
            >>> mc_loaded = MagneticConfig.from_file('/tmp/mc.xlm')
            >>> to_osa_type(mc) == to_osa_type(mc_loaded)
            True

        """
        self.as_input().to_file(rna.path.resolve(path))

    @classmethod
    def from_file(cls, path: str):
        """
        Load from path
        """
        return cls(cls.get_ws_class().from_file(rna.path.resolve(path)))

    def _save_xml(self, path):
        """
        Alias for to_file
        """
        path = rna.path.resolve(path)
        rna.path.mkdir(path)
        self.to_file(path)

    @classmethod
    def _load_xml(cls, path):
        """
        Alias for from_file
        """
        return cls.from_file(rna.path.resolve(path))

    def as_input(self):
        """
        return copy in get_ws_class format. Chain this to the attributes.
        """
        cls = self.get_ws_class()
        ws_class_args = self.ws_class_args or []
        ws_class_kwargs = self.ws_class_kwargs or {}
        instance = cls(*ws_class_args, **ws_class_kwargs)
        for (prop, default) in self.prop_defaults.items():
            value = self.__dict__.get(prop, default)
            if value is not None:
                if issubclass(value.__class__, OsaType) or hasattr(value, "as_input"):
                    value = value.as_input()
                elif hasattr(value, "__iter__") and not isinstance(value, string_types):
                    value = [
                        v.as_input() if hasattr(v, "as_input") else v for v in value
                    ]
                setattr(instance, prop, value)
        return instance


class OsaTypePoints3D(tfields.Points3D, OsaType):  # pylint: disable=too-many-ancestors
    """Imitation of the field_line_server Points3D Type.
    Inheriting from tfield.Points3D so the coordinate system is tracked and
    coordinate transformations are inherently possible

    Args:
        many ways to initialize:
        1.
            like tfields.Points3D
        2.
            points3D (osa.Points3D): copyConstructor
        3.
            pointsList (list): list of triples in varioues formats
    """

    def __new__(cls, tensors, *args, **kwargs):
        if isinstance(tensors, cls.get_ws_class()):
            tensors = np.array([tensors.x1, tensors.x2, tensors.x3]).T
        obj = tfields.Points3D.__new__(cls, tensors, *args, **kwargs)
        return obj

    def __init__(self, *args, **kwargs):
        for attr in self.__slots__:
            kwargs.pop(attr, None)
        super().__init__(self, *args, **kwargs)

    def as_input(self):
        """
        return field_line_server type copy of self
        """
        raw_points = self.get_ws_class()()
        raw_points.x1 = list(self[:, 0])
        raw_points.x2 = list(self[:, 1])
        raw_points.x3 = list(self[:, 2])
        return raw_points


def points_to_osa_type(points3d, ws_server):
    """
    Convert a Points3D object to osa_type.
    """

    points = get_ws_class(ws_server, "Points3D")()

    points.x1 = list(points3d[:, 0])
    points.x2 = list(points3d[:, 1])
    points.x3 = list(points3d[:, 2])

    return points


def profile_to_osa_type(
    profile: w7x.lib.profiles.Profile,
    ws_server: str = None,
    kind: str = "pressure",
    num_locations: int = None,
):
    """
    Convert a Profile to osa_type.

    Args:
        profile: a generic profile.
        kind: wether the profile represents pressure, current or current density.
        num_locations: number of locations to use. It has to be supported by the profile.
    """

    profile_class = profile.__class__.__name__

    vmec_profile = get_ws_class(ws_server, "Profile")()
    vmec_profile.ProfileType = get_vmec_profile_type(profile, kind)

    if profile_class in ["PowerSeries", "TwoPower", "SumAtan"]:
        vmec_profile.coefficients = list(profile.coefficients)
        return vmec_profile

    if profile_class == "CubicSpline":
        if num_locations:
            vmec_profile.locations = list(
                np.linspace(profile.domain[0], profile.domain[-1], num_locations)
            )
            vmec_profile.coefficients = list(profile(vmec_profile.locations))
        else:
            vmec_profile.locations = list(profile.domain)
            vmec_profile.coefficients = list(profile.coefficients)

        return vmec_profile

    raise ValueError(f"Conversion of a {profile_class} not implemeted.")


def fourier_series_to_osa_type(series, ws_server):
    """
    Convert a Fourier Series to osa_type.
    """

    coef = get_ws_class(ws_server, "FourierCoefficients")()

    coef.coefficients = list(series.coef.flatten())
    coef.poloidalModeNumbers = series.poloidal_modes
    coef.toroidalModeNumbers = series.toroidal_modes
    coef.numRadialPoints = series.num_radial_locations

    return coef


def tensor_series_to_osa_type(tensor, ws_server):
    """
    Convert a Tensor Series to osa_type.
    """

    if tensor.ndim != 2:
        raise ValueError("Input tensor series dimensions must be 2")

    surf = get_ws_class(ws_server, "surfaceCoefficients")()

    if tensor.dims[0].cos is not None:
        surf.RCos = fourier_series_to_osa_type(tensor.dims[0].cos, ws_server=ws_server)

    if tensor.dims[0].sin is not None:
        surf.RSin = fourier_series_to_osa_type(tensor.dims[0].sin, ws_server=ws_server)

    if tensor.dims[1].cos is not None:
        surf.ZCos = fourier_series_to_osa_type(tensor.dims[1].cos, ws_server=ws_server)

    if tensor.dims[1].sin is not None:
        surf.ZSin = fourier_series_to_osa_type(tensor.dims[1].sin, ws_server=ws_server)

    return surf


def vmec_input_to_osa_type(vmec_input, ws_server):
    """
    Convert a Vmec input object to osa_type.
    """

    if (
        vmec_input.toroidal_current_profile is not None
        and vmec_input.iota_profile is not None
    ):
        raise RuntimeError(
            "Either a toroidalCurrentProfile or a iotaProfile has to be set"
        )

    osa_input = get_ws_class(ws_server, "VmecInput")(1)

    osa_input.coilCurrents = vmec_input.coil_currents
    osa_input.mgridFile = vmec_input.mgrid_path
    osa_input.freeBoundary = vmec_input.free_boundary

    #  Fix for magnetic axis.
    # rcos = Cos(coef=vmec_input.magnetic_axis.dims[0].cos.truncated(m=0, n=1))
    # zsin = Sin(coef=vmec_input.magnetic_axis.dims[1].sin.truncated(m=0, n=1))
    # magnetic_axis = TensorSeries(Fourier(cos=rcos), Fourier(sin=zsin))
    osa_input.magneticAxis = to_osa_type(vmec_input.magnetic_axis, ws_server=ws_server)
    osa_input.boundary = to_osa_type(vmec_input.boundary, ws_server=ws_server)

    osa_input.pressureProfile = to_osa_type(
        vmec_input.pressure_profile,
        ws_server=ws_server,
        kind="pressure",
    )
    osa_input.pressureScale = vmec_input.pressure_scale

    if vmec_input.toroidal_current_profile is not None:
        osa_input.toroidalCurrentProfile = to_osa_type(
            vmec_input.toroidal_current_profile,
            ws_server=ws_server,
            kind="current",
        )
    osa_input.totalToroidalCurrent = vmec_input.total_toroidal_current

    if vmec_input.iota_profile is not None:
        osa_input.iotaProfile = to_osa_type(
            vmec_input.iota_profile, ws_server=ws_server, kind="iota"
        )

    osa_input.numFieldPeriods = vmec_input.num_field_periods
    osa_input.forceToleranceLevels = vmec_input.force_tolerance_levels
    osa_input.gamma = vmec_input.gamma
    osa_input.intervalConvergenceOutput = vmec_input.num_step
    osa_input.intervalFullVacuumCalculation = vmec_input.num_vac_skip
    osa_input.maxIterationsPerSequence = vmec_input.num_iter
    osa_input.maxToroidalMagneticFlux = vmec_input.phi_edge
    osa_input.numGridPointsRadial = vmec_input.num_grid_points_radial
    osa_input.numGridPointsPoloidal = vmec_input.num_grid_points_poloidal
    osa_input.numGridPointsToroidal = vmec_input.num_grid_points_toroidal
    osa_input.numModesPoloidal = vmec_input.num_modes_poloidal
    osa_input.numModesToroidal = vmec_input.num_modes_toroidal
    osa_input.tcon0 = vmec_input.tcon0
    osa_input.timeStep = vmec_input.time_step

    return osa_input


def to_osa_type(obj, **kwargs):
    """
    Convert obj to osa_type
    """

    if hasattr(obj, "as_input"):
        return obj.as_input()

    ws_server = kwargs.pop("ws_server", None)
    assert ws_server is not None

    if isinstance(obj, tfields.Points3D) or (
        isinstance(obj, tfields.Tensors) and obj.dim == 3
    ):
        return points_to_osa_type(obj, ws_server)

    if isinstance(obj, w7x.lib.profiles.Profile):
        return profile_to_osa_type(obj, ws_server, **kwargs)

    if isinstance(obj, w7x.lib.equilibrium.FourierTerm):
        return fourier_series_to_osa_type(obj, ws_server)

    if isinstance(obj, w7x.lib.equilibrium.TensorSeries):
        return tensor_series_to_osa_type(obj, ws_server)

    if isinstance(obj, w7x.simulation.vmec.VmecInput):
        return vmec_input_to_osa_type(obj, ws_server)

    raise NotImplementedError(obj, ws_server)


def to_tfields_type(obj, *args, **kwargs):
    """
    Convert object to tfields primitive
    """
    if isinstance(obj, tfields.core.AbstractObject):
        return obj
    if hasattr(obj, "x1"):
        tensors = np.array([obj.x1, obj.x2, obj.x3]).T
        obj = tfields.Points3D(tensors, *args, **kwargs)
        return obj
    raise NotImplementedError(
        f"Conversion from {type(obj)} to tfields type not implemented."
    )


if __name__ == "__main__":
    import doctest

    doctest.testmod()
