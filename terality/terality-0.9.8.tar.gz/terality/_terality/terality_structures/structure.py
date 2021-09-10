from dataclasses import dataclass, field
from functools import partial, partialmethod
import sys
from typing import Any, Set, Callable, Optional, Iterable

# noinspection PyProtectedMember
from pandas._libs.properties import AxisProperty, CachedProperty

from . import call_pandas_function


# WARNING: `sys.gettrace` is considered a CPython implementation detail, so we check that it's available.
# See [documentation](https://docs.python.org/3.8/library/sys.html?highlight=gettrace#sys.gettrace).
# CTRacer is excluded because it is not a debugger but a code coverage tool.
_process_is_being_debugged: bool = (
    hasattr(sys, "gettrace")
    and sys.gettrace() is not None
    and sys.gettrace().__class__.__name__ != "CTracer"
)


class PandasDisplay:
    min_rows: int = 5
    max_rows: int = 20
    min_cols: int = 5
    max_cols: int = 20


class ClassMethod(type):
    """Only to be used for stuff that can't be done directly on yhe class"""

    _class_name: str
    _pandas_class: Any
    _additional_class_methods: Set[str] = {"from_pandas"}

    @classmethod
    def _attr_if_exists(cls, item: str):
        return getattr(cls._pandas_class, item, None)

    def __getattr__(cls, key: str) -> Callable:
        call = partial(call_pandas_function, cls._class_name, None, key)
        if key in cls._additional_class_methods or cls._attr_if_exists(key) is not None:
            return call
        raise ValueError()

    def __dir__(cls) -> Iterable[str]:
        return list(cls._additional_class_methods) + list(dir(cls._pandas_class))


class Struct(metaclass=ClassMethod):
    _pandas_class_instance: Any = None
    _additional_methods: Set[str] = {
        "to_pandas",
        "load",
        "save",
    }  # put in the mcs to get in the dir?
    _accessors: Set[str] = set()  # put in the mcs to get in the dir?
    _indexers = {"iat", "at", "loc", "iloc"}  # put in the mcs to get in the dir?

    @classmethod
    def _is_property(cls, item: str) -> bool:
        property_ = cls._attr_if_exists(item)
        return isinstance(property_, (property, AxisProperty, CachedProperty))  # works for None too

    @classmethod
    def _is_method(cls, item: str) -> bool:
        method = cls._attr_if_exists(item)
        return callable(method)  # works for None too

    @classmethod
    def _call(cls, accessor, func_name, *args, **kwargs):
        return call_pandas_function(cls._class_name, accessor, func_name, *args, **kwargs)

    def _call_method(self, accessor: Optional[str], func_name: str, *args, **kwargs):
        return self._call(accessor, func_name, self, *args, **kwargs)

    def _on_missing_attribute(self, item: str):
        raise AttributeError(f"'{type(self)}' has no attribute {item!r}")

    ###################################################################################################################
    # Creation/upgrade

    @classmethod
    def _new(cls, id_: str, cached_attributes=None):
        # Workaround to avoid being intercepted
        struct = object.__new__(cls)
        struct._id = id_  # pylint: disable=attribute-defined-outside-init
        struct._cached_attributes = (  # pylint: disable=attribute-defined-outside-init
            {} if cached_attributes is None else cached_attributes
        )
        return struct

    def _mutate(self, other: "Struct") -> None:
        self._id = other._id  # type: ignore  # pylint: disable=attribute-defined-outside-init
        self._cached_attributes = (  # pylint: disable=attribute-defined-outside-init
            other._cached_attributes  # type: ignore
        )

    ###################################################################################################################
    # Magic methods

    def __new__(cls, *args, **kwargs):
        return cls._call(None, "__init__", *args, **kwargs)

    def __getattr__(self, item: str):  # pylint: disable=too-many-return-statements
        """Intercepting all not-magic methods"""
        # return partial(self._call_method, None, item, PandasDisplay)
        if item.startswith("_") and item not in ("_repr_html_", "_ipython_display_"):
            return object.__getattribute__(self, item)
        if item in self._cached_attributes:  # type: ignore
            return self._cached_attributes[item]  # type: ignore
        if item in self._accessors:
            return NameSpace(self, item)
        if item in self._indexers:
            return Indexer(self, item)
        if item in self._additional_methods:
            return partial(self._call_method, None, item)
        if self._is_property(item):
            return self._call_method(None, item)
        if self._is_method(item):
            return partial(self._call_method, None, item)
        return self._on_missing_attribute(item)

    def __setattr__(self, name, value):  # pylint: disable=inconsistent-return-statements
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            return self._call_method(None, "__setattr__", name=name, value=value)

    def __str__(self):
        # NOTE: When debugging, we avoid network calls and fall back to a bare bones representation.
        if _process_is_being_debugged:
            _id = getattr(self, "_id", None)
            return f"terality.{self.__class__.__name__}(_id={_id})"
        return self._call_method(None, "__str__")

    def __repr__(self):
        return self.__str__()

    def __dir__(self) -> Iterable[str]:
        # WARNING: When the process is being debugged, we do not want to list any dynamic properties.
        # Why? Because the debugger's variable view uses `dir` to list a variable's children, then evaluates them.
        # Listing dynamic properties would cause spurious calls to the server.
        if _process_is_being_debugged:
            members = [
                key
                for key in self.__dict__.keys() | type(self).__dict__.keys()
                if key.startswith("_") and not key.startswith("__")
            ]
            return members

        members = list(self._additional_methods)
        if self._pandas_class_instance is not None:
            members += list(dir(self._pandas_class_instance))
        return members

    def __len__(self):
        return self._call_method(None, "__len__")


# Add magic methods (otherwise they won't be itercepted) programmatically rather than by hand
# ------------------------------


def _forward_to_backend(lhs: Struct, func_name: str, *args, **kwargs):
    return lhs._call_method(None, func_name, *args, **kwargs)


def _set_magics(magic_method_names):
    for magic_method_name in magic_method_names:
        full_magic_method_name = f"__{magic_method_name}__"
        operator = partialmethod(_forward_to_backend, full_magic_method_name)
        setattr(Struct, full_magic_method_name, operator)


_access = ["getitem", "setitem", "delitem"]
_comparisons = ["lt", "le", "eq", "ne", "ge", "gt"]
_others = ["neg", "pos", "invert", "abs", "len"]
_with_reverse = [
    "add",
    "sub",
    "mul",
    "matmul",
    "floordiv",
    "truediv",
    "pow",
    "mod",
    "divmod",
    "lshift",
    "rshift",
    "and",
    "xor",
    "or",
]
_double = [f"{prefix}{function_name}" for function_name in _with_reverse for prefix in ["", "r"]]


_set_magics(_access + _comparisons + _others + _double)


# Other stuff
# ------------------------------


@dataclass
class NameSpace:
    _obj: Struct
    _name: str

    def __getattr__(self, item: str):
        if item.startswith("_"):
            return object.__getattribute__(self, item)
        pd_class = self._obj.__class__._attr_if_exists(self._name)
        pd_method = getattr(pd_class, item)
        if isinstance(pd_method, property):
            # noinspection PyProtectedMember
            return self._obj._call_method(self._name, item)
        # noinspection PyProtectedMember
        return partial(self._obj._call_method, self._name, item)


@dataclass
class Indexer:
    _obj: Struct
    _name: str

    def __getitem__(self, item):
        # noinspection PyProtectedMember
        return self._obj._call_method(self._name, "__getitem__", item)

    def __setitem__(self, key, value):
        # noinspection PyProtectedMember
        self._obj._call_method(self._name, "__set_item__", key, value)


@dataclass
class StructIterator:
    _struct: Struct
    _pos: int = 0
    _buffer: list = field(default_factory=list)
    _buffer_start: int = 0

    def __iter__(self):
        # Must return itself, as per the [documentation](https://docs.python.org/3.8/library/stdtypes.html#typeiter).
        return self

    @property
    def _buffer_stop(self):
        return self._buffer_start + len(self._buffer)

    def __next__(self) -> Any:
        if self._pos >= self._struct.size:
            raise StopIteration()
        if self._pos >= self._buffer_stop:
            self._buffer_start = self._buffer_stop
            self._buffer = self._struct.get_range_auto(self._buffer_start)
        value = self._buffer[self._pos - self._buffer_start]
        self._pos += 1
        return value
