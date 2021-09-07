# -*- coding: utf-8 -*-
"""
    pip_services3_commons.config.IConfigurable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for components that require configuration
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC

from pip_services3_commons.config.ConfigParams import ConfigParams


class IConfigurable(ABC):
    """
     An interface to set configuration parameters to an object.

     It can be added to any existing class by implementing a single :func:`configure()` method.

     If you need to emphasis the fact that :func:`configure()` method can be called multiple times
     to change object configuration in runtime, use :class:`IReconfigurable <pip_services3_commons.config.IReconfigurable.IReconfigurable>` interface instead.

     Example:

    .. code-block:: python

         class MyClass(IConfigurable):
            _myParam = "default args"

         def configure(self, config):
            self._myParam = config.get_as_string_with_default("options.param", myParam)
    """

    def configure(self, config: ConfigParams):
        """
        Configures object by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        raise NotImplementedError('Method from interface definition')
