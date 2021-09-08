from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import Type, Union

from ubotadapter import InboundMessage, InboundMessageFactory, ReplyToMessage
from .user import TelegramUser


class TGReplyToMessage(ReplyToMessage):
    @property
    def inbound(self) -> TGInboundMessage:
        return self._inbound

    @cached_property
    def _from(self) -> dict:
        return self.get('from')

    @property
    def text(self) -> Union[str, None]:
        return self.get('text')

    @property
    def message_id(self) -> Union[int, str]:
        return self.get('message_id')

    @property
    def chat_id(self) -> Union[int, str]:
        return self.get('chat', {}).get('id', None)

    @property
    def user_id(self) -> Union[int, str]:
        return self._from.get('id', None)

    @property
    def user_visual_name(self) -> Union[str, None]:
        return self._from.get('username', None)

    @property
    def date_raw(self) -> Union[int, None]:
        return self.get('date', None)


class TGInboundMessage(InboundMessage):
    _UserClass = TelegramUser
    _ReplyMessageClass = TGReplyToMessage

    @property
    def message(self) -> dict:
        return self['message']

    @property
    def user_data(self) -> dict:
        return self._from

    @property
    def _from(self) -> dict:
        return self.message['from']

    @property
    def text_only(self) -> str:
        return self.message.get('text', '')

    @property
    def sticker(self) -> dict:
        return self.message.get('sticker', {})

    @property
    def text(self) -> str:
        return self.message.get('text', self.sticker.get('emoji', ''))

    @property
    def user_id(self) -> int:
        return self._from['id']

    @property
    def user_id_url(self) -> str:
        return f'@{self._from["username"]}'

    @property
    def chat_id(self) -> str:
        return self.message['chat']['id']

    @property
    def message_id(self) -> str:
        return self.message['message_id']

    @property
    def secret_code(self) -> None:
        return None

    @property
    def is_private(self) -> bool:
        return self.message.get('type', None) == 'private'

    @property
    def date_raw(self) -> Union[int, None]:
        return self.message.get('date', None)

    @property
    def reply_to_msg_raw(self) -> Union[dict, None]:
        return self.message.get('reply_to_message', {})


class TGInboundCallbackQuery(TGInboundMessage):
    @property
    def callback_query(self):
        return self['callback_query']

    @property
    def message(self):
        return self.callback_query['message']

    @property
    def _from(self):
        return self.callback_query['from']

    @property
    def text(self) -> str:
        data = self.callback_query['data']
        if isinstance(data, str):
            return data
        return ''


class TGInboundMessageFactory(InboundMessageFactory):
    def get_inbound_message_class(self, data) -> Type[InboundMessage]:
        if 'callback_query' in data:
            return TGInboundCallbackQuery
        return self._default_inbound_message_class
