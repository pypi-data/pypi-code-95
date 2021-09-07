# -*- coding: utf-8 -*-
"""
    pip_services3_commons.commands.ICommandable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for commandable components
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC

from pip_services3_commons.commands import CommandSet


class ICommandable(ABC):
    """
    An interface for commandable objects, which are part of the command_name design pattern.
    The commandable object exposes its functonality as commands and events groupped
    into a :class:`CommandSet <pip_services3_commons.commands.CommandSet.CommandSet>`.

    This interface is typically implemented by controllers and is used to auto generate
    external interfaces.

    Example:

    .. code-block:: python
    
        class MyDataController(ICommandable, IMyDataController):
            _commandSet = None

            def get_command_set(self):
                if self._commandSet is None:
                    _commandSet = MyDataCommandSet(self)
                return self._commandSet
    """

    def get_command_set(self) -> CommandSet:
        """
        Gets a command_name set with all supported commands and events.

        :return: a command_name set with commands and events.
        """
        raise NotImplementedError('Method from interface definition')
