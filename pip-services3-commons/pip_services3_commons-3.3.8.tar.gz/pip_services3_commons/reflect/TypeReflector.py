# -*- coding: utf-8 -*-
"""
    pip_services3_commons.reflect.TypeReflector
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Type reflector implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import importlib
import inspect
from typing import Any

from pip_services3_commons.convert import TypeConverter, TypeCode
from pip_services3_commons.reflect import TypeDescriptor

from ..errors.NotFoundException import NotFoundException


class TypeReflector:
    """
    Helper class to perform object type introspection and object instantiation.

    This class has symmetric implementation across all languages supported
    by Pip.Services toolkit and used to support dynamic data processing.

    Because all languages have different casing and case sensitivity __rules,
    this TypeReflector treats all type names as case insensitive.

    Example:

    .. code-block:: python

        descriptor = TypeDescriptor("MyObject", "mylibrary")
        Typeeflector.get_type_by_descriptor(descriptor)
        myObj = TypeReflector.create_instance_by_descriptor(descriptor)
        TypeDescriptor.is_primitive(myObject)           # Result: false
        TypeDescriptor.is_primitive(123)                # Result: true
    """

    @staticmethod
    def get_type(name: str, library: str) -> Any:
        """
        Gets object type by its name and library where it is defined.

        :param name: an object type name.

        :param library: a library where the type is defined

        :return: the object type or null is the type wasn't found.
        """
        if name is None:
            raise Exception("Class name cannot be null")
        if library is None:
            raise Exception("Module name cannot be null")

        try:
            # to python format import
            if library.count('.') > 1:
                library = library.split('/')
                dots_lvl = library[0]
                library = dots_lvl + '.'.join(list(filter(lambda x: x != '.', library.split('/'))))
            else:
                library = '.'.join(list(filter(lambda x: x != '.', library.split('/'))))
            module = importlib.import_module(library)
            return getattr(module, name)
        except:
            return None

    @staticmethod
    def get_type_by_descriptor(descriptor: TypeDescriptor) -> Any:
        """
        Gets object type by type descriptor.

        :param descriptor: a type descriptor that points to an object type

        :return: the object type or null is the type wasn't found.
        """
        if descriptor is None:
            raise Exception("Type descriptor cannot be null")

        return TypeReflector.get_type(descriptor.get_name(), descriptor.get_library())

    @staticmethod
    def create_instance(name: str, library: str, *args: Any) -> Any:
        """
        Creates an instance of an object type specified by its name and library where it is defined.

        :param name: an object type (factory function) to create.

        :param library: a library (module) where object type is defined.

        :param args: arguments for the object constructor.

        :return: the created object instance.
        """
        obj_type = TypeReflector.get_type(name, library)
        if obj_type is None:
            raise NotFoundException(
                None, "TYPE_NOT_FOUND", "Type " + name + "," + library + " was not found"
            ).with_details("type", name).with_details("library", library)

        init_params = inspect.signature(obj_type.__init__).parameters

        if len(init_params.keys()) > 1 or init_params.get('self') is None:
            return obj_type(*args)
        else:
            return obj_type()

    @staticmethod
    def create_instance_by_type(obj_type: Any, *args: Any) -> Any:
        """
        Creates an instance of an object type.

        :param obj_type: an object type (factory function) to create.

        :param args: arguments for the object constructor.

        :return: the created object instance.
        """
        if obj_type is None:
            raise Exception("Class type cannot be null")

        return obj_type(*args)

    @staticmethod
    def create_instance_by_descriptor(descriptor: TypeDescriptor, *args: Any) -> Any:
        """
        Creates an instance of an object type specified by type descriptor.

        :param descriptor: a type descriptor that points to an object type

        :param args: arguments for the object constructor.

        :return: the created object instance.
        """
        if descriptor is None:
            raise Exception("Type descriptor cannot be null")

        return TypeReflector.create_instance(descriptor.get_name(), descriptor.get_library(), args)

    @staticmethod
    def is_primitive(value: Any) -> bool:
        """
        Checks if args has primitive type.

        Primitive types are: numbers, strings, booleans, date and time.
        Complex (non-primitive types are): objects, maps and arrays

        :param value: a args to check

        :return: true if the args has primitive type and false if args type is complex.
        """
        typeCode = TypeConverter.to_type_code(value)
        return typeCode == TypeCode.String or typeCode == TypeCode.Enum or typeCode == TypeCode.Boolean \
               or typeCode == TypeCode.Integer or typeCode == TypeCode.Long \
               or typeCode == TypeCode.Float or typeCode == TypeCode.Double \
               or typeCode == TypeCode.DateTime or typeCode == TypeCode.Duration
