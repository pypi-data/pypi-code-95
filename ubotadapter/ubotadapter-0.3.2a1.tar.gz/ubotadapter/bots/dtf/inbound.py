from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import Union

from deteefapi import WebhookComment, DeteefAPI
from deteefapi.webhook import CommentCreator

from ubotadapter import InboundMessage, ReplyToMessage
from .user import DTFUser


class DTFReplyToMessage(ReplyToMessage):
    @property
    def data(self) -> WebhookComment:
        return self._data

    @property
    def text(self) -> Union[str, None]:
        return self.data.text

    @property
    def message_id(self) -> Union[int, str]:
        return self.data.id

    @property
    def chat_id(self) -> Union[int, str]:
        return self.inbound.chat_id

    @property
    def user_id(self) -> Union[int, str]:
        return self.data.creator.id

    @property
    def user_visual_name(self) -> Union[str, None]:
        return self.data.creator.name

    @property
    def date_raw(self) -> None:
        return None

    @property
    def inbound(self) -> DTFInboundMessage:
        return self._inbound


class DTFInboundMessage(InboundMessage):
    _UserClass = DTFUser
    _ReplyMessageClass = DTFReplyToMessage

    @property
    def user_id(self) -> int:
        return self._comment.creator.id

    @property
    def user_id_url(self) -> str:
        return DeteefAPI.get_user_url(user_id=self.user_id, name=self._comment.creator.name)

    @property
    def chat_id(self) -> int:
        return self._comment.content.id

    @property
    def message_id(self) -> int:
        return self._comment.id

    @property
    def secret_code(self) -> str:
        # TODO: implement
        return ''

    @property
    def text(self) -> str:
        return self._comment.text

    @cached_property
    def _comment(self) -> WebhookComment:
        return WebhookComment(self._data.get('data', self._data))

    @property
    def user_data(self) -> CommentCreator:
        return self._comment.creator

    @property
    def date_raw(self) -> Union[int, None]:
        return self._comment._data.get('date')

    def raw_date_converter(self, timestamp: str) -> datetime:
        return datetime.fromisoformat(timestamp)

    @property
    def reply_to_msg_raw(self) -> WebhookComment:
        return self._comment.reply_to
