# -*- coding: utf-8 -*-
"""
    pip_services3_commons.reflect.TypeDescriptor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Type descriptor implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional, Any

from ..errors.ConfigException import ConfigException


class TypeDescriptor:
    """
    Descriptor that points to specific object type by it's name
    and optional library (or module) where this type is defined.

    This class has symmetric implementation across all languages supported
    by Pip.Services toolkit and used to support dynamic data processing.
    """

    def __init__(self, name: str, library: Optional[str]):
        """
        Creates a new instance of the type descriptor and sets its values.

        :param name: a name of the object type.

        :param library: a library or module where this object type is implemented.
        """
        self.__name: str = name
        self.__library: str = library

    def get_name(self) -> str:
        """
        Get the name of the object type.

        :return: the name of the object type.
        """
        return self.__name

    def get_library(self) -> str:
        """
        Gets the name of the library or module where the object type is defined.

        :return: the name of the library or module.
        """
        return self.__library

    def __eq__(self, other: Any) -> bool:
        """
        Compares this descriptor to a args.
        If the args is also a TypeDescriptor it compares their name and library fields.
        Otherwise this method returns false.

        :param other: a args to compare.

        :return: true if args is identical TypeDescriptor and false otherwise.
        """
        if isinstance(other, TypeDescriptor):
            if self.__name is None or other.__name is None:
                return False
            if self.__name != other.__name:
                return False
            if self.__library is None or other.__library is None or self.__library == other.__library:
                return True

        return False

    def equals(self, other: Any) -> bool:
        """
        Compares this descriptor to a args.
        If the args is also a TypeDescriptor it compares their name and library fields.
        Otherwise this method returns false.

        :param other: a args to compare.

        :return: true if args is identical TypeDescriptor and false otherwise.
        """
        if isinstance(other, TypeDescriptor):
            if self.__name is None or other.__name is None:
                return False
            if self.__name != other.__name:
                return False
            if self.__library is None or other.__library is None or self.__library == other.__library:
                return True

        return False

    def __str__(self):
        """
        Gets a string representation of the object. The result has format name[,library]

        :return: a string representation of the object.
        """
        result = self.__name
        if not (self.__library is None):
            result += ',' + self.__library
        return result

    def to_string(self):
        """
        Gets a string representation of the object. The result has format name[,library]

        :return: a string representation of the object.
        """
        result = self.__name
        if not (self.__library is None):
            result += ',' + self.__library
        return result

    @staticmethod
    def from_string(value: str) -> Optional['TypeDescriptor']:
        """
        Parses a string to get descriptor fields and returns them as a Descriptor.
        The string must have format name[,library]

        :param value: a string to parse.

        :return: a newly created Descriptor.
        """
        if value is None or len(value) == 0:
            return None

        tokens = value.split(",")
        if len(tokens) == 1:
            return TypeDescriptor(tokens[0].strip(), None)
        elif len(tokens) == 2:
            return TypeDescriptor(tokens[0].strip(), tokens[1].strip())
        else:
            raise ConfigException(
                None, "BAD_DESCRIPTOR", "Type descriptor " + value + " is in wrong format"
            ).with_details("descriptor", value)
