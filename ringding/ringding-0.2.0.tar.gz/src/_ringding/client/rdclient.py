import logging
from typing import Dict

from _ringding.client.base import BaseClient
from _ringding.messages import (MessageResponse, Message,
                                MESSAGE_TYPE_REQUEST, ErrorResponse)
from ringding.datatypes import ServerError, NoAccessError


class RdClient(BaseClient):
    GENERIC_PARAMETER = '*'

    def on_message(self, message: Message):
        parameters = message.param or '{}'
        try:
            value = self._resolve_command(message.cmd, parameters)
        except Exception as error:
            self.send_message(ErrorResponse(message.id, str(error)))
            logging.exception(f'Exception occured while resolving command: {error}')
        else:
            if message.type == MESSAGE_TYPE_REQUEST:
                response = MessageResponse(message.id, value)
                self.send_message(response)

    def _resolve_command(self, command: str, parameters: Dict):
        entry = self._api_entry
        commands = command.split('.')

        while commands:
            current_command = commands.pop(0)
            if current_command.startswith('_'):
                raise NoAccessError(
                    f'You are not allowed to access the private member '
                    f'{command}.')
            try:
                attribute, parameter_name = current_command.split('(')
            except ValueError:
                entry = getattr(entry, current_command)
                continue
            else:
                parameter_name = parameter_name.strip('()')
                parameter_data = {}
                if parameter_name:
                    if parameter_name == self.GENERIC_PARAMETER:
                        parameter_data = parameters
                    elif parameter_name.startswith(self.GENERIC_PARAMETER):
                        parameter_data = parameters[
                            parameter_name.strip(self.GENERIC_PARAMETER)]
                    else:
                        for param_name in parameter_name.split(','):
                            param_name = param_name.strip()
                            parameter_data[param_name] = parameters[param_name]
                try:
                    func = getattr(entry, attribute)
                    if hasattr(func, '__tracked__'):
                        entry = func(**parameter_data, client=self)
                        continue
                    entry = func(**parameter_data)
                except Exception as error:
                    raise ServerError(
                        f'Error while executing {attribute}({parameter_data}) of '
                        f'{command}: {error}')

        return entry


def tracked(func):
    """
    Decorator to inject the current client to a function.

    The function will receive an additional parameter "client" that can be used to
    identify the client.

    Example:
        >>> @tracked
            def greet_client(client: RdClient):
                return f'Hello {client}'
    """
    func.__tracked__ = True
    return func
