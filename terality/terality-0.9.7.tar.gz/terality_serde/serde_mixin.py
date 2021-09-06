from __future__ import annotations
import base64
from enum import Enum
import re
import zlib
import inspect
import json
import sys
from typing import Any, Dict, Optional, Type, Union

from . import TeralitySerializationError, all_external_types, external_base_classes


class SerdeMixin:
    subclasses = []  # type: ignore

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @classmethod
    def _cached_properties_names(cls):
        from functools import cached_property

        return {k for k, v in inspect.getmembers(cls) if isinstance(v, cached_property)} | {
            # betterproto internal fields
            "_unknown_fields",
            "_serialized_on_wire",
            "_group_map",
        }

    @property
    def dict(self) -> Dict:
        if sys.version_info[1] >= 8:
            dict_ = {
                k: v for k, v in self.__dict__.items() if k not in self._cached_properties_names()
            }
        else:
            dict_ = dict(self.__dict__)
        return dict_

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)


class SerializableEnum(SerdeMixin, Enum):
    """An Enum that is also serializable.

    Usage:
    >>> class MySerializableEnum(SerializableEnum):
            VARIANT_1 = "VARIANT_1"
            VARIANT_2 = "VARIANT_2"
    """

    @property
    def dict(self) -> Dict:
        dict_ = {"name": self.name}
        return dict_

    @classmethod
    def from_dict(cls, name: str) -> SerializableEnum:  # type: ignore
        return cls[name]


class _SerdeConfig:
    """Store the known serialized and deserializer for various types, and apply them to objects.

    This class is immutable and a single instance can be reused.  For performance reasons, do not instantiate
    this class in tight loops.

    Note: the naming of this class implies that it's only configuration, but it actually contains business
    logic. Additionally, the naming of methods and attributes is all over the place ("serializers" are actually "encoders").
    Cleaning that up is TODO.
    """

    def __init__(self):
        self._internal_type_attribute = "!terality:internal_type"
        self._external_type_attribute = "!terality:external_type"
        self._external_types = all_external_types
        self._external_base_types = external_base_classes
        self._external_types_to_serializer = {ex.class_: ex for ex in all_external_types}
        self._external_type_names_to_deserializer = {
            ex.class_name: ex for ex in self._external_types + self._external_base_types
        }
        self._internal_types_cached = None

    def encode(self, obj: Any) -> Union[dict, Any]:
        """
        Encode an Python object to a JSON-serializable value.

        Objects of known types (types with a registered serializer) will be encoded to a dict.
        Objects of types that are already JSON-serializable and types without any registered serializer will be returned
        as-it.

        To fully encode an object to a JSON-serializable value, this function needs to be called recursively
        on any dicts or lists returned by this function (see `serialize`).
        """

        if isinstance(obj, SerdeMixin):
            dict_ = obj.dict
            dict_[self._internal_type_attribute] = obj.class_name
            return dict_

        type_ = type(obj)

        if type_ in self._external_types_to_serializer:
            if isinstance(obj, dict) and all((isinstance(key, str) for key in obj.keys())):
                return obj

            external_type = self._external_types_to_serializer[type_]
            dict_ = external_type.to_json(obj)
            dict_[self._external_type_attribute] = external_type.class_name
            return dict_

        for base_class in self._external_base_types:
            if issubclass(type_, base_class.class_):
                dict_ = base_class.to_json(obj)
                dict_[self._external_type_attribute] = base_class.class_name
                return dict_

        return obj

    def encode_recursively(self, obj):
        """Try to return a JSON-serializable representation of this object.

        Calls `encode` recursively. If no unknown types are encountered, the result is a JSON-serializable list, dict
        or scalar.

        Complex types will be encoded as dicts (see `encode`), then `encode` will be called recursively on the keys and
        values of the resulting dictionary (this allows encoding collections of arbitrary objects).

        The result of this function may not be JSON-serializable if this recursive process encounters types
        without any registered serializer.
        """
        encoded = self.encode(obj)

        if isinstance(encoded, list):
            return [self.encode_recursively(elt) for elt in encoded]
        if isinstance(encoded, dict):
            return {
                self.encode_recursively(k): self.encode_recursively(v) for k, v in encoded.items()
            }
        return encoded

    @property
    def _internal_types(self) -> Dict[str, Type[SerdeMixin]]:
        # Put in a property so that it gets computed at runtime at the last minute before it is needed
        # We do this because the problem of the subclasses registration is that it only happens if the subclass gets
        # imported in an __init__ somewhere, so we compute this function at the latest moment to give a chance for
        # the subclasses to have be imported
        if self._internal_types_cached is None:
            self._internal_types_cached = {
                internal.__name__: internal for internal in SerdeMixin.subclasses
            }
        return self._internal_types_cached

    def decode(self, encoded: Dict[str, Any]):
        """Reverse of `encode`. Call this as `json.loads(object_hook=SerdeConfig().decode)`.

        Mutate `obj`.
        """
        if self._internal_type_attribute in encoded:
            internal_type_name = encoded.pop(self._internal_type_attribute)
            internal_type = self._internal_types[internal_type_name]
            return internal_type.from_dict(**encoded)
        if self._external_type_attribute in encoded:
            external_type_name = encoded.pop(self._external_type_attribute)
            deserializer = self._external_type_names_to_deserializer[external_type_name]
            return deserializer.from_json(**encoded)
        return encoded


_SERDE_CONFIG = _SerdeConfig()


# pylint: disable=invalid-name
def dumps(o: Any, compressed: bool = False) -> str:
    o = _SERDE_CONFIG.encode_recursively(o)
    try:
        result = json.dumps(o)
    except TypeError as e:
        unserializable_type = _parse_json_type_error(e)
        if unserializable_type is not None:
            raise TeralitySerializationError(
                f"Can not serialize an object with a type of '{unserializable_type}' (or a collection or object containing such a type)",
                unserializable_type=unserializable_type,
            ) from e
        raise TeralitySerializationError(
            "Couldn't serialize the provided Python object: {str(e)}"
        ) from e
    if compressed:
        result = base64.encodebytes(zlib.compress(result.encode("utf-8"))).decode("utf-8")
    return result


# pylint: disable=invalid-name
def loads(
    s: str,
    compressed: bool = False,
) -> Any:
    if compressed:
        s = zlib.decompress(base64.decodebytes(s.encode("utf-8"))).decode("utf-8")
    return json.loads(s, object_hook=_SERDE_CONFIG.decode)


def _parse_json_type_error(e: TypeError) -> Optional[str]:
    """Return the unserializable type that caused the JSON module to throw an error.

    The exception message should look like: "Object of type xxx is not JSON serializable".

    Returns None is the exception message could not be parsed.
    """
    if len(e.args) != 1 or not isinstance(e.args[0], str):
        return None
    message = e.args[0]
    match = re.compile(r"^Object of type (.*) is not JSON serializable$").match(message)
    if match is None:
        return None
    return match.group(1)
