# -*- coding: utf-8 -*-
"""
    pip_services3_commons.reflect.ObjectWriter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Object writer implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any

from .PropertyReflector import PropertyReflector
from ..convert.IntegerConverter import IntegerConverter


class ObjectWriter:
    """
    Helper class to perform property introspection and dynamic writing.

    In contrast to :class:`PropertyReflector <pip_services3_commons.reflect.PropertyReflector.PropertyReflector>` which only introspects regular objects,
    this ObjectWriter is also able to handle maps and arrays.
    For maps properties are key-pairs identified by string keys,
    For arrays properties are elements identified by integer index.

    This class has symmetric implementation across all languages supported
    by Pip.Services toolkit and used to support dynamic data processing.

    Because all languages have different casing and case sensitivity __rules,
    this ObjectWriter treats all property names as case insensitive.

    Example:

    .. code-block:: python
    
        myObj = MyObject()

        ObjectWriter.set_property(myObj, "myProperty", 123)
        myMap = { key1: 123, key2: "ABC" }
        ObjectWriter.set_property(myMap, "key1", "XYZ")

        myArray = [1, 2, 3]
        ObjectWriter.set_property(myArray, "0", 123)
    """

    @staticmethod
    def set_property(obj: Any, name: str, value: Any):
        """
        ets args of object property specified by its name.

        The object can be a user defined object, map or array.
        The property name correspondently must be object property, map key or array index.

        If the property does not exist or introspection fails
        this method doesn't do anything and doesn't any throw errors.

        :param obj: an object to write property to.

        :param name: a name of the property to set.

        :param value: a new args for the property to set.
        """
        if obj is None:
            raise Exception("Object cannot be null")
        if name is None:
            raise Exception("Property name cannot be null")

        name = name.lower()

        if isinstance(obj, dict):
            for key in obj.keys():
                if name == str(key).lower():
                    obj[key] = value
                    return
            obj[name] = value
        elif isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
            index = IntegerConverter.to_nullable_integer(name)
            if index is None:
                return
            if 0 <= index < len(obj):
                obj[index] = value
            elif isinstance(obj, list):
                while index - 1 >= len(obj):
                    obj.append(None)
                obj.append(value)
        else:
            return PropertyReflector.set_property(obj, name, value)

    @staticmethod
    def set_properties(obj: Any, values: Any):
        """
        Sets values of some (all) object properties.

        The object can be a user defined object, map or array.
        Property values correspondently are object properties, map key-pairs or array elements with their indexes.

        If some properties do not exist or introspection fails they are just silently skipped and no errors thrown.

        :param obj: an object to write properties to.

        :param values: a map, containing property names and their values.
        """
        if values is None or len(values) == 0:
            return

        for (key, value) in values.items():
            ObjectWriter.set_property(obj, key, value)
