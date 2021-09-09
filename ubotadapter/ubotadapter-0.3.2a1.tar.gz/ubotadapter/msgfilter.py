from abc import ABC, abstractmethod
from typing import List, Type, Union

from .inbound import InboundMessage, BotContext


class MessageFilter(ABC):
    __slots__ = ()

    @staticmethod
    @abstractmethod
    def is_true(context: BotContext, message: InboundMessage) -> bool:
        pass


class NotBotMessage(MessageFilter):
    @staticmethod
    def is_true(context: BotContext, message: InboundMessage) -> bool:
        return message.user_id != context.bot.config.bot_id


class MessageFilterManager:
    __slots__ = ('_message_filters',)

    def __init__(self, filters: List[Type[MessageFilter]]):
        self._message_filters = filters

    @property
    def message_filters(self) -> List[Type[MessageFilter]]:
        return self._message_filters

    def check(self, context: BotContext, message: InboundMessage) -> Union[Type[MessageFilter], None]:
        for msg_filter in self.message_filters:
            if not msg_filter.is_true(context, message):
                return msg_filter
        return None

    def add_filter(self, msg_filter: Type[MessageFilter]):
        self._message_filters.append(msg_filter)

    def remove_filters(self):
        self._message_filters = []
