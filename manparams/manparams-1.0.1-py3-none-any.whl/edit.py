"""
High level edition function
"""

import collections.abc


def deepupdate(inputs, other):
    """Recursively update content of inputs with values in other

    Args:
        inputs (dict): object to update
        other (collections.abc.Mapping): potentially nested dictionaries

    Returns:
        (None): inputs modified in place

    """
    for key, val in other.items():
        if isinstance(val, collections.abc.Mapping):
            if key not in inputs:
                inputs[key] = {}

            deepupdate(inputs[key], val)
        else:
            inputs[key] = val
