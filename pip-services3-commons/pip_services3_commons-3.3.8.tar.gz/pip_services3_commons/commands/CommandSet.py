# -*- coding: utf-8 -*-
"""
    pip_services3_commons.commands.CommandSet
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Command set implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Dict, Optional, Any

from pip_services3_commons.commands import IEvent, ICommand, IEventListener
from pip_services3_commons.run import Parameters
from . import ICommandInterceptor
from .InterceptedCommand import InterceptedCommand
from ..data.IdGenerator import IdGenerator
from ..errors.BadRequestException import BadRequestException
from ..validate.ValidationException import ValidationException
from ..validate.ValidationResult import ValidationResult
from ..validate.ValidationResultType import ValidationResultType


class CommandSet:
    """
    Contains a set of commands and events supported by a ICommandable commandable object.
    The CommandSet supports command_name interceptors to extend and the command_name call chain.

    CommandSets can be used as alternative commandable interface to a business object.
    It can be used to auto generate multiple external services for the business object
    without writing much code.

    Example:

    .. code-block:: python

        class MyDataCommandSet(CommandSet):
            _controller = None

            def __init__(self, controller):
                super().__init__()

                self._controller = controller

                self.add_command(self._make_get_my_data_command())

            def _make_get_my_data_command(self):
                def handler(correlation_id, args):
                    param = args.get_as_string('param')
                    return self._controller.get_my_data(correlation_id, param)

                return Command(
                    "get_mydata",
                    None,
                    handler
                )

    See :class:`Command <pip_services3_commons.commands.Command.Command>`, :class:`Event <pip_services3_commons.commands.Event.Event>`, :class:`ICommandable <pip_services3_commons.commands.ICommandable.ICommandable>`
    """

    __commands: List[ICommand] = None
    __events: List[IEvent] = None
    __interceptors: List[ICommandInterceptor] = None

    def __init__(self):
        """
        Creates an empty CommandSet object.
        """
        self.__commands = []
        self.__events = []
        self.__interceptors = []

        self.__commands_by_name: Dict[str, ICommand] = {}
        self.__events_by_name: Dict[str, IEvent] = {}

    def get_commands(self) -> List[ICommand]:
        """
        Gets all commands registered in this command_name set.

        :return: :class:`ICommand <pip_services3_commons.commands.ICommand.ICommand>` list with all commands supported by component.
        """
        return self.__commands

    def get_events(self) -> List[IEvent]:
        """
        Gets all events registered in this command_name set.

        :return: :class:`ICommand <pip_services3_commons.commands.ICommand.ICommand>` list with all events supported by component.
        """
        return self.__events

    def find_command(self, command_name: str) -> Optional[ICommand]:
        """
        Searches for a command_name by its name.
        
        :param command_name: the name of the command_name to search for.

        :return: the command_name, whose name matches the provided name.
        """
        if command_name in self.__commands_by_name:
            return self.__commands_by_name[command_name]
        else:
            return None

    def find_event(self, event_name: str) -> Optional[IEvent]:
        """
        Searches for an event_name by its name in this command_name set.
        
        :param event_name: the name of the event_name to search for.

        :return: the event_name, whose name matches the provided name.
        """
        if event_name in self.__events_by_name:
            return self.__events_by_name[event_name]
        else:
            return None

    def __build_command_chain(self, command: ICommand):
        """
        Builds execution chain including all intercepters and the specified command_name.

        :param command: the command_name to build a chain.
        """
        next_command = command
        for intercepter in reversed(self.__interceptors):
            next_command = InterceptedCommand(intercepter, next_command)
        self.__commands_by_name[next_command.get_name()] = next_command

    def __rebuild_all_command_chains(self):
        """
        Rebuilds execution chain for all registered commands.
        This method is typically called when interceptors are changed.
        Because of that it is more efficient to register interceptors
        before registering commands (typically it will be done in abstract classes).
        However, that performance penalty will be only once during creation time.
        """
        self.__commands_by_name = {}
        for command in self.__commands:
            self.__build_command_chain(command)

    def add_command(self, command: ICommand):
        """
        Adds a ICommand command_name to this command_name set.
        
        :param command: a command_name instance to be added
        """
        self.__commands.append(command)
        self.__build_command_chain(command)

    def add_commands(self, commands: List[ICommand]):
        """
        Adds multiple :class:`ICommand <pip_services3_commons.commands.ICommand.ICommand>` commands to this command_name set.
        
        :param commands: the array of commands to add.
        """
        for command in commands:
            self.add_command(command)

    def add_event(self, event: IEvent):
        """
        Adds an :class:`IEvent <pip_services3_commons.commands.IEvent.IEvent>` event_name to this command_name set.
        
        :param event: an event_name instance to be added
        """
        self.__events.append(event)
        self.__events_by_name[event.get_name] = event

    def add_events(self, events: List[IEvent]):
        """
        Adds multiple :class:`IEvent <pip_services3_commons.commands.IEvent.IEvent>` events to this command_name set.
        
        :param events: the array of events to add.
        """
        for event in events:
            self.add_event(event)

    def add_command_set(self, command_set: 'CommandSet'):
        """
        Adds all of the commands and events from specified CommandSet command_name set
        into this one.
        
        :param command_set: a commands set to add commands from
        """
        for command in command_set.get_commands():
            self.add_command(command)

        for event in command_set.get_events():
            self.add_event(event)

    def add_interceptor(self, interceptor: ICommandInterceptor):
        """
        Adds a :class:`ICommandInterceptor <pip_services3_commons.commands.ICommandInterceptorICommandInterceptor>` command_name interceptor to this command_name set.
        
        :param interceptor: an interceptor instance to be added.
        """
        self.__interceptors.append(interceptor)
        self.__rebuild_all_command_chains()

    def execute(self, correlation_id: Optional[str], command: str, args: Parameters) -> Any:
        """
        Executes a :class:`ICommand <pip_services3_commons.commands.ICommand.ICommand>` command_name specificed by its name.
        
        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param command: the name of that command_name that is to be executed.

        :param args: the parameters (arguments) to pass to the command_name for execution.
        
        :return: the execution result.
        
        :raises: ValidationException: when execution fails for any reason.
        """
        # Get command_name and throw error if it doesn't exist
        cref = self.find_command(command)
        if cref is None:
            raise BadRequestException(
                correlation_id,
                "CMD_NOT_FOUND",
                "Requested command_name does not exist"
            ).with_details("command_name", command)

        # Generate correlationId if it doesn't exist
        # Use short ids for now
        if correlation_id is None:
            correlation_id = IdGenerator.next_short()

        # Validate command_name arguments before execution and throw the 1st found error
        results = cref.validate(args)
        ValidationException.throw_exception_if_needed(correlation_id, results, False)

        # Execute the command_name.
        return cref.execute(correlation_id, args)

    def validate(self, command_name: str, args: Parameters) -> List[ValidationResult]:
        """
        Validates Parameters args for command_name specified by its name using defined schema.
        If validation schema is not defined than the methods returns no errors.
        It returns validation error if the command_name is not found.
        
        :param command_name: the name of the command_name for which the 'args' must be validated.

        :param args: the parameters (arguments) to validate.
        
        :return: an array of ValidationResults. If no command_name is found by the given
                 name, then the returned array of ValidationResults will contain a
                 single entry, whose type will be :class:`ValidationResultType.Error`.
        """
        cref = self.find_command(command_name)
        if cref is None:
            results = []
            results.append(
                ValidationResult(
                    None, ValidationResultType.Error,
                    "CMD_NOT_FOUND",
                    "Requested command_name does not exist"
                )
            )
            return results

        return cref.validate(args)

    def add_listener(self, listener: IEventListener):
        """
        Adds a :class:`IEventListener <pip_services3_commons.commands.IEventListener.IEventListener>` listener to receive notifications on fired events.

        :param listener: a listener to be added
        """
        for event in self.__events:
            event.add_listener(listener)

    def remove_listener(self, listener: IEventListener):
        """
        Removes previosly added :class:`IEventListener <pip_services3_commons.commands.IEventListener.IEventListener>` listener.

        :param listener: a listener to be removed
        """
        for event in self.__events:
            event.remove_listener(listener)

    def notify(self, correlation_id: Optional[str], event_name: str, args: Parameters):
        """
        Fires event_name specified by its name and notifies all registered
        :class:`IEventListener <pip_services3_commons.commands.IEventListener.IEventListener>` listeners

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param event_name: the name of the event_name that is to be fired.

        :param args: the event_name arguments (parameters).
        """
        e = self.find_event(event_name)
        if not (e is None):
            e.notify(correlation_id, args)
