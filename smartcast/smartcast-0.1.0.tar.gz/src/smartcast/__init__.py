import typing

import enum
import dataclasses

# flake8: noqa: C901
def cast(value, typeof):
    """
    Cast an normal (json) object to specfied type.
    """
    if typeof is None and not value:
        return None
    if typeof is typing.Union:
        raise Exception("typing.Union is not a valid type")
    # TODO handle datatype specificly
    if typeof is typing._SpecialForm and typeof._name == 'Union':
        possibe_types = typeof._subs_tree()[1:]
        for try_type in possibe_types:
            try:
                return cast(value, try_type)
            except Exception:
                pass
        raise Exception("Not one of the Union types.")

    print(typeof)
    if type(typeof) == typing._GenericAlias:
        if typeof._name == "List":
            (list_type, ) = typeof.__args__
            return [cast(v, list_type) for v in value]
        raise Exception(f"unkown GenericAlias {typeof._name}")

    if isinstance(value, typeof):
        return value

    if dataclasses.is_dataclass(typeof):
        as_dict = {field.name: cast(value[field.name], field.type)
                   for field in dataclasses.fields(typeof) if field.name in value}
        print(as_dict)
        return typeof(**as_dict)

    if typeof is list:
        return [v for v in value]
    if typeof is dict:
        return {k: v for k, v in value.items()}
    if issubclass(typeof, enum.Enum):
        return typeof[value]
    if isinstance(value, dict):
        attrs = typing.get_type_hints(typeof)  # self.__annotations__
        out = typeof()
        # assert attrs.keys() >= content.keys(), "source has unkown key type"
        for attr, typeof in attrs.items():
            if attr in value:
                value = value[attr]
                setattr(out, attr, cast(typeof, value))
            elif not hasattr(out, attr):
                raise Exception(f"{typeof} missing required value for {attr}")
        return out
    # TODO dict
    # TODO list
    raise Exception(f"can't cast {value} to {typeof}")


def normal(value):
    """
    Convert a python object to normal form (so it can be json serlized)
    """
    if isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, dict):
        return {k: normal(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normal(v) for v in value]
    if isinstance(value, enum.Enum):
        return value.name
    if dataclasses.is_dataclass(value):
        return normal(dataclasses.asdict(value))
    return normal(value.__dict__)
