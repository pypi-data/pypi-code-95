# -*- coding: utf-8 -*-
"""
    pip_services3_commons.reflect.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains classes for data reflection. Reflects objects into parameters, methods.
    Most programming languages contain reflections, but they are all implemented
    differently. In the PipService framework, dynamic data types are often used. So as
    to not rewrite these dynamic data types differently for each language,
    this cross-language reflection package was written. All dynamic data types that are
    built on top of this package are portable from one language to another.

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'TypeDescriptor', 'TypeReflector', 'MethodReflector', 
    'PropertyReflector', 'TypeMatcher', 
    'ObjectReader', 'ObjectWriter',
    'RecursiveObjectReader', 'RecursiveObjectWriter'
]

from .TypeDescriptor import TypeDescriptor
from .TypeReflector import TypeReflector
from .MethodReflector import MethodReflector
from .PropertyReflector import PropertyReflector
from .TypeMatcher import TypeMatcher
from .ObjectReader import ObjectReader
from .ObjectWriter import ObjectWriter
from .RecursiveObjectReader import RecursiveObjectReader
from .RecursiveObjectWriter import RecursiveObjectWriter
