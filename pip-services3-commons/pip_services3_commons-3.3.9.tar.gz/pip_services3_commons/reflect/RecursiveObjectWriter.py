# -*- coding: utf-8 -*-
"""
    pip_services3_commons.reflect.RecursiveObjectWriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Recursive object writer implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from .ObjectReader import ObjectReader
from .ObjectWriter import ObjectWriter
from .RecursiveObjectReader import RecursiveObjectReader


class RecursiveObjectWriter:
    """
    Helper class to perform property introspection and dynamic writing.

    It is similar to :class:`ObjectWriter <pip_services3_commons.reflect.ObjectWriter.ObjectWriter>` but writes properties recursively
    through the entire object graph. Nested property names are defined
    using dot notation as "object.subobject.property"
    """

    @staticmethod
    def __create_property(obj: Any, name: str):
        return {}

    @staticmethod
    def __perform_set_property(obj: Any, names: List[str], name_index: int, value: Any) -> Any:
        if name_index < len(names) - 1:
            sub_obj = ObjectReader.get_property(obj, names[name_index])
            if not (sub_obj is None):
                RecursiveObjectWriter.__perform_set_property(sub_obj, names, name_index + 1, value)
            else:
                sub_obj = RecursiveObjectWriter.__create_property(obj, names[name_index])
                if not (sub_obj is None):
                    RecursiveObjectWriter.__perform_set_property(sub_obj, names, name_index + 1, value)
                    ObjectWriter.set_property(obj, names[name_index], sub_obj)
        else:
            ObjectWriter.set_property(obj, names[name_index], value)

    @staticmethod
    def set_property(obj: Any, name: str, value: Any):
        """
        Recursively sets args of object and its subobjects property specified by its name.

        The object can be a user defined object, map or array.
        The property name correspondently must be object property, map key or array index.

        If the property does not exist or introspection fails
        this method doesn't do anything and doesn't any throw errors.

        :param obj: an object to write property to.

        :param name: a name of the property to set.

        :param value: a new args for the property to set.
        """
        if obj is None or name is None:
            return

        names = name.split(".")
        if names is None or len(names) == 0:
            return

        RecursiveObjectWriter.__perform_set_property(obj, names, 0, value)

    @staticmethod
    def set_properties(obj: Any, values: Any):
        """
        Recursively sets values of some (all) object and its subobjects properties.

        The object can be a user defined object, map or array.
        Property values correspondently are object properties, map key-pairs or array elements with their indexes.

        If some properties do not exist or introspection fails they are just silently skipped and no errors thrown.

        :param obj: an object to write properties to.

        :param values: a map, containing property names and their values.
        """
        if values is None or len(values) == 0:
            return

        for (key, value) in values.items():
            RecursiveObjectWriter.set_property(obj, key, value)

    @staticmethod
    def copy_properties(dest: Any, src: Any):
        """
        Copies content of one object to another object
        by recursively reading all properties from source object
        and then recursively writing them to destination object.

        :param dest: a destination object to write properties to.

        :param src: a source object to read properties from
        """
        if dest is None or src is None:
            return

        values = RecursiveObjectReader.get_properties(src)
        RecursiveObjectWriter.set_properties(dest, values)
