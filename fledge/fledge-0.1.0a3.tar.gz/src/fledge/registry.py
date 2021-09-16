"""Registry."""
# flake8: noqa
# TODO: re-add to flake8
from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import TypeVar
from typing import Union
from weakref import WeakValueDictionary

from .named import Named


SN = TypeVar("SN", bound="Named")


def _get_name(name_or_item: Union[str, Named]) -> str:
    if isinstance(name_or_item, str):
        return name_or_item
    if isinstance(name_or_item, Named):
        return name_or_item.name
    else:
        raise TypeError(f"invalid name or item: {name_or_item}")


class Registry(WeakValueDictionary, Mapping[str, Named]):
    """A registry of named objects."""

    def add(self, item: Named) -> None:
        if not isinstance(item, Named):
            raise TypeError("Registries must contain Named object")
        if super(Registry, self).__contains__(item.name):
            raise RuntimeError(f'name "{item.name}" already in use by {self[item.name]}')
        super(Registry, self).__setitem__(item.name, item)

    def remove(self, item: Union[str, Named]) -> None:
        if not isinstance(item, (str, Named)):
            raise TypeError
        name = _get_name(item)
        super(Registry, self).__delitem__(name)

    def __contains__(self, item: Any) -> bool:
        if not isinstance(item, (str, Named)):
            return False
        name = _get_name(item)
        return super(Registry, self).__contains__(name)

    def __getitem__(self, name_or_item: Union[str, Named]) -> SN:
        name = _get_name(name_or_item)
        return super(Registry, self).__getitem__(name)

    def __setitem__(self, name, item):
        raise NotImplementedError("use Registry.add(named_item)")
