# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains "soft" data converters. Soft data converters differ from the data conversion algorithms
    found in typical programming language, due to the fact that they support rare conversions between
    various data types (such as integer to timespan, timespan to string, and so on).

    These converters are necessary, due to the fact that data in enterprise systems is represented in
    various forms and conversion is often necessary – at times in very difficult combinations.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'StringConverter', 'BooleanConverter', 'IntegerConverter',
    'LongConverter', 'FloatConverter', 'DoubleConverter', 'DateTimeConverter',
    'ArrayConverter', 'MapConverter', 'RecursiveMapConverter',
    'JsonConverter', 'TypeCode', 'TypeConverter', 'UTC'
]

from .ArrayConverter import ArrayConverter
from .BooleanConverter import BooleanConverter
from .DateTimeConverter import DateTimeConverter
from .DoubleConverter import DoubleConverter
from .FloatConverter import FloatConverter
from .IntegerConverter import IntegerConverter
from .JsonConverter import JsonConverter
from .LongConverter import LongConverter
from .MapConverter import MapConverter
from .RecursiveMapConverter import RecursiveMapConverter
from .StringConverter import StringConverter
from .TypeCode import TypeCode
from .TypeConverter import TypeConverter
from .UTC import UTC
