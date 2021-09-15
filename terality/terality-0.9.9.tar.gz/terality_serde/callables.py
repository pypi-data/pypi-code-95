from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import pickle
import sys

import cloudpickle

from . import SerdeMixin


@dataclass
class CallableWrapper(SerdeMixin):
    """Represent a user-supplied callable. THIS OBJECT CAN BE UNSAFE, READ THE DOCS!"""

    pickled_payload: bytes

    @classmethod
    def from_object(cls, obj: Callable) -> CallableWrapper:
        """Serialize the provided callable to a CallableWrapper.

        Internally, this uses the `cloudpickle` package and has the same limitations.

        Deserializing (even without running) such a serialized object can run arbitrary code.
        Only deserialize this in a safe sandboxed environment.
        """
        if isinstance(obj, type):
            # types are callable, but we don't support serializing them in this class
            raise TypeError("'obj' must not be a type")

        module_obj = None
        if hasattr(obj, "__module__") and obj.__module__ is not None:
            if obj.__module__ not in sys.modules:
                raise ValueError(
                    f"The provided callable module is '{obj.__module__}', but it does not seem to be imported (not present in sys.modules). "
                    "Import this module in this Python session to be able to serialize this callable."
                )

            module_obj = sys.modules[obj.__module__]
            cloudpickle.register_pickle_by_value(module_obj)  # type: ignore

        try:
            return cls(pickled_payload=cloudpickle.dumps(obj))  # type: ignore
        finally:
            if module_obj is not None:
                cloudpickle.unregister_pickle_by_value(module_obj)  # type: ignore

    def to_callable(self) -> Callable:
        """Return the deserialized callable. This function can run arbitrary user-supplied code and must only be run in a secure sandbox."""
        try:
            return pickle.loads(self.pickled_payload)
        except ModuleNotFoundError as e:
            raise ValueError(
                f"Can not deserialize this function, as it depends on a module not available in this execution environment: {str(e)}"
            ) from e
