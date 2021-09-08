from enum import Enum


class BotReplyException(Exception):
    pass


# region Processing

class BotProcessStatus(Enum):
    ok = 0
    unknown_error = 1
    inbound_error = 2
    filter_not_passed = 10
    wrong_secret = 100


class BotProcessResult:
    __slots__ = ('status', 'data', 'exception')

    def __init__(self, status: BotProcessStatus, data=None, exception: Exception = None):
        self.status = status
        self.data = data
        self.exception = exception

    def __str__(self):
        return [getattr(self, k) for k in self.__slots__]


class BotHandleStatus(Enum):
    ok = 0
    error = 1
    partial_error = 2


class BotReplyStatus(Enum):
    ok = 0
    unknown_error = 1
    unknown_exception = 2
    no_permission = 90


class BotReplyResult:
    __slots__ = ('status', 'data', 'exception')

    def __init__(self, status: BotReplyStatus, data=None, exception: Exception = None):
        self.status = status
        self.data = data
        self.exception = exception

    def __str__(self):
        return [getattr(self, k) for k in self.__slots__]


class BotHandleResult:
    __slots__ = ('_process_result', '_replies_result')

    def __init__(self):
        self._process_result = None
        self._replies_result = []

    @property
    def process_result(self) -> BotProcessResult:
        return self._process_result

    @process_result.setter
    def process_result(self, value: BotProcessResult):
        self._process_result = value

    @property
    def reply_result(self) -> BotReplyResult:
        return self._replies_result[-1]

    @reply_result.setter
    def reply_result(self, value: BotReplyResult):
        self._replies_result.append(value)

    @property
    def status(self) -> BotHandleStatus:
        if self.process_result.status == BotProcessStatus.ok:
            if any(result.status != BotReplyStatus.ok for result in self._replies_result):
                return BotHandleStatus.partial_error
            return BotHandleStatus.ok
        return BotHandleStatus.error

    @property
    def is_ok(self) -> bool:
        return self.status == BotHandleStatus.ok

    @property
    def no_replies(self) -> bool:
        return len(self._replies_result) == 0

    def report(self):
        return {
            'result': self.is_ok,
            'process': self._process_result.__str__(),
            'replies': [r.__str__() for r in self._replies_result]
        }
