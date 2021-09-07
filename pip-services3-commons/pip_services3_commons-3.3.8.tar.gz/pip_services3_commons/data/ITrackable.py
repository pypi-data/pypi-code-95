# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.ITrackable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for trackable data objects
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from datetime import datetime

from pip_services3_commons.data import IChangeable


class ITrackable(IChangeable):
    """
    Interface for data objects that can track their changes, including logical deletion.

    Example:

    .. code-block:: python
    
        class MyData(IStringIdentifiable, ITrackable):
            id = None
            ...

            change_time = None
            create_time = None
            deleted = None
    """
    # The UTC time at which the object was created.
    create_time: datetime = None
    # The UTC time at which the object was last changed (created, updated, or deleted).
    change_time: datetime = None
    # The logical deletion flag. True when object is deleted and null or false otherwise
    deleted: bool = None
