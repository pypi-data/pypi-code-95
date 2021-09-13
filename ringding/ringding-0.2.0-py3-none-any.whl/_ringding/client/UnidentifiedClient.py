from typing import Union, Type, Callable

from _ringding.client.base import BaseClient
from _ringding.messages import Message, ErrorResponse, MessageResponse
from ringding.datatypes import HandshakeError


class UnidentifiedClient(BaseClient):
    """
    This client is created after initial connection of a new client to the server.

    It accepts only a "handshake" as a message and then creates the final client
    based on the sent handshake data.
    """

    def __init__(self, entry_point: Union[object, Type[object]],
                 upgrade_client_fn: Callable):
        super().__init__(entry_point)
        self._upgrade_client_fn = upgrade_client_fn

    def on_message(self, message: Message):
        if not message.cmd == 'handshake':
            self.send_message(
                ErrorResponse(message.id, str('Missing proper handshake.')))
            raise HandshakeError('Client did not offer handshake. Rude.')
        try:
            self._upgrade_client_fn(self._client_data, message.param)
            self.send_message(MessageResponse(message.id, ''))
        except Exception as e:
            self.send_message(ErrorResponse(message.id, str(e)))
