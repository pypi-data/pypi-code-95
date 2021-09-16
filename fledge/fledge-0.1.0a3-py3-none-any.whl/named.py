# flake8: noqa
# TODO: re-add to flake8
from __future__ import annotations

from copy import deepcopy
from typing import Any
from typing import Final
from typing import final
from typing import Optional


def is_named(item: Any) -> bool:
    return issubclass(type(item), Named)


class Named(object):
    """Named objects are uniquely identifiable by their `name` attribute.

    NOTE: this does not preclude objects of different classes from sharing names if the user
    provides them. This is not a problem unless the objects are stored in the same registry, which
    handles that case.

    Args:
        name (Optional[str], optional): name of the instance. If not provided, the name is derived
            from the classname.

    Raises:
        ValueError: if the provided name is already in use by an instance of the same class.

    """

    name: str

    # The instance count is never decremented.
    _instance_count: int = 0

    # Names are removed from this when deleted, allowing for reuse.
    _instance_names: Final[set[str]] = set()

    def __init__(self, name: Optional[str] = None) -> None:
        if name is None:
            self.name = f"{self.__class__.__name__.lower()}_{self.__class__._instance_count}"
        elif name not in self._instance_names:
            self.name = name
        else:
            raise ValueError("cannot reuse name: {}".format(name))

        self.__class__._instance_count += 1

    def __hash__(self) -> int:
        return hash(self.name)

    def __del__(self):
        if self.name in self._instance_names:
            self._instance_names.remove(self.name)

    def rename(self, name: str):
        """Rename the named object.

        Sub-classes may wish to update a registry containing the object.

        """
        if self.name == name:
            return self
        elif name in self._instance_names:
            raise ValueError(f"name already taken: {name}")

        self._instance_names.remove(self.name)
        self._instance_names.add(name)
        self.name = name

    def copy(self, name: Optional[str] = None):
        """Perform a deepcopy, except rename the output to `name`."""
        cls = self.__class__
        out = cls.__new__(cls)
        memo = dict()
        memo[id(self)] = out
        Named.__init__(out, name=name)
        for k, v in self.__dict__.items():
            if k == "name":
                continue
            setattr(out, k, deepcopy(v, memo))
        return out

    def __deepcopy__(self, memo):
        """Deepcopy of a named object should have a new name."""
        cls = self.__class__
        out = cls.__new__(cls)
        memo[id(self)] = out
        Named.__init__(out, name=None)
        for k, v in self.__dict__.items():
            if k == "name":
                continue
            setattr(out, k, deepcopy(v, memo))
        return out
