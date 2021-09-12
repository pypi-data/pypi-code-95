# -*- coding: utf-8 -*-
"""
    pip_services3_commons.reflect.PropertyReflector
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Property reflector implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List


class PropertyReflector:
    """
    Helper class to perform property introspection and dynamic reading and writing.

    This class has symmetric implementation across all languages supported
    by Pip.Services toolkit and used to support dynamic data processing.

    Because all languages have different casing and case sensitivity __rules,
    this PropertyReflector treats all property names as case insensitive.

    Example:

    .. code-block:: python

        myObj = MyObject()

        properties = PropertyReflector.get_property_names()
        PropertyReflector.has_property(myObj, "myProperty")

        args = PropertyReflector.get_property(myObj, "myProperty")
        PropertyReflector.set_property(myObj, "myProperty", 123)
    """

    @staticmethod
    def _is_property(property, name: str) -> bool:
        if callable(property):
            return False

        # if magic method or base abstract class property
        if name.startswith("__") and name.endswith('__') or name == '_abc_impl':
            return False

        return True

    @staticmethod
    def __match_field(field_name: str, filed_value: Any, expected_name: str) -> bool:
        if filed_value is None:
            return False
        if not callable(filed_value):
            return False
        if field_name.startswith("_"):
            return False
        if expected_name is None:
            return True

        return field_name.lower() == expected_name

    @staticmethod
    def has_property(obj: Any, name: str) -> bool:
        """
        Checks if object has a property with specified name.

        :param obj: an object to introspect.

        :param name: a name of the property to check.

        :return: true if the object has the property and false if it doesn't.
        """
        if obj is None:
            raise Exception("Object cannot be null")
        if name is None:
            raise Exception("Property name cannot be null")

        name = name.lower()

        for property_name in dir(obj):
            if property_name.lower() != name:
                continue

            if hasattr(obj, property_name):
                property = getattr(obj, property_name, None)

                if PropertyReflector._is_property(property, property_name):
                    return True

        return False

    @staticmethod
    def get_property(obj: Any, name: str) -> Any:
        """
        Gets args of object property specified by its name.

        :param obj: an object to read property from.

        :param name: a name of the property to get.

        :return: the property args or null if property doesn't exist or introspection failed.
        """
        if obj is None:
            raise Exception("Object cannot be null")
        if name is None:
            raise Exception("Property name cannot be null")

        name = name.lower()

        try:
            for property_name in dir(obj):
                if property_name.lower() != name:
                    continue

                if hasattr(obj, property_name):
                    property = getattr(obj, property_name, None)

                    if PropertyReflector._is_property(property, property_name):
                        return property
        except:
            pass

        return None

    @staticmethod
    def get_property_names(obj: Any) -> List[str]:
        """
        Gets names of all properties implemented in specified object.

        :param obj: an objec to introspect.

        :return: a list with property names.
        """
        property_names = []

        for property_name in dir(obj):

            if hasattr(obj, property_name):
                property = getattr(obj, property_name, None)

                if PropertyReflector._is_property(property, property_name):
                    property_names.append(property_name)

        return property_names

    @staticmethod
    def get_properties(obj: Any) -> Any:
        """
        Get values of all properties in specified object and returns them as a map.

        :param obj: an object to get properties from.

        :return: a map, containing the names of the object's properties and their values.
        """
        properties = {}

        for property_name in dir(obj):

            if hasattr(obj, property_name):
                property = getattr(obj, property_name, None)

                if PropertyReflector._is_property(property, property_name):

                    # Prepare private fields
                    if property_name.startswith('_') and len(property_name.split('__')) > 1:
                        property_name = '__' + property_name.split('__')[-1]

                    # Prepare protected fields
                    elif property_name.startswith('_'):
                        property_name = property_name[1:]

                    properties[property_name] = property

        return properties

    @staticmethod
    def set_property(obj: Any, name: str, value: Any):
        """
        Sets args of object property specified by its name.

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

        try:
            for property_name in dir(obj):
                if property_name.lower() != name:
                    continue

                if hasattr(obj, property_name):
                    property = getattr(obj, property_name, None)

                    if PropertyReflector._is_property(property, property_name):
                        setattr(obj, property_name, value)
        except:
            pass

    @staticmethod
    def set_properties(obj: Any, values: Any):
        """
        Sets values of some (all) object properties.

        If some properties do not exist or introspection fails
        they are just silently skipped and no errors thrown.

        :param obj: an object to write properties to.

        :param values: a map, containing property names and their values.
        """
        if values is None or len(values) == 0:
            return

        for (name, value) in values:
            PropertyReflector.set_property(obj, name, value)
