from copy import copy
from dataclasses import dataclass, is_dataclass
from typing import Dict, List, Tuple, Union

from annotell.openlabel.models.utils.deserialize import deserialize
from annotell.openlabel.models.datatypelist import DataTypeList


def handle_dict(self_attribute: dict, other_attribute: dict) -> dict:
    merged_attribute = {}
    for key, self_nested_attribute in self_attribute.items():
        other_nested_attribute = other_attribute.pop(key, self_nested_attribute.__class__())
        merged_attribute[key] = merge_attributes(self_nested_attribute, other_nested_attribute)
    merged_attribute.update(other_attribute)
    return merged_attribute


def handle_dataclass(self_dc, other_dc) -> dict:
    merged_attributes = {}
    for attribute in self_dc.__dict__:
        self_attribute = getattr(self_dc, attribute)
        other_attribute = getattr(other_dc, attribute)
        merged_attribute = merge_attributes(self_attribute, other_attribute)
        merged_attributes[attribute] = merged_attribute
    return merged_attributes


def merge_attributes(self_attribute, other_attribute):
    if isinstance(self_attribute, dict):
        merged_attribute = handle_dict(self_attribute, other_attribute)
    elif getattr(self_attribute, "__add__", False):
        merged_attribute = self_attribute if other_attribute is None else self_attribute + other_attribute
    else:
        merged_attribute = other_attribute if self_attribute is None else self_attribute.merge_with(other_attribute)
    return merged_attribute


@dataclass
class OpenLabelBase:

    def merge_with(self, other):
        if other is None:
            return self

        assert self.__class__ == other.__class__, "Can't add different datatypes"

        merged_attributes = handle_dataclass(self, other)

        return self.__class__(**merged_attributes)

    @classmethod
    def from_dict(cls, data: dict):
        data = data['openlabel'] if 'openlabel' in data.keys() else data
        return deserialize(data=data, cls=cls)

    def to_dict(self) -> Dict:
        none_types = (None, {}, [], DataTypeList())

        def special_cases(context: List[str]) -> bool:
            """
            There are some special cases where we do not want to strip empty dicts from the OpenLABEL tree.
            An empty {} inside frames->frame->sub-category indicates existance without any properties.
            The example below indicates the existance of the object "foo" in frame "0".
            Example:
                "frames" : {           # level: 1
                    "0": {             # level: 2
                        "objects": {   # level: 3
                            "foo": {}  # level: 4
                        }
                    }
                }
            """
            return len(context) == 4 and \
                   "frames" in context and \
                   any([k in context for k in ["objects", "relations"]])

        def list_stripper(data: List, context: List[str]) -> Tuple[list, List[str]]:
            new_list = []
            for v in data:
                if v:
                    v, context = strip_item(v, copy(context))
                if v not in none_types:
                    new_list.append(v)
            return new_list, context

        def dict_stripper(data, context: List[str]) -> Tuple[dict, List[str]]:
            new_data = {}
            for k, v in data.items():
                context.append(k)
                if v:
                    v, context = strip_item(v, copy(context))
                if v not in none_types or special_cases(context):
                    new_data[k] = v
                context.pop()
            return new_data, context

        def strip_item(v, context: List[str] = None) -> Tuple[Union[list, dict], List[str]]:
            if context is None:
                context = []

            if isinstance(v, dict):
                return dict_stripper(v, context)
            elif isinstance(v, list):
                return list_stripper(v, context)
            elif isinstance(v, DataTypeList):
                return list_stripper(v.__dict__["list"], context)
            elif is_dataclass(v):
                return dict_stripper(v.__dict__, context)

            return v, context

        stripped_dict, _ = dict_stripper(self.__dict__, context=[])
        return stripped_dict
