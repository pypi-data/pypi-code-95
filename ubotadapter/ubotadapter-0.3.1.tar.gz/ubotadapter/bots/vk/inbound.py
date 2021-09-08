from __future__ import annotations

from functools import cached_property
from typing import Union

from ubotadapter import InboundMessage
from ubotadapter.inbound import ReplyToMessage
from .user import VKUser


class VKReplyToMessage(ReplyToMessage):
    @property
    def text(self) -> Union[str, None]:
        return self.get('text')

    @property
    def message_id(self) -> Union[int, str]:
        return self.get('id')

    @property
    def vk_conversation_message_id(self) -> int:
        return self.get('conversation_message_id')

    @property
    def chat_id(self) -> Union[int, str]:
        return self.get('peer_id')

    @property
    def user_id(self) -> Union[int, str]:
        return self.get('from_id')

    @property
    def user_visual_name(self) -> Union[str, None]:
        return f'@{self.user_id}'

    @property
    def date_raw(self) -> Union[int, None]:
        return self.get('date')

    @property
    def inbound(self) -> VKInboundMessage:
        return self._inbound


class VKInboundMessage(InboundMessage):
    _UserClass = VKUser
    _ReplyMessageClass = VKReplyToMessage

    @property
    def object(self):
        return self['object']

    @property
    def message(self):
        return self.object['message']

    @property
    def group_id(self) -> int:
        return self.get('group_id', None)

    @property
    def text(self) -> str:
        return self.message['text']

    @property
    def user_id(self) -> str:
        return self.message['from_id']

    @property
    def user_id_url(self) -> str:
        return f'@id{self.user_id}'

    @property
    def chat_id(self) -> str:
        return self.message['peer_id']

    @property
    def message_id(self) -> int:
        return self.message['id']

    @property
    def vk_conversation_message_id(self) -> int:
        return self.message['conversation_message_id']

    @property
    def secret_code(self) -> str:
        return self.get('secret', None)

    @property
    def date_raw(self) -> Union[int, None]:
        return self.message.get('date', None)

    @cached_property
    def reply_to_msg_raw(self) -> Union[dict, None]:
        return self.message.get('reply_message', None)
