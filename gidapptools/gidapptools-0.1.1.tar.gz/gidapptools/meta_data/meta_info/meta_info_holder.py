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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, ClassVar
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
import importlib.metadata
from psutil import virtual_memory
from itertools import cycle
from gidapptools.errors import NotBaseInitFileError
from urlextract import URLExtract
import attr
import requests
from yarl import URL
from tzlocal import get_localzone
from gidapptools.utility import OperatingSystem, memory_in_use, handle_path, utc_now

from gidapptools.types import general_path_type

# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST

# endregion[Imports]

# region [TODO]

# - Make into a class

# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

def url_converter(in_url: str) -> Optional[URL]:
    if in_url is None:
        return in_url
    return URL(in_url)


@attr.s(auto_attribs=True, auto_detect=True, kw_only=True, frozen=True)
class MetaInfo:
    name: str = attr.ib(default=None)
    author: str = attr.ib(default=None)
    version: str = attr.ib(default=None)
    url: URL = attr.ib(converter=url_converter, default=None)
    pid: int = attr.ib(factory=os.getpid)
    os: OperatingSystem = attr.ib(factory=OperatingSystem.determine_operating_system)
    os_release: str = attr.ib(factory=platform.release)
    python_version: str = attr.ib(factory=platform.python_version)
    started_at: datetime = attr.ib(factory=utc_now)
    base_mem_use: int = attr.ib(default=memory_in_use())

    def as_dict(self, encoder=None) -> dict[str, Any]:
        if encoder is None:
            encoder = None
        return attr.asdict(self, recurse=False, value_serializer=encoder)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
