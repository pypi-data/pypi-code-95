# -*- coding: utf-8 -*-
"""
    pip_services3_commons.config.NameResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Name resolver implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from .ConfigParams import ConfigParams
from ..refer.Descriptor import Descriptor


class NameResolver:
    """
    A helper class that allows to extract component name from configuration parameters.
    The name can be defined in "id", "name" parameters or inside a component descriptor.

    Examples:

    .. code-block:: python

        config = ConfigParams.fromTuples("descriptor", "myservice:connector:aws:connector1:1.0",
                                         "param1", "ABC",
                                         "param2", 123)

        name = NameResolver.resolve(config)
    """

    @staticmethod
    def resolve(config: ConfigParams, default_name: str = None) -> str:
        """
        Resolves a component name from configuration parameters.
        The name can be stored in "id", "name" fields or inside a component descriptor.
        If name cannot be determined it returns a defaultName.

        :param config: configuration parameters that may contain a component name.

        :param default_name: (optional) a default component name.

        :return: resolved name or default name if the name cannot be determined.
        """
        name = config.get_as_nullable_string("name")
        name = name if not (name is None) else config.get_as_nullable_string("id")

        if name is None:
            descriptor_str = config.get_as_nullable_string("descriptor")
            descriptor = Descriptor.from_string(descriptor_str)
            if not (descriptor is None):
                name = descriptor.get_name()

        return name if not (name is None) else default_name
