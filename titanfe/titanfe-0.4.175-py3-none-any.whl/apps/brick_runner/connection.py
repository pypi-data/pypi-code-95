#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Connection objects and its methods: Buffer, Mapping.."""

# pylint: disable=too-few-public-methods

from abc import ABC, abstractmethod

from collections.abc import MutableMapping, Mapping

from ujotypes import UjoStringUTF8, UjoMap, UjoBase, UjoList, UjoNone

from titanfe.ujo_helper import get_ujo_value, python_to_ujo

CONST = "constant"
BUFFER = "buffer"
OBJECT = "object"
RECORD = "record"


def get_constant(constant):
    """get a constant as a class based on the constants type"""
    if constant["type"] == OBJECT:
        return ObjectConstant(constant)
    if constant["type"] == RECORD:
        return RecordConstant(constant)
    return BasicConstant(constant)


class Rule:
    """A mapping rule"""

    def __init__(self, rule):
        self.source = rule["type"]
        self.source_fields, self.target_fields = (
            rule["source_fields"][1:],
            rule["target_fields"][1:],
        )
        self.buffer_id = rule["buffer_id"]
        if self.source == CONST:
            self.constant = get_constant(rule["constant"])

    def __repr__(self):
        return (
            f"Rule(source={self.source}, source_fields={self.source_fields}, "
            f"target_fields={self.target_fields},  buffer_id={self.buffer_id} "
        )

    @property
    def is_const(self):
        return self.source == CONST

    @property
    def is_buffer(self):
        return self.source == BUFFER


class Constant(ABC):
    """A constant"""

    def __init__(self, constant):
        self.name = constant["name"]
        self.type = constant["type"]
        self.value = constant["value"]

    @abstractmethod
    def to_ujo(self):
        """convert the constants value to ujo"""


class BasicConstant(Constant):
    """A constant of a basic type"""

    def to_ujo(self):
        """convert the constants value to ujo"""
        return get_ujo_value(self.value, self.type)


class ObjectConstant(Constant):
    """A constant of type object"""

    def __init__(self, constant):
        super().__init__(constant)
        self.elements = [get_constant(element) for element in constant["elements"]]

    def to_ujo(self):
        """convert the constants value to ujo"""
        ujomap = UjoMap()
        ujoitems = ((ensure_ujo_key(element.name), element.to_ujo()) for element in self.elements)
        for ujokey, ujoval in ujoitems:
            ujomap[ujokey] = ujoval
        return ujomap


class RecordConstant(Constant):
    """A constant of type record"""

    def __init__(self, constant):
        super().__init__(constant)
        self.elements = [get_constant(element) for element in constant["elements"]]

    def to_ujo(self):
        """convert the constants value to ujo"""
        ujolist = UjoList()
        for ujoval in (element.to_ujo() for element in self.elements):
            ujolist.append(ujoval)
        return ujolist


class MappingRules:
    """A connections mapping rules"""

    def __init__(self, rules):
        self.rules = [Rule(rule) for rule in rules]

    def apply(self, buffer, source, target):
        """"convert ujo types according to its mapping rules"""
        for rule in self.rules:
            if rule.is_const:
                try:
                    source_field = rule.constant.to_ujo()
                except (ValueError, TypeError) as error:
                    raise TypeError(
                        f"Failed to convert constant to UJO "
                        f"{rule.constant.value, rule.constant.type}: {error}"
                    )
            else:
                if rule.is_buffer:
                    source_field = buffer[UjoStringUTF8(rule.buffer_id)]
                else:
                    source_field = source

                for field in rule.source_fields:
                    source_field = source_field[UjoStringUTF8(field)]

            if not rule.target_fields:
                return source_field

            target_field = target
            *target_fields, last_target_field = rule.target_fields
            for field in target_fields:
                try:
                    if isinstance(target_field[UjoStringUTF8(field)], UjoNone):
                        target_field[UjoStringUTF8(field)] = UjoMap()
                    target_field = target_field[UjoStringUTF8(field)]
                except KeyError:
                    target_field[UjoStringUTF8(field)] = UjoMap()
                    target_field = target_field[UjoStringUTF8(field)]

            target_field[UjoStringUTF8(last_target_field)] = source_field

        return target


class BufferDescription(Mapping):
    """A connections description of a buffer object"""

    def __init__(self, description_dict):
        self._elements = {}
        for elementid, source in description_dict.items():
            self._elements[elementid] = source["source"]

    def __getitem__(self, key):
        return self._elements.__getitem__(key)

    def __iter__(self):
        return iter(self._elements)

    def __len__(self):
        return len(self._elements)

    def __repr__(self):
        return f"BufferDescription({self._elements!r})"


def ensure_ujo_key(key):
    if not isinstance(key, UjoBase):
        key = UjoStringUTF8(key)
    return key


class Buffer(MutableMapping):
    """A connections buffer of memorized upstream values"""

    def __init__(self, ujoBuffer=None):
        if ujoBuffer is None:
            ujoBuffer = UjoMap()
        self._elements = ujoBuffer

    def __repr__(self):
        return f"Buffer({self._elements!r})"

    def __getitem__(self, key):
        return self._elements.__getitem__(ensure_ujo_key(key))

    def __iter__(self):
        return iter(self._elements)

    def __len__(self):
        return len(self._elements)

    def __eq__(self, other):
        if not isinstance(other, (Buffer, UjoMap)):
            return False
        if isinstance(other, UjoMap):
            return self._elements == other  # pylint: disable=protected-access
        return self._elements == other._elements  # pylint: disable=protected-access

    def __setitem__(self, key, value):
        return self._elements.__setitem__(ensure_ujo_key(key), value)

    def __delitem__(self, key):
        return self._elements.__delitem__(ensure_ujo_key(key))

    @classmethod
    def from_dict(cls, buffer_dict):
        return cls(python_to_ujo(buffer_dict))

    def update_from_result(self, result, buffer_description):
        """update the buffer using the information given
        in the buffer_description"""
        for key in self:
            if key.value not in buffer_description:
                del self[key]

        for element_id, source_fields in buffer_description.items():
            if not source_fields:
                continue  # should already exist
            source = result
            _, *source_fields = source_fields  # remove leading typename
            for field in source_fields:
                source = source[UjoStringUTF8(field)]
            self[element_id] = source
