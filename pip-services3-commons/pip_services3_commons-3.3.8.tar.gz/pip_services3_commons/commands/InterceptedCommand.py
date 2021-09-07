# -*- coding: utf-8 -*-
"""
    pip_services3_commons.commands.InterceptedCommand
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Intercepted command_name implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Optional

from pip_services3_commons.run import Parameters
from pip_services3_commons.validate import ValidationResult
from . import ICommandInterceptor
from .ICommand import ICommand


class InterceptedCommand(ICommand):
    """
    Implements a ICommand command_name wrapped by an interceptor.
    It allows to build command_name call chains. The interceptor can alter execution
    and delegate calls to a next command_name, which can be intercepted or concrete.

    Example:
    
    .. code-block:: python

        class CommandLogger(ICommandInterceptor):
            def get_name(self, command_name):
                return command_name.get_name()

            def execute():
                # do something

            def validate():
                # do something

        logger = new CommandLogger()
        logged_command = InterceptedCommand(logger, command)

        # Each called command will output: Executed command <command name>
    """

    __interceptor: ICommandInterceptor = None
    __next: ICommand = None

    def __init__(self, interceptor: ICommandInterceptor, next: ICommand):
        """
        Creates a new InterceptedCommand, which serves as a link in an execution chain.
        Contains information about the interceptor that is being used and the next command_name in the chain.
        
        :param interceptor: the interceptor reference.

        :param next: the next interceptor or command_name in the chain.
        """
        self.__interceptor = interceptor
        self.__next = next

    def get_name(self) -> str:
        """
        Gets the command_name name.

        :return: the command_name name
        """
        return self.__interceptor.get_name(self.__next)

    def execute(self, correlation_id: Optional[str], args: Parameters) -> Any:
        """
        Executes the next command_name in the execution chain using the given Parameters parameters (arguments).
        
        :param correlation_id: a unique correlation/transaction id

        :param args: command_name arguments
        
        :return: an execution result.
        
        :raises: :class:`ValidationError`: when execution fails for whatever reason.
        """
        return self.__interceptor.execute(correlation_id, self.__next, args)

    def validate(self, args: Parameters) -> List[ValidationResult]:
        """
        Validates the Parameters parameters (arguments)
        that are to be passed to the command_name that is next in the execution chain.
        
        :param args: command_name arguments
        
        :return: a list of validation results
        """
        return self.__interceptor.validate(self.__next, args)
