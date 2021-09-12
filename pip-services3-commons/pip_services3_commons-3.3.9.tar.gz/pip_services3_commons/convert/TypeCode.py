# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.TypeCode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Type code enumeration
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from enum import Enum


class TypeCode(Enum):
    """
    Codes for the data types that can be converted using :class:`TypeConverter <pip_services3_commons.convert.TypeConverter.TypeConverter>`.
    """
    Unknown = 0
    String = 1
    Boolean = 2
    Integer = 3
    Long = 4
    Float = 5
    Double = 6
    DateTime = 7
    Duration = 8
    Object = 9
    Enum = 10
    Array = 11
    Map = 12
