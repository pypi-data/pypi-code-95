# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.IChangeable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for changeable data objects
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from datetime import datetime


class IChangeable(ABC):
    """
    Interface for data objects that contain their latest change time.

    Example:

    .. code-block:: python

        class MyData(IStringIdentifiable, IChangeable):
            id: str = '1234567'
            field1: str = 'field1'
            field2: int = 123
            change_time: datetime = datetime.now()

    """
    change_time: datetime = None
