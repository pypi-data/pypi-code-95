from typing import Any, Dict

from deepmerge import always_merger


def merge_dicts(*args: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Successively merge any number of dictionaries.

    >>> merge_dicts({'a': 1}, {'b': 2})
    {'a': 1, 'b': 2}

    >>> merge_dicts({'a': 1}, {'a': 2}, {'a': 3})
    {'a': 3}

    Returns:
        Dict: Dictionary of merged inputs.
    """
    out = {}  # type: Dict[Any, Any]
    for dct in args:
        out = {**out, **dct}
    return out


def deep_merge_dicts(*args: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Successively perform a deep merge on any number of dictionaries.

    >>> deep_merge_dicts({'a': {'x': 1}}, {'a': {'x': 2}})
    {'a': {'x': 2}}

    Returns:
        Dict: Dictionary of merged inputs.
    """
    out = {}  # type: Dict[Any, Any]
    for dct in args:
        out = always_merger.merge(out, dct)
    return out


def collapse_dict(dct: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Collapse a dictionary's top level keys.

    >>> collapse_dict({'a': {'x': 1}, 'b': {'y': 2}})
    {'x': 1, 'y': 2}

    >>> collapse_dict({'a': {'x': 1}, 'b': 2})
    {'a': {'x': 1}, 'b': 2}

    >>> collapse_dict({})
    {}

    Returns:
        Dict: Dictionary of value fields.
    """
    return (
        merge_dicts(*dct.values())
        if all(map(lambda x: isinstance(x, dict), dct.values()))
        else dct
    )


def key_is_true(dct: Dict[str, Any], key: str) -> bool:
    """
    Check if a dictionary contains a key who's value is set to True.
    Truthy values should return False.

    >>> key_is_true({'a': True}, 'a')
    True

    >>> key_is_true({'a': False}, 'a')
    False

    >>> key_is_true({'a': True}, 'b')
    False

    >>> key_is_true({'a': "True"}, 'a')
    False
    """
    return key in dct and dct[key] is True


def non_null_entries(dct: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    >>> non_null_entries({'a': 0, 'b': None, 'c': []})
    {'a': 0}
    """
    return dict(
        filter(
            lambda x: x[1] not in [None, (), [], {}],
            dct.items(),
        )
    )


def without(dct: Dict[Any, Any], exclude: Any) -> Dict[Any, Any]:
    """
    >>> without({'a': 1, 'b': 2}, 'a')
    {'b': 2}

    >>> without({'a': 1, 'b': 2}, 'c')
    {'a': 1, 'b': 2}
    """
    return {k: v for k, v in dct.items() if k != exclude}
