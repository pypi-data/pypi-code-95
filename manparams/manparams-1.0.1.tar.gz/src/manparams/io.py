"""
This module defines function to serialize and deserialize parameters
"""
from dataclasses import fields

import marshmallow_dataclass


def dump(params):
    """Serialize params to native Python data types.

    Args:
        params (Params): object to serialize

    Returns:
        (dict)
    """
    schema = marshmallow_dataclass.class_schema(type(params))()
    return schema.dump(params)


def load(params_cls, data):
    """Create Params object with content of data.

    Args:
        params_cls (type): Params dataclass
        data (dict): previously serialized subset of params

    Returns:
        (Params): object of type params_cls
    """
    schema = marshmallow_dataclass.class_schema(params_cls)()
    return schema.load(data)


def to_record(params):
    """Dumps outer level into dict.

    This function is not recursive and will not convert sub-params.

    Args:
        params (Params): object to serialize

    Returns:
        (dict)
    """
    return {ff.name: getattr(params, ff.name) for ff in fields(params)}
