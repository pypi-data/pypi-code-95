# -*- coding: utf-8 -*-
"""
    pip_services_runtime.refer.Descriptor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Component descriptor implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional, Any

from ..errors.ConfigException import ConfigException


class Descriptor:
    """
    Locator type that most often used in PipServices toolkit.
    It locates components using several fields:
        - Group: a package or just named group of components like "pip-services"
        - Type: logical component type that defines it's contract like "persistence"
        - Kind: physical implementation type like "mongodb"
        - Name: unique component name like "default"
        - Version: version of the component contract like "1.0"

    The locator matching can be done by all or only few selected fields.
    The fields that shall be excluded from the matching must be set to **"*"** or **None**.
    That approach allows to implement many interesting scenarios. For instance:
        - Locate all loggers (match by type and version)
        - Locate persistence components for a microservice (match by group and type)
        - Locate specific component by its name (match by name)

    Example:

    .. code-block:: python
    
        locator1 = Descriptor("mygroup", "connector", "aws", "default", "1.0")
        locator2 = Descriptor.from_string("mygroup:connector:*:*:1.0")

        locator1.match(locator2);		// Result: true
        locator1.eq(locator2);		// Result: true
        locator1.exact_match(locator2);	// Result: false
    """

    def __init__(self, group: Optional[str], type: Optional[str], kind: Optional[str], name: Optional[str],
                 version: Optional[str]):
        """
        Creates a new instance of the descriptor.

        :param group: a logical component group

        :param type: a logical component type or contract

        :param kind: a component implementation type

        :param name: a unique component name

        :param version: a component implementation version
        """
        group = None if "*" == group else group
        type = None if "*" == type else type
        kind = None if "*" == kind else kind
        name = None if "*" == name else name
        version = None if "*" == version else version

        self.__group: str = group
        self.__type: str = type
        self.__kind: str = kind
        self.__name: str = name
        self.__version: str = version

    def get_group(self) -> str:
        """
         Gets the component's logical group.

        :return: the component's logical group
        """
        return self.__group

    def get_type(self) -> str:
        """
        Gets the component's logical type.

        :return: the component's logical type.
        """
        return self.__type

    def get_kind(self) -> str:
        """
        Gets the component's implementation type.

        :return: the component's implementation type.
        """
        return self.__kind

    def get_name(self) -> str:
        """
        Gets the unique component's name.

        :return: the unique component's name.
        """
        return self.__name

    def get_version(self) -> str:
        """
        Gets the component's implementation version.

        :return: the component's implementation version.
        """
        return self.__version

    def __match_field(self, field1: str, field2: str) -> bool:
        return field1 is None \
               or field2 is None \
               or field1 == field2

    def match(self, descriptor: 'Descriptor') -> bool:
        """
        Partially matches this descriptor to another descriptor.
        Fields that contain "*" or null are excluded from the match.

        :param descriptor: the descriptor to match this one against.

        :return: true if descriptors match and false otherwise
        """
        return self.__match_field(self.__group, descriptor.get_group()) \
               and self.__match_field(self.__type, descriptor.get_type()) \
               and self.__match_field(self.__kind, descriptor.get_kind()) \
               and self.__match_field(self.__name, descriptor.get_name()) \
               and self.__match_field(self.__version, descriptor.get_version())

    def __exact_match_field(self, field1: str, field2: str) -> bool:
        if field1 is None and field2 is None:
            return True
        if field1 is None or field2 is None:
            return False
        return field1 == field2

    def exact_match(self, descriptor: 'Descriptor') -> bool:
        """
        Matches this descriptor to another descriptor by all fields. No exceptions are made.

        :param descriptor: the descriptor to match this one against.

        :return: true if descriptors match and false otherwise.
        """
        return self.__exact_match_field(self.__group, descriptor.get_group()) \
               and self.__exact_match_field(self.__type, descriptor.get_type()) \
               and self.__exact_match_field(self.__kind, descriptor.get_kind()) \
               and self.__exact_match_field(self.__name, descriptor.get_name()) \
               and self.__exact_match_field(self.__version, descriptor.get_version())

    def is_complete(self) -> bool:
        """
        Checks whether all descriptor fields are set.
        If descriptor has at least one "*" or null field it is considered "incomplete"

        :return: true if all descriptor fields are defined and false otherwise.
        """
        return not (self.__group is None) and not (self.__type is None) \
               and not (self.__kind is None) and not (self.__name is None) and not (self.__version is None)

    def equals(self, value: Any) -> bool:
        """
        Compares this descriptor to a args.
        If args is a Descriptor it tries to match them, otherwise the method returns false.

        :param value: the args to match against this descriptor.

        :return: true if the args is matching descriptor and false otherwise.
        """
        if isinstance(value, Descriptor):
            return self.match(value)
        return False

    def to_string(self) -> str:
        """
        Gets a string representation of the object.
        The result is a colon-separated list of descriptor fields as "mygroup:connector:aws:default:1.0"

        :return: a string representation of the object.
        """
        result = ''
        result += self.__group if not (self.__group is None) else '*'
        result += ':'
        result += self.__type if not (self.__type is None) else '*'
        result += ':'
        result += self.__kind if not (self.__kind is None) else '*'
        result += ':'
        result += self.__name if not (self.__name is None) else '*'
        result += ':'
        result += self.__version if not (self.__version is None) else '*'
        return result

    def __eq__(self, other):
        """
        Compares this descriptor to a args.
        If args is a Descriptor it tries to match them, otherwise the method returns false.

        :param other: the args to match against this descriptor.

        :return: true if the args is matching descriptor and false otherwise.
        """
        if isinstance(other, Descriptor):
            return self.match(other)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        """
        Gets a string representation of the object.
        The result is a colon-separated list of descriptor fields as "mygroup:connector:aws:default:1.0"

        :return: a string representation of the object.
        """
        result = ''
        result += self.__group if not (self.__group is None) else '*'
        result += ':'
        result += self.__type if not (self.__type is None) else '*'
        result += ':'
        result += self.__kind if not (self.__kind is None) else '*'
        result += ':'
        result += self.__name if not (self.__name is None) else '*'
        result += ':'
        result += self.__version if not (self.__version is None) else '*'
        return result

    @staticmethod
    def from_string(value: str) -> Optional['Descriptor']:
        """
        Parses colon-separated list of descriptor fields and returns them as a Descriptor.

        :param value: colon-separated descriptor fields to initialize Descriptor.

        :return: a newly created Descriptor.
        """
        if value is None or len(value) == 0:
            return None

        tokens = value.split(":")
        if len(tokens) != 5:
            raise ConfigException(
                None, "BAD_DESCRIPTOR", "Descriptor " + str(value) + " is in wrong format"
            ).with_details("descriptor", value)

        return Descriptor(tokens[0].strip(), tokens[1].strip(), tokens[2].strip(), tokens[3].strip(), tokens[4].strip())
