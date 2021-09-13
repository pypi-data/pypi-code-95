from typing import Any
from .missing import MISSING


def zip_dict(*dicts: dict, default=None) -> dict:
    """
    Takes a list of dicts, and creates a union of all dicts with the values from each dict as elements of a tuples
    zip_dict({a: 1, b: 2}, {a: 2, c: 3}) == {a: (1, 2), b: {2, None}, c: {None, 3}}
    """
    keys_sets = tuple(set(d.keys()) for d in dicts)
    keys = set.union(*keys_sets)
    return {k: tuple(d.get(k, default) for d in dicts) for k in keys}


def get_attr_typevals(cls) -> dict[str, tuple[Any, Any]]:
    attr_types: dict[str] = {name: t for name, t in getattr(cls, "__annotations__", {}).items() if not name.startswith("__")}
    attr_vals: dict[str] = {name: v for name, v in cls.__dict__.items() if not name.startswith("__")}
    attr_typevals = zip_dict(attr_types, attr_vals, default=MISSING)
    return attr_typevals
