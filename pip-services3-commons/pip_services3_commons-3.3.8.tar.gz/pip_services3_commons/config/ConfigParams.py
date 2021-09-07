# -*- coding: utf-8 -*-
"""
    pip_services3_commons.config.ConfigParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Config params implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from ..data.StringValueMap import StringValueMap
from ..reflect.RecursiveObjectReader import RecursiveObjectReader


class ConfigParams(StringValueMap):
    """
    Contains a key-args map with configuration parameters.
    All values stored as strings and can be serialized as JSON or string forms.
    When retrieved the values can be automatically converted on read using GetAsXXX methods.

    The keys are case-sensitive, so it is recommended to use consistent C-style as: **"my_param"**

    Configuration parameters can be broken into sections and subsections using dot notation as:
    **"section1.subsection1.param1"**. Using GetSection method all parameters from specified section
    can be extracted from a ConfigMap.

    The ConfigParams supports serialization from/to plain strings as:
    **"key1=123;key2=ABC;key3=2016-09-16T00:00:00.00Z"**

    ConfigParams are used to pass configurations to :class:`IConfigurable <pip_services3_commons.config.IConfigurable.IConfigurable>` objects.
    They also serve as a basis for more concrete configurations such as :class:`ConnectionParams <pip_services3_components.connect.ConnectionParams.ConnectionParams>`
    or :class:`CredentialParams <pip_services3_components.auth.CredentialParams.CredentialParams>` (in the Pip.Services components package).

    Example:

    .. code-block:: python

        config = ConfigParams.fromTuples("section1.key1", "AAA",
                                         "section1.key2", 123,
                                         "section2.key1", true)
        config.get_as_string("section1.key1")  # Result: AAA
        config.get_as_integer("section1.key1") # Result: 0

        section1 = config.get_section("section1")
        section1.__str__() # Result: key1=AAA;key2=123
    """

    def __init__(self, values: Any = None):
        """
        Creates a new :class:`ConfigParams` and fills it with values.

        :param values: (optional) an object to be converted into key-args pairs to initialize this config map.
        """
        super().__init__(values)

    def get_section_names(self) -> List[str]:
        """
        Gets a list with all 1st level section names.

        :return: a list of section names stored in this ConfigMap.
        """
        sections = []

        for (key, value) in self.items():
            pos = key.find('.')
            if pos > 0:
                key = key[0: pos]

            # Perform case sensitive search
            found = False
            for section in sections:
                if section == key:
                    found = True
                    break

            if not found:
                sections.append(key)

        return sections

    def get_section(self, section: str) -> 'ConfigParams':
        """
        Gets parameters from specific section stored in this ConfigMap.
        The section name is removed from parameter keys.

        :param section: name of the section to retrieve configuration parameters from.

        :return: all configuration parameters that belong to the section named 'section'.
        """
        result = ConfigParams()
        prefix = section + "."

        for (key, value) in self.items():
            # Prevents error on the next line
            if len(key) < len(prefix):
                continue

            # Perform case sensitive match
            key_prefix = key[: len(prefix)]
            if key_prefix == prefix:
                key = key[len(prefix):]
                result[key] = value

        return result

    def _is_shadow_name(self, name):
        return name is None or len(name) == 0 or name[0] == "#" or name[0] == "!"

    def add_section(self, section: str, section_params: 'ConfigParams'):
        """
        Adds parameters into this ConfigParams under specified section.
        Keys for the new parameters are appended with section dot prefix.

        :param section: name of the section where add new parameters

        :param section_params: new parameters to be added.
        """
        if section is None:
            raise Exception("Section name cannot be null")

        section = "" if self._is_shadow_name(section) else section

        if section_params is None or len(section_params) == 0:
            return

        for (key, value) in section_params.items():
            key = "" if self._is_shadow_name(key) else key

            if len(key) > 0 and len(section) > 0:
                key = section + "." + key
            elif len(key) == 0:
                key = section

            self[key] = value

    def override(self, config_params: 'ConfigParams') -> 'ConfigParams':
        """
        Overrides parameters with new values from specified ConfigParams and returns a new ConfigParams object.

        :param config_params: ConfigMap with parameters to override the current values.

        :return: a new ConfigParams object.
        """
        map = StringValueMap.from_maps(self, config_params)
        return ConfigParams(map)

    def set_defaults(self, default_config_params: 'ConfigParams') -> 'ConfigParams':
        """
        Set default values from specified ConfigParams and returns a new ConfigParams object.

        :param default_config_params: ConfigMap with default parameter values.

        :return: a new ConfigParams object.
        """
        map = StringValueMap.from_maps(default_config_params, self)
        return ConfigParams(map)

    @staticmethod
    def from_value(value: Any) -> 'ConfigParams':
        """
        Creates a new ConfigParams object filled with key-args pairs from specified object.

        :param value: an object with key-args pairs used to initialize a new ConfigParams.

        :return: a new ConfigParams object.
        """
        map = RecursiveObjectReader.get_properties(value)
        return ConfigParams(map)

    @staticmethod
    def from_tuples(*tuples: Any) -> 'ConfigParams':
        """
        Creates a new ConfigParams object filled with provided key-args pairs called tuples.
        Tuples parameters contain a sequence of key1, value1, key2, value2, ... pairs.

        :param tuples: the tuples to fill a new ConfigParams object.

        :return: a new ConfigParams object.
        """

        map = StringValueMap.from_tuples_array(tuples)
        return ConfigParams(map)

    @staticmethod
    def from_string(line: str) -> 'ConfigParams':
        """
        Creates a new ConfigParams object filled with key-args pairs serialized as a string.

        :param line: a string with serialized key-args pairs as "key1=value1;key2=value2;..."

        :return: a new ConfigParams object.
        """
        map = StringValueMap.from_string(line)
        return ConfigParams(map)

    @staticmethod
    def merge_configs(*configs: 'ConfigParams') -> 'ConfigParams':
        """
        Merges two or more ConfigParams into one. The following ConfigParams override previously defined parameters.

        :param configs: a list of ConfigParams objects to be merged.

        :return: a new ConfigParams object.
        """
        map = StringValueMap.from_maps(*configs)
        return ConfigParams(map)
