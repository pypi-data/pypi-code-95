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
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class _BaseGidEnum(Enum):
    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, str):
            mod_value = value.casefold()
            for member_name, member_value in cls.__members__.items():
                if member_name.casefold() == mod_value or member_value == mod_value:
                    return cls(member_value)
                if isinstance(member_value, str) and member_value.casefold() == mod_value:
                    return cls(member_value)
        return super()._missing_(value)

    @classmethod
    def is_in_value(cls, other: Any) -> bool:
        return other in {member.value for name, member in cls.__members__.items()}


class OperatingSystem(_BaseGidEnum):
    WINDOWS = auto()
    LINUX = auto()
    MAC_OS = auto()
    JYTHON = auto()
    UNDETERMINED = auto()

    @classmethod
    @property
    def default_member(cls) -> "OperatingSystem":
        return cls.UNDETERMINED

    @classmethod
    @property
    def member_str_map(cls) -> dict[str, "OperatingSystem"]:
        return {'windows': cls.WINDOWS,
                'linux': cls.LINUX,
                'darwin': cls.MAC_OS,
                'java': cls.JYTHON}

    @classmethod
    def str_to_member(cls, os_string: str) -> "OperatingSystem":
        def _normalize_name(in_name: str) -> str:
            mod_name = in_name.casefold()
            mod_name = mod_name.strip()
            return mod_name

        return cls.member_str_map.get(_normalize_name(os_string), cls.default_member)

    @classmethod
    def determine_operating_system(cls) -> "OperatingSystem":
        os_string = platform.system()

        return cls.str_to_member(os_string)

    def __str__(self) -> str:
        return self.name.title()


class NamedMetaPath(_BaseGidEnum):
    DATA = 'user_data_dir'
    LOG = 'user_log_dir'
    CACHE = 'user_cache_dir'
    CONFIG = 'user_config_dir'
    STATE = 'user_state_dir'
    SITE_DATA = 'site_data_dir'
    SITE_CONFIG = 'site_config_dir'
    TEMP = 'user_temp_dir'


class MiscEnum(Enum):
    NOTHING = auto()


class EnvName(str, Enum):
    APP_NAME = 'APP_NAME'
    APP_AUTHOR = 'APP_AUTHOR'
    LOG_DIR = 'APP_LOG_DIR'


# region[Main_Exec]


if __name__ == '__main__':
    x = 'something'
    print(NamedMetaPath.is_in_value(x))

# endregion[Main_Exec]
