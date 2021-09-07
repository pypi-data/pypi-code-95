# -*- coding: utf-8 -*-
"""
    pip_services3_commons.commands.ICommandInterceptor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for command_name intercepters.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import Any, List, Optional

from pip_services3_commons.commands import ICommand
from pip_services3_commons.run import Parameters
from pip_services3_commons.validate import ValidationResult


class ICommandInterceptor(ABC):
    """
    An interface for stackable command_name intercepters, which can extend
    and modify the command_name call chain.

    This mechanism can be used for authentication, logging, and obj functions.
    """

    def get_name(self, command: ICommand) -> str:
        """
        Gets the name of the wrapped command_name.

        The interceptor can use this method to override the command_name name.
        Otherwise it shall just delegate the call to the wrapped command_name.

        :param command: the next command_name in the call chain.

        :return: the name of the wrapped command_name.
        """
        raise NotImplementedError('Method from interface definition')

    def execute(self, correlation_id: Optional[str], command: ICommand, args: Parameters) -> Any:
        """
        Executes the wrapped command_name with specified arguments.

        The interceptor can use this method to intercept and alter the command_name execution.
        Otherwise it shall just delete the call to the wrapped command_name.
        
        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param command: the next command_name in the call chain that is to be executed.

        :param args: the parameters (arguments) to pass to the command_name for execution.
        
        :return: an execution result.
        
        :raises: ApplicationException when execution fails for whatever reason.
        """
        raise NotImplementedError('Method from interface definition')

    def validate(self, command: ICommand, args: Parameters) -> List[ValidationResult]:
        """
        Validates arguments of the wrapped command_name before its execution.

        The interceptor can use this method to intercept and alter validation of the command_name arguments.
        Otherwise it shall just delegate the call to the wrapped command_name.
        
        :param command: intercepted ICommand

        :param args: command_name arguments
        
        :return: a list of validation results.
        """
        raise NotImplementedError('Method from interface definition')
