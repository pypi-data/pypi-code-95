from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from .botdebug import BotHandleResult
from .botmsg import BotReplies

if TYPE_CHECKING:
    from .botadapter import UBotAdapter
    from .inbound import InboundMessage


class BotContext(ABC):
    __slots__ = ('_replies', '_inbound', '_bot', '_handle_result')

    def __init__(self, bot: UBotAdapter):
        self._inbound = None
        self._bot = bot
        self._replies = BotReplies()
        self._handle_result = BotHandleResult()

    @property
    def replies(self) -> BotReplies:
        return self._replies

    @property
    def bot(self) -> UBotAdapter:
        return self._bot

    @property
    def bot_info(self):
        return self.bot.info

    @property
    def inbound(self) -> InboundMessage:
        return self._inbound

    @inbound.setter
    def inbound(self, value):
        self._inbound = value

    @property
    def handle_result(self) -> BotHandleResult:
        return self._handle_result

    def clear(self):
        self.replies.clear()
        self._handle_result.__init__()
