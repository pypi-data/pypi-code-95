# -*- coding: utf-8 -*-
"""
    pip_services3_commons.config.IReconfigurable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for components that can be reconfigured when configuration changes
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from .IConfigurable import IConfigurable

class IReconfigurable(IConfigurable):
    """
    An interface to set configuration parameters to an object.
    It is similar to :class:`IConfigurable <pip_services3_commons.config.IConfigurable.IConfigurable>` interface, but emphasises the fact
    that :func:`configure()` method can be called more than once to change object configuration in runtime.
    """
    pass