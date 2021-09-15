import platform
from collections import deque

from .getch import getch


class Input:
    _buffer = deque()
    _system = platform.system()

    def __call__(self, prompt=""):
        if prompt != "":
            print(prompt, end="", flush=True)

        while True:
            char = getch()

            if char == "\r":
                break
            elif char == "\x03":
                self._buffer.clear()
                raise KeyboardInterrupt

            if self._system == "Windows":
                if char == "\x08":
                    if len(self._buffer) > 0:
                        self._buffer.pop()
                        len_ = len(self._buffer) + len(prompt) + 1
                        out = "\r" + " "*len_ + "\r" + prompt + "".join(self._buffer)
                        print(out, end="", flush=True)
                else:
                    self._buffer.append(char)
                    print(char, end="", flush=True)
            else:
                if char == "\x7f":
                    if len(self._buffer) > 0:
                        self._buffer.pop()
                        len_ = len(self._buffer) + len(prompt) + 1
                        out = "\r" + " "*len_ + "\r" + prompt + "".join(self._buffer)
                        print(out, end="", flush=True)
                else:
                    self._buffer.append(char)
                    print(char, end="", flush=True)

        print()
        string = ""

        while len(self._buffer) > 0:
            string += self._buffer.popleft()

        return string

    @classmethod
    def get_input_buffer(cls):
        return cls._buffer.copy()


buffer_input = Input()
