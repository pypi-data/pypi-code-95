import dataclasses
import json
import logging
from typing import Dict, Union, Type, Any

from _ringding.messages import (MessageResponse, EventResponse, Message,
                                MESSAGE_TYPE_REQUEST, ErrorResponse)
from _ringding.ws.wsserver import WebsocketServer
from ringding.datatypes import ServerError, NoAccessError

GENERIC_PARAMETER = '*'
_RESPONSE_TYPES = Union[ErrorResponse, MessageResponse, EventResponse]


class _ApiEntry:
    pass


class _ApiEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return str(o)


class RdClient:
    def __init__(self, server: WebsocketServer, client_data: Dict,
                 entry_point: Union[object, Type[object]]):

        self._client_data = client_data
        self._server = server
        api_entry = _ApiEntry()
        initialized_entrypoint = entry_point
        if type(entry_point) == type:
            initialized_entrypoint = entry_point()
        api_entry.__dict__ = {
            initialized_entrypoint.__class__.__name__: initialized_entrypoint}
        self._api_entry = api_entry

    def send_message(self, message: _RESPONSE_TYPES):
        try:
            self._server.send_message(self._client_data,
                                      json.dumps(message, cls=_ApiEncoder))
        except Exception as error:
            self._server.send_message(self._client_data,
                                      json.dumps(ErrorResponse(message.id, str(error)),
                                                 cls=_ApiEncoder))

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
                    if parameter_name == GENERIC_PARAMETER:
                        parameter_data = parameters
                    elif parameter_name.startswith(GENERIC_PARAMETER):
                        parameter_data = parameters[
                            parameter_name.strip(GENERIC_PARAMETER)]
                    else:
                        for param_name in parameter_name.split(','):
                            param_name = param_name.strip()
                            parameter_data[param_name] = parameters[param_name]
                try:
                    entry = getattr(entry, attribute)(**parameter_data)
                except Exception as error:
                    raise ServerError(
                        f'Error while executing {attribute}({parameter_data}) of '
                        f'{command}: {error}')

        return entry
