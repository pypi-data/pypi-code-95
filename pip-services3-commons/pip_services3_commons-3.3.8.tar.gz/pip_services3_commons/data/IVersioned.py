# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.IVersioned
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for versioned data objects
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC


class IVersioned(ABC):
    """
    Interface for data objects that can be versioned.

    Versioning is often used as optimistic concurrency mechanism.

    The version doesn't have to be a number, but it is recommended to use sequential
    values to determine if one object has newer or older version than another one.

    It is a common pattern to use the time of change as the object version

    Example:

    .. code-block:: python

        class MyData(IStringIdentifiable, IVersioned):
            id = None
            version = None

            # do something

            def update_data(item):

                # do something

                if item.version < old_item.version:
                    raise ConcurrencyException(None, "VERSION_CONFLICT", "The change has older version stored args")
            
            # do something
    """
    version: str = None
