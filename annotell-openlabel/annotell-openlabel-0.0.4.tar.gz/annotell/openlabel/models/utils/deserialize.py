import inspect
from typing import Any, Dict, List, Type, Union, _GenericAlias
from dataclasses import is_dataclass
import logging

from annotell.openlabel.models.utils.data_type_parsing import get_openlabel_type

logger = logging.getLogger(__name__)

built_in_types = (int, float, bool, str, dict, list)


def deserialize(data: Any, cls: Type):
    return parse_data(data=data, cls=cls)


def parse_data(data: Any, cls: Type):

    if data is None:
        return None
    elif cls in built_in_types:
        return parse_built_in(data)
    elif is_dataclass(cls):
        return parse_dataclass(data, cls)
    elif inspect.isclass(cls):
        return parse_custom_class(data, cls)
    elif isinstance(cls, _GenericAlias):
        return parse_generic_alias(data, cls)
    else:
        raise NotImplementedError(f"object of type {cls} is not implemented yet")


def parse_dataclass(data: Union[Dict, List], cls: Type):
    if isinstance(data, list):
        data_instance = cls()
        for d in data:
            k, v = get_openlabel_type(d["name"], d["val"])
            data_instance.append(v)
        return data_instance

    dataclass_fields = cls.__dataclass_fields__
    params = {}
    for name, value in data.items():
        if dataclass_fields.get(name) is None:
            raise ValueError(f"'{name}' is not a valid attribute for {cls}")

        field_type = dataclass_fields.get(name).type
        params[name] = parse_data(value, field_type)

    return cls(**params)


def parse_custom_class(data: Dict, cls: Type):
    assert isinstance(data, dict), f"data must be of type dict when parsing a custom class, not {type(data)}"
    return cls(**data)


def parse_generic_alias(data: _GenericAlias, cls: Type):

    if cls.__origin__ == Union:
        NoneType = type(None)

        cls = next(
            (
                ft for ft in cls.__args__ if not isinstance(ft, NoneType) and (
                    (inspect.isclass(ft) and isinstance(data, ft)) or
                    (isinstance(data, dict) and
                     (is_dataclass(ft) or inspect.isclass(ft))) or (isinstance(ft, _GenericAlias) and isinstance(data, ft.__origin__))
                )
            ),
            None
        )
        if cls is None:
            raise ValueError(f"Did not find any suitable types in {cls} for value: \n {data}")
        else:
            return parse_data(data, cls)

    if cls.__origin__ == dict:
        return parse_dict(data, cls)
    elif cls.__origin__ == list:
        return parse_list(data, cls)
    elif is_dataclass(cls.__origin__):
        return parse_data(data, cls.__origin__)

    raise NotImplementedError(f"Parsing of {cls} not implemented yet")


def parse_built_in(data: Any):
    assert isinstance(data, built_in_types), f"data should be of any of the types {built_in_types}, not {type(data)}"
    return data


def parse_dict(data: Dict, cls: Type):
    assert isinstance(data, dict), f"data should be of type dict, not {type(data)}"
    val_type = cls.__args__[1]
    instance: dict = dict()
    for key, value in data.items():
        instance.update({key: parse_data(value, val_type)})
    return instance


def parse_list(data: List, cls: Type):
    assert isinstance(data, list), f"data should be of type list, not {type(data)}"
    list_type = cls.__args__[0]
    instance: list = list()
    for value in data:
        instance.append(parse_data(value, list_type))
    return instance
