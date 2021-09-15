import threading
from collections import deque

from .buffer_input import Input


class TryInput(Input):
    def __init__(self):
        super().__init__()

    def __call__(self, prompt="", *, cast=None, default=None):
        if cast is None:
            return super().__call__(prompt)

        try:
            return cast(super().__call__(prompt))
        except ValueError:
            return default


class ThreadSafeInput(Input):
    _input_lock = threading.Lock()
    _buffer = deque()

    def __init__(self):
        super().__init__()

    def __call__(self, prompt):
        with self._input_lock:
            return super().__call__(prompt)


class ThreadSafeTryInput(TryInput):
    _input_lock = ThreadSafeInput._input_lock
    _buffer = ThreadSafeInput._buffer

    def __init__(self):
        super().__init__()

    def __call__(self, prompt="", *, cast=None, default=None):
        with self._input_lock:
            return super().__call__(prompt, cast=cast, default=default)


try_input = TryInput()
safe_input = ThreadSafeInput()
safe_try_input = ThreadSafeTryInput()
