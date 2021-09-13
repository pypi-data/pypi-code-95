import dataclasses
import json
from typing import Dict, Union, Type, Optional, Any

from _ringding.messages import (ErrorResponse, MessageResponse, EventResponse, Message)
from _ringding.ws.wsserver import WebsocketServer


class _ApiEntry:
    pass


class _ApiEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return str(o)


class BaseClient:
    RESPONSE_TYPES = Union[ErrorResponse, MessageResponse, EventResponse]

    def __init__(self, entry_point: Union[object, Type[object]]):

        api_entry = _ApiEntry()
        initialized_entrypoint = entry_point
        if type(entry_point) == type:
            initialized_entrypoint = entry_point()
        api_entry.__dict__ = {
            initialized_entrypoint.__class__.__name__: initialized_entrypoint}
        self._api_entry = api_entry
        self._client_data: Dict = {}
        self._server: Optional[WebsocketServer] = None

    def get_json_encoder(self) -> Type[json.JSONEncoder]:
        return _ApiEncoder

    def send_message(self, message: 'BaseClient.RESPONSE_TYPES'):
        try:
            self._server.send_message(self._client_data,
                                      json.dumps(message, cls=self.get_json_encoder()))
        except Exception as error:
            self._server.send_message(self._client_data,
                                      json.dumps(ErrorResponse(message.id, str(error)),
                                                 cls=self.get_json_encoder()))

    def on_message(self, message: Message):
        pass

    def connect_client(self, server: WebsocketServer, client_data: Dict):
        self._client_data = client_data
        self._server = server
