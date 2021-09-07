# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.IIdentifiable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for identifiable data objects
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from abc import ABC
from typing import Any


class IIdentifiable(ABC):
    """
    Generic interface for data objects that can be uniquely identified by an id.

    The type specified in the interface defines the type of id field.

    Example:
    
    .. code-block:: python

        class MyData(IIdentifiable):
            id = None

    """
    id: Any
