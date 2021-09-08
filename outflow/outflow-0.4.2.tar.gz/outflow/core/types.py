# -*- coding: utf-8 -*-
from typing import Any, Dict, NewType, Union

from typing_extensions import TypedDict


class Skipped:
    pass


TargetOutputs = NewType("TargetOutputs", Union[Dict, None])


class TypedTargetOutputs(TypedDict):
    pass


def outputs_type_factory(type_dict=None, name="TypedTargetOutputs", *args, **kwargs):
    if type_dict is None:
        return TargetOutputs
    else:
        output_type = TypedDict(name, type_dict)
        if len(type_dict) == 1:
            return Union[output_type, next(iter(type_dict.values())), Skipped]
        else:
            return Union[output_type, Skipped]


_outflow_map_iterator_prefix = "_OutflowMapIterator__"


def IterateOn(iterable_target_name, input_type=Any, **kwargs):
    return NewType(
        _outflow_map_iterator_prefix + iterable_target_name,
        kwargs.get("type", input_type),
    )


IterateOn.prefix = _outflow_map_iterator_prefix
