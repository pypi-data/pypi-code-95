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
from tempfile import TemporaryDirectory, gettempdir, gettempprefix
import tempfile
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from importlib.metadata import metadata, distributions
from contextlib import contextmanager, asynccontextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from urlextract import URLExtract
from yarl import URL
import psutil
from gidapptools.types import general_path_type
from appdirs import AppDirs
from uuid import uuid4
from gidapptools.utility.enums import NamedMetaPath
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def abstract_class_property(func):
    return property(classmethod(abstractmethod(func)))


def utc_now():
    return datetime.now(tz=timezone.utc)


def handle_path(path: Optional[general_path_type]):
    if path is None:
        return path
    return Path(path).resolve()


def memory_in_use():
    memory = psutil.virtual_memory()
    return memory.total - memory.available


def meta_data_from_path(in_path: Path) -> dict[str, Any]:
    _init_module = inspect.getmodule(None, in_path)
    _metadata = metadata(_init_module.__package__)
    return {k.casefold(): v for k, v in _metadata.items()}


def mark_appdir_path(func):
    func._appdir_path_type = NamedMetaPath(func.__name__)
    return func


class PathLibAppDirs(AppDirs):
    mark_path = mark_appdir_path

    def __init__(self,
                 appname: str,
                 appauthor: str = None,
                 version: str = None,
                 roaming: bool = True,
                 multipath: bool = False) -> None:
        super().__init__(appname=appname, appauthor=appauthor, version=version, roaming=roaming, multipath=multipath)

    @mark_appdir_path
    def user_data_dir(self) -> Path:
        return Path(super().user_data_dir)

    @mark_appdir_path
    def user_log_dir(self) -> Path:
        return Path(super().user_log_dir)

    @mark_appdir_path
    def user_cache_dir(self) -> Path:
        return Path(super().user_cache_dir)

    @mark_appdir_path
    def user_config_dir(self) -> Path:
        return Path(super().user_config_dir)

    @mark_appdir_path
    def user_state_dir(self) -> Path:
        return Path(super().user_state_dir)

    @mark_appdir_path
    def site_data_dir(self) -> Path:
        return Path(super().site_data_dir)

    @mark_appdir_path
    def site_config_dir(self) -> Path:
        return Path(super().site_config_dir)

    def as_path_dict(self) -> dict[NamedMetaPath, Optional[Path]]:
        path_dict = {named_path_item: None for named_path_item in NamedMetaPath.__members__.values()}
        for meth_name, meth_object in inspect.getmembers(self, inspect.ismethod):
            if hasattr(meth_object, '_appdir_path_type'):
                path_dict[meth_object._appdir_path_type] = meth_object()
        return path_dict


# region[Main_Exec]
if __name__ == '__main__':
    a = PathLibAppDirs(appauthor='giddi', appname='check_appdir')
    print(a.as_path_dict())
# endregion[Main_Exec]
