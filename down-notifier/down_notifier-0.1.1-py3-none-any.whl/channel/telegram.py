from typing import List

from aiogram import Bot

from down_notifier.channel import BaseChannel


class TelegramChannel(BaseChannel):
    _chats: List[str]

    def __init__(self, name: str, message: str, **kwargs) -> None:
        super().__init__(name, message)
        self._bot = Bot(kwargs.get("token"))
        self._chats = kwargs.get("chats")  # type: ignore

    async def notify(self, url: str, status: int) -> None:
        for chat_id in self._chats:
            await self._bot.send_message(chat_id, self._message.format(url, status))
