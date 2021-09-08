import concurrent.futures
import os
import json
import pathlib
import queue
import threading
import urllib.request
from .LAUNCHER import Launcher
import logging.handlers
import logging
import typing

ALL = [
    "JsonHandler",
    "Launcher",
    "LogHandler",
    "format_root",
    "DownloadFromJson",
    "callback_type",
    "ALL",
    "Formatter",
]

__all__ = ALL

callback_type = typing.Callable[[str, logging.LogRecord], None]

Formatter = logging.Formatter(
    "%(asctime)s:[%(levelname)s]:%(threadName)s :: %(message)s",
    datefmt="%d-%m-%Y %I:%M:%S",
)


class JsonHandler:
    def __init__(self, file: typing.Optional[str] = None):
        self.file = file

    def load(self) -> dict:
        with open(self.file, "r") as loaded:
            return json.load(loaded)

    def dump(self, store: dict) -> None:
        with open(self.file, "w") as loaded:
            return json.dump(store, loaded, indent=4)

    def __call__(self, raw: str) -> dict:
        return json.loads(raw)

    def __str__(self) -> str:
        return self.file

    def parse_url(self, raw_link: str) -> dict:
        with urllib.request.urlopen(raw_link) as raw:
            return json.loads(raw.read().decode())

    def close(self) -> None:
        os.remove(self.file)

    def __enter__(self):
        return self.load()

    def __exit__(self, *_):
        self.close()


def format_root() -> logging.Logger:
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)

    root.addHandler(logging.StreamHandler(None)) if len(root.handlers) == 0 else None

    handler = root.handlers[0]
    handler.setLevel(logging.DEBUG)

    handler.setFormatter(Formatter)

    return root


class DownloadFromJson:
    def __init__(self, save: str, raw: dict):
        self.linear = queue.Queue()

        self._safe = threading.Lock()
        self._count, self._done = 0, False

        self.linear.put(
            (raw, "")
        )

        self.pointer = save

        if not os.path.isdir(self.pointer):
            raise NotADirectoryError(f"{self.pointer} is not a directory")

        self._failed = False

    def initiate(self):
        while self.linear.qsize():
            tree, rel = self.linear.get()  # definitely tree is of dict type

            for name in tree:
                relative = os.path.join(rel, name)
                absolute = os.path.join(self.pointer, relative)

                if type(tree[name]) != dict:
                    None if os.path.exists(absolute) else self._grab(tree[name], absolute)
                    continue

                None if os.path.exists(absolute) else os.mkdir(absolute)
                self.linear.put(
                    (tree[name], relative)
                )

        with self._safe:
            self._done = True
            self._finished() if self._count == 0 else None

    def _grab(self, *_):
        with self._safe:
            self._count += 1

    def _parse(self, *_):
        with self._safe:
            self._count -= 1

    def _finished(self):
        ...


class LogHandler(logging.Handler):
    def __init__(
            self,
            level=logging.DEBUG,
            formatter=logging.Formatter(
                "%(asctime)s:[%(levelname)s]:%(threadName)s :: %(message)s",
                datefmt="%d-%m-%Y %I:%M:%S",
            ),
            emit_record: typing.Callable = None,
            emit_id: typing.Callable = None,
    ):
        super().__init__(level)
        self._record, self._emit_id = emit_record, emit_id

        self.setFormatter(formatter)

    def register_callbacks(
            self, emit_record: typing.Callable = None, emit_id: typing.Callable = None
    ):
        self._record = emit_record if emit_record else self._record
        self._emit_id = emit_id if emit_id else self._emit_id

    def emit(self, record: logging.LogRecord):
        formatted = self.format(record)

        self._record(formatted, record) if self._record else None

        return record
