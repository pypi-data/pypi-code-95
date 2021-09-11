"""
WiP.

Soon.
"""

# region [Imports]

import gc
import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import unicodedata
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict, UserDict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader

from gidapptools.utility import MiscEnum
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class PostInitMeta(ABCMeta):
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        instance = super(PostInitMeta, cls).__call__(*args, **kwargs)
        if hasattr(instance, "_post_init"):
            instance._post_init()
        return instance


class KwargDict(UserDict, metaclass=PostInitMeta):
    # pylint: disable=useless-super-delegation
    def __init__(self, base_defaults: dict = None, **kwargs) -> None:
        super().__init__(base_defaults, **kwargs)

    def get_kwargs_for(self, target_class: object, defaults: dict[str, Any] = None, exclude: Iterable[str] = None, overwrites: dict[str, Any] = None) -> Optional[dict[str, Any]]:
        defaults = {} if defaults is None else defaults
        overwrites = {} if overwrites is None else overwrites
        exclude = set() if exclude is None else set(exclude)
        kwarg_names = [name for name, obj in inspect.signature(target_class).parameters.items() if obj.kind is not obj.VAR_KEYWORD]

        _kwargs = {}
        for name in kwarg_names:
            if name in exclude:
                continue
            if name in overwrites:
                value = overwrites.get(name)
            else:
                value = self.get(name, defaults.get(name, MiscEnum.NOTHING))

            if value is MiscEnum.NOTHING:
                continue
            _kwargs[name] = value
        return _kwargs

    def get_many(self, keys: Union[list[str], dict[str, Any]]) -> dict[str, Any]:
        keys = keys if isinstance(keys, dict) else {key: None for key in keys}
        result = {}
        for key in keys:
            result[key] = self.get(key, keys.get(key, None))
        return result


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
