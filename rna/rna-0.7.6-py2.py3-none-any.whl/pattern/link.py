import typing
from rna.pattern.switch import Switch


NOTSET = object()


class exposed(Switch):
    """
    This switch is related to the Linker pattern and - if enabled - exposes the Link behind
    a Linker attribute.
    """

    ENABLED = False


class Reference:
    def __init__(self, references=None):
        if references is None:
            references = []
        self._references = references


class Link:
    """
    Base class of an attribute in the Linker class that acts as a symlink to a reference.

    Args:
        value: value of the attribute.
        ref: reference containing the value
        fget: callable, following fget(ref) -> value
        cache: if true, store the value after fget and return the stored value after that.
    """

    def __init__(
        self,
        ref: typing.Optional[typing.Union[Reference, any]] = None,
        fget: typing.Callable = None,
        value: typing.Any = NOTSET,
        cache=False,
    ):
        self.value = value
        self.ref = ref
        self.fget = fget
        self.cache = cache
        if value is NOTSET:
            assert ref is not None
            assert fget is not None


class Linker:
    """
    Linkers are handling the attribute acces of Links by __getattribute__.
    Linker attributes reveal the ref with the exposed switch set to True

    Examples:
        >>> import dataclasses
        >>> from rna.pattern.link import Linker, Link, Reference

        >>> @dataclasses.dataclass
        ... class Wout(Reference):
        ...     path: str = None
        ...     data_1: any = None
        ...     data_2: any = None
        ...
        ...     def __post_init__(self):
        ...         super().__init__()

        >>> wout = Wout(path="wout_asdf.nc", data_1=21, data_2=42)

        >>> @dataclasses.dataclass
        ... class Equilibrium(Linker):
        ...     data_1: typing.Union[Link, float] = Link(
        ...         ref=wout, fget=lambda wo: wo.data_1
        ...     )
        ...     data_2: typing.Union[Link, float] = Link(
        ...         ref=wout, fget=lambda wo: wo.data_2
        ...     )
        ...     flux_surfaces: typing.Union[Link, float] = Link(value=None)
        ...     dummy: any = "any value"

        >>> equi_explicit = Equilibrium(flux_surfaces=42)
        >>> assert equi_explicit.flux_surfaces == 42

        >>> equi = Equilibrium(
        ...     flux_surfaces=Link(
        ...         "./flux_surfaces_123.txt -> 123",
        ...         lambda ref: int(ref[-3:])
        ...     )
        ... )
        >>> assert equi.flux_surfaces == 123

        Linker attributes reveal the ref with the exposed switch set to True
        >>> with exposed(True):
        ...     assert "./flux_surfaces" in equi.flux_surfaces.ref
        >>> assert equi.flux_surfaces == 123

        You can also use the 'get_link' method to do the same
        >>> assert equi.data_2 == 42
        >>> link = equi.get_link("data_2")
        >>> assert link.ref is wout

        Or in short use the 'get_ref' method to directly access the reference
        >>> ref = equi.get_ref("data_2")
        >>> assert ref is wout

        It returns None if no Link instance is found
        >>> assert equi.get_link("dummy") is None
        >>> equi.dummy
        'any value'

        You can ask for multiple attributes and it will return the first valid
        >>> link = equi.get_link("dummy", "data_2", "data_1")
        >>> assert link.fget(link.ref) == 42  # data_2 getter ref was returned

        You can find all references to the wget ref by the _references attribute.
        This is only possible, if the referenced object has is an instance of Reference.
        >>> assert isinstance(wout, Reference)

        The first two entries in _references stam from equi_explicit, the last two from equi
        >>> assert wout._references[2][0] is equi
        >>> assert wout._references[2][1] == "data_1"
        >>> assert wout._references[3][0] is equi
        >>> assert wout._references[3][1] == "data_2"

        The cache attribute allows to - if true - store the call value of fget (at the expense
        of not being up to date with the ref). -> Only use the cache=True value if you are
        sure that the reference object will never change the referred value.
        >>> equi_cached = Equilibrium(
        ...     data_2=Link(
        ...         ref=wout, fget=lambda wo: wo.data_2, cache=True
        ...     )
        ... )
        >>> assert equi_cached.data_2 == 42
        >>> wout.data_2 = 12
        >>> assert equi_cached.data_2 == 42
        >>> assert equi.data_2 == 12
    """

    def __getattribute__(self, name):
        val = super().__getattribute__(name)
        if isinstance(val, Link):
            if exposed.enabled():
                return val
            if not val.cache or val.value is NOTSET:
                value = val.fget(val.ref)
                if val.cache:
                    val.value = value
            else:
                value = val.value
            return value
        return val

    def __setattr__(self, name, val):
        if isinstance(val, Link):
            if isinstance(val.ref, Reference):
                val.ref._references.append((self, name))
        super().__setattr__(name, val)

    def get_link(self, *attribute_names):
        """
        Returns:
            first Link object found under attribute_names
        """
        link = None
        with exposed(True):
            for name in attribute_names:
                val = getattr(self, name)
                if isinstance(val, Link):
                    link = val
                    break
        return link

    def get_ref(self, *attribute_names):
        """
        Returns:
            reference of first Link found under attribute_names
        """
        link = self.get_link(*attribute_names)
        if link is not None:
            return link.ref
        return None
