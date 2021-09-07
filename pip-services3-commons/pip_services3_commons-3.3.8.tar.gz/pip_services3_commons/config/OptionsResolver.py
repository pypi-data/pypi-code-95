# -*- coding: utf-8 -*-
"""
    pip_services3_commons.config.OptionsResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Options resolver implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.config.ConfigParams import ConfigParams


class OptionsResolver:
    """
    A helper class to parameters from "options" configuration section.

    Example:

    .. code-block:: python

        config = ConfigParams.fromTuples(
          ...
          "options.param1", "ABC",
          "options.param2", 123)

        options = OptionsResolver.resolve(config)
    """

    @staticmethod
    def resolve(config: ConfigParams, config_as_default: bool = False) -> ConfigParams:
        """
        Resolves an "options" configuration section from component configuration parameters.

        :param config: configuration parameters

        :param config_as_default: (optional) When set true the method returns the entire parameter
                                  set when "options" section is not found. Default: false

        :return: configuration parameters from "options" section
        """
        options = config.get_section("options")

        if len(options) == 0 and config_as_default:
            options = config

        return options
