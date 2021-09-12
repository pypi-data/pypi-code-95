# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.INamed
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for named data objects
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""


class INamed:
    """
    Interface for data objects that have human-readable names.

    Example:

    .. code-block:: python
    
        class MyData(IIdentifiable, INamed):
            id = None
            name = None

    """
    name: str = None
