# -*- coding: utf-8 -*-
"""
    pip_services3_commons.reflect.ObjectReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Object reader implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from .PropertyReflector import PropertyReflector
from ..convert.IntegerConverter import IntegerConverter


class ObjectReader:
    """
    Helper class to perform property introspection and dynamic reading.

    In contrast to :class:`PropertyReflector <pip_services3_commons.reflect.PropertyReflector.PropertyReflector>` which only introspects regular objects,
    this ObjectReader is also able to handle maps and arrays.

    For maps properties are key-pairs identified by string keys,
    For arrays properties are elements identified by integer index.

    This class has symmetric implementation across all languages supported
    by Pip.Services toolkit and used to support dynamic data processing.

    Because all languages have different casing and case sensitivity __rules,
    this ObjectReader treats all property names as case insensitive.

    Example:

    .. code-block:: python
    
        myObj = MyObject()

        properties = ObjectReader.get_property_names()

        ObjectReader.has_property(myObj, "myProperty")
        args = PropertyReflector.get_property(myObj, "myProperty")

        myMap = { key1: 123, key2: "ABC" }
        ObjectReader.has_property(myMap, "key1")
        args = ObjectReader.get_property(myMap, "key1")

        myArray = [1, 2, 3]
        ObjectReader.has_property(myArrat, "0")
        args = ObjectReader.get_property(myArray, "0")
    """

    @staticmethod
    def get_value(obj: Any) -> Any:
        """
        Gets a real object args. If object is a wrapper, it unwraps the args behind it.
        Otherwise it returns the same object args.

        :param obj: an object to unwrap.

        :return: an actual (unwrapped) object args.
        """
        # Todo: just a blank implementation for compatibility
        return obj

    @staticmethod
    def has_property(obj: Any, name: str) -> bool:
        """
        Checks if object has a property with specified name.

        The object can be a user defined object, map or array.
        The property name correspondently must be object property, map key or array index.

        :param obj: an object to introspect.

        :param name: a name of the property to check.

        :return: true if the object has the property and false if it doesn't.
        """
        if obj is None or name is None:
            return False

        name = name.lower()

        if isinstance(obj, dict):
            for (key, value) in obj.items():
                if name == str(key).lower():
                    return True
            return False
        elif isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
            index = IntegerConverter.to_nullable_integer(name)
            return index is not None and 0 <= index < len(obj)
        else:
            return PropertyReflector.has_property(obj, name)

    @staticmethod
    def get_property(obj: Any, name: str) -> Any:
        """
        Gets args of object property specified by its name.

        The object can be a user defined object, map or array.
        The property name correspondently must be object property, map key or array index.

        :param obj: an object to read property from.

        :param name: a name of the property to get.

        :return: the property args or null if property doesn't exist or introspection failed.
        """
        if obj is None or name is None:
            return False

        name = name.lower()

        if isinstance(obj, dict):
            for (key, value) in obj.items():
                if name == str(key).lower():
                    return value
            return None
        elif isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
            index = IntegerConverter.to_nullable_integer(name)
            if index is not None and 0 <= index < len(obj):
                return obj[index]
            return None
        else:
            return PropertyReflector.get_property(obj, name)

    @staticmethod
    def get_property_names(obj: Any) -> List[str]:
        """
        Gets names of all properties implemented in specified object.

        The object can be a user defined object, map or array.
        Returned property name correspondently are object properties, map keys or array indexes.

        :param obj: an object to introspect.

        :return: a list with property names.
        """
        property_names = []

        if isinstance(obj, dict):
            for (key, value) in obj.items():
                property_names.append(key)
        elif isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
            for index in range(len(obj)):
                property_names.append(str(index))
        else:
            property_names = PropertyReflector.get_property_names(obj)

        return property_names

    @staticmethod
    def get_properties(obj: Any) -> Any:
        """
        Get values of all properties in specified object and returns them as a map.

        The object can be a user defined object, map or array.
        Returned properties correspondently are object properties, map key-pairs or array elements with their indexes.

        :param obj: an object to get properties from.

        :return: a map, containing the names of the object's properties and their values.
        """
        map = {}

        if isinstance(obj, dict):
            for (key, value) in obj.items():
                map[key] = value
        elif isinstance(obj, (list, set, tuple)):
            for index in range(len(obj)):
                map[str(index)] = obj[index]
        else:
            map = PropertyReflector.get_properties(obj)

        return map
