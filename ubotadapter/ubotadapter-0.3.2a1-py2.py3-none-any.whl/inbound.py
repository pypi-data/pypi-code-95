from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from typing import Union, Type

from .botcontext import BotContext
from .botmsg import BotMessage
from .user import User


class ReplyToMessage(ABC):
    __slots__ = ('_data', '__dict__')

    def __init__(self, data, inbound):
        self._data = data
        self._inbound = inbound

    def get(self, key, default_value=None):
        return self._data.get(key, default_value)

    @property
    @abstractmethod
    def text(self) -> Union[str, None]:
        pass

    @property
    @abstractmethod
    def message_id(self) -> Union[int, str]:
        pass

    @property
    @abstractmethod
    def chat_id(self) -> Union[int, str]:
        pass

    @property
    @abstractmethod
    def user_id(self) -> Union[int, str]:
        pass

    @property
    @abstractmethod
    def user_visual_name(self) -> Union[str, None]:
        pass

    @property
    @abstractmethod
    def date_raw(self) -> Union[int, None]:
        pass

    @cached_property
    def date(self) -> Union[datetime, None]:
        return self.inbound.raw_date_converter(self.date_raw)

    @property
    @abstractmethod
    def inbound(self) -> InboundMessage:
        pass


class InboundMessage(ABC):
    __slots__ = ('_data', '__dict__', '__channel_type')

    _UserClass = User
    _ReplyMessageClass = ReplyToMessage

    def __init__(self, data):
        self._data = data
        self.validate()
        self._user = self._UserClass(self.user_id)
        self._context = None

    def __getitem__(self, key):
        return self._data[key]

    @property
    @abstractmethod
    def text(self) -> str:
        pass

    # region User
    @property
    def user(self) -> User:
        return self._user

    @property
    @abstractmethod
    def user_id(self) -> Union[int, str]:
        pass

    @property
    @abstractmethod
    def user_id_url(self) -> str:
        pass

    @property
    def user_visual_name(self) -> str:
        return self.user.visual_name or self.user.short_name

    @property
    def user_data(self):
        return None

    # endregion

    @property
    @abstractmethod
    def date_raw(self) -> Union[int, None]:
        pass

    @cached_property
    def date(self) -> Union[datetime, None]:
        return self.raw_date_converter(self.date_raw)

    def raw_date_converter(self, timestamp: int) -> Union[datetime, None]:
        """Default raw_date_converter_that can be overriden."""
        if timestamp:
            return datetime.fromtimestamp(timestamp)
        return None

    @property
    @abstractmethod
    def chat_id(self) -> Union[int, str]:
        pass

    @property
    @abstractmethod
    def message_id(self) -> Union[int, str]:
        pass

    @property
    def is_private(self) -> bool:
        return self.user_id == self.chat_id

    def get(self, key, default_value):
        return self._data.get(key, default_value)

    @property
    @abstractmethod
    def secret_code(self) -> str:
        pass

    @cached_property
    def reply_to_msg(self) -> Union[ReplyToMessage, None]:
        return self._ReplyMessageClass(self.reply_to_msg_raw, self)

    @property
    @abstractmethod
    def reply_to_msg_raw(self) -> Union[dict, None]:
        pass

    def validate(self):
        assert self.user_id is not None

    @property
    def context(self) -> BotContext:
        return self._context


class InboundProcessor(ABC):
    error_message_default = 'Inbound processing error'

    @staticmethod
    @abstractmethod
    def process(context: BotContext, inbound: InboundMessage):
        """context.replies.add(BotMessage(inbound.text))"""
        pass


class DefaultInboundProcessor(InboundProcessor):
    """Empty processor"""

    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        pass


class EchoInboundProcessor(InboundProcessor):
    """Echo processor"""

    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        context.replies.add(BotMessage(inbound.text))


class EchoReplyToInboundProcessor(InboundProcessor):
    """Echo processor"""

    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        context.replies.add(BotMessage(inbound.text, is_reply_to_message=True))


class EchoNameInboundProcessor(InboundProcessor):
    """Echo processor"""

    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        # text = f'{context.bot.get_user_visual_name(inbound)} is your name.'
        text = f'{inbound.user.visual_name} is your name.'
        context.replies.add(BotMessage(text))


class InboundMessageFactory:
    __slots__ = ('_default_inbound_message_class',)

    def __init__(self, default_inbound_message_class: Type[InboundMessage]):
        self._default_inbound_message_class = default_inbound_message_class

    def create(self, data) -> InboundMessage:
        inbound_message_class = self.get_inbound_message_class(data)
        return inbound_message_class(data)

    def get_inbound_message_class(self, data) -> Type[InboundMessage]:
        return self._default_inbound_message_class
