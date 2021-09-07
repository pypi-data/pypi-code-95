#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""simplify ujo conversions (eventually we'd want to use an UjoScheme instead though)"""

from typing import Sequence, Mapping, Set

from datetime import datetime

from ujotypes import (
    UjoBase,
    UjoBool,
    UjoStringUTF8,
    UjoStringC,
    UjoInt8,
    UjoInt16,
    UjoInt32,
    UjoInt64,
    UjoUInt8,
    UjoUInt16,
    UjoUInt32,
    UjoUInt64,
    UjoFloat16,
    UjoFloat32,
    UjoFloat64,
    UjoList,
    UjoMap,
    UjoTimestamp,
    UJO_VARIANT_NONE,
    ujo_to_python,
)
from ujotypes.variants import write_buffer, read_buffer


def python_to_ujo(py_obj):  # pylint: disable=too-many-return-statements
    """convert python objects recursively into corresponding UJO

    int, float, etc. will be converted to Int64, Float64, etc.
    If you actually want e.g. an Int8 do a manual conversion for that specific item beforehand.
    """
    if isinstance(py_obj, UjoBase):
        return py_obj

    if py_obj is None:
        return UJO_VARIANT_NONE
    if isinstance(py_obj, bool):
        return UjoBool(py_obj)
    if isinstance(py_obj, int):
        return UjoInt64(py_obj)
    if isinstance(py_obj, float):
        return UjoFloat64(py_obj)
    if isinstance(py_obj, str):
        return UjoStringUTF8(py_obj)
    if isinstance(py_obj, datetime):
        return UjoTimestamp(py_obj)

    if isinstance(py_obj, (Sequence, Set)):
        ujolist = UjoList()
        for ujoval in (python_to_ujo(val) for val in py_obj):
            ujolist.append(ujoval)
        return ujolist

    if isinstance(py_obj, Mapping):
        ujomap = UjoMap()
        ujoitems = ((python_to_ujo(key), python_to_ujo(val)) for key, val in py_obj.items())
        for ujokey, ujoval in ujoitems:
            ujomap[ujokey] = ujoval
        return ujomap

    raise NotImplementedError(
        f"TODO: SimplifiedUjo TypeConversion for: {type(py_obj)} ({py_obj!r})"
    )


def ujo_bytes_to_py(bytes_obj):
    ujoobj = read_buffer(bytes_obj)
    return ujo_to_python(ujoobj)


def py_to_ujo_bytes(py_obj):
    if not isinstance(py_obj, (Mapping, Sequence)):
        raise TypeError("can only turn mapping or sequence to ujo bytes")
    ujoobj = python_to_ujo(py_obj)
    return write_buffer(ujoobj)


UJO_TYPES = {
    "int8": UjoInt8,
    "int16": UjoInt16,
    "int32": UjoInt32,
    "int64": UjoInt64,
    "uint8": UjoUInt8,
    "uint16": UjoUInt16,
    "uint32": UjoUInt32,
    "uint64": UjoUInt64,
    "float16": UjoFloat16,
    "float32": UjoFloat32,
    "float64": UjoFloat64,
    "string": UjoStringUTF8,
    "cstring": UjoStringC,
    "bool": lambda x: UjoBool(x.lower() == "true"),
}


def get_ujo_value(value, type_name):
    "get value in ujo based on given type_name and value"
    if "int" in type_name:
        value = int(value)
    if "float" in type_name:
        value = float(value)
    return UJO_TYPES.get(type_name)(value)
