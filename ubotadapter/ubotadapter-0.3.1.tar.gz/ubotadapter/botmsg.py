from typing import List, Generator, Any, Callable


class Keyboard:
    def __init__(self,
                 buttons: List[List[str]],
                 n_cols: int = 1,
                 in_line: bool = False,
                 one_time: bool = False):
        self.buttons = buttons
        self.n_cols = n_cols
        self.in_line = in_line
        self.one_time = one_time

    def rows(self) -> Generator[List[str], Any, None]:
        return (row for row in self.buttons)

    def __iter__(self) -> Generator[List[str], Any, None]:
        yield self.rows

    def serialize_buttons(self, serializer: Callable):
        return ([serializer(button) for button in row] for row in self.buttons)


class BotMessage:
    __slots__ = ('is_reply_to_message', 'reply_to_message', 'data', '_text', '_keyboard')

    def __init__(self, text: str,
                 is_reply_to_message: bool = False,
                 keyboard: Keyboard = None,
                 reply_to_message=None,
                 **kwargs):
        self._text = text
        self._keyboard = keyboard
        self.is_reply_to_message = is_reply_to_message
        self.reply_to_message = reply_to_message
        self.data = kwargs

    @property
    def content(self):
        return self.text

    @property
    def text(self) -> str:
        return self._text

    @property
    def keyboard(self) -> Keyboard:
        return self._keyboard

    @property
    def has_content(self) -> bool:
        return bool(self._text or self._keyboard)


class BotReplies:
    __slots__ = ('_messages',)

    def __init__(self):
        self._messages: List[BotMessage] = []

    def __iter__(self) -> Generator[BotMessage, Any, None]:
        return (m for m in self._messages)

    def __getitem__(self, idx) -> BotMessage:
        return self._messages[idx]

    @property
    def count(self) -> int:
        return len(self._messages)

    def add(self, message: BotMessage):
        self._messages.append(message)

    def add_text(self, text: str):
        self._messages.append(BotMessage(text))

    def clear(self):
        self._messages.clear()
