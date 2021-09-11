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

from gidapptools.utility import PathLibAppDirs, NamedMetaPath
from tempfile import gettempdir
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidAppDirs(PathLibAppDirs):

    @PathLibAppDirs.mark_path
    def user_config_dir(self) -> Path:
        config_dir = super().user_config_dir().joinpath('config')
        return config_dir

    @PathLibAppDirs.mark_path
    def user_cache_dir(self) -> Path:
        cache_dir = super().user_cache_dir()
        return cache_dir.with_name(cache_dir.name.lower())

    @PathLibAppDirs.mark_path
    def user_log_dir(self) -> Path:
        log_dir = super().user_log_dir()
        return log_dir.with_name(log_dir.name.lower())

    @PathLibAppDirs.mark_path
    def user_temp_dir(self) -> Path:
        default_temp_dir = Path(gettempdir())
        app_temp_dir = default_temp_dir.joinpath(self.appname)
        return Path(str(app_temp_dir))

    @classmethod
    def get_path_dict_direct(cls,
                             name: str,
                             author: str = None,
                             roaming: bool = True,
                             **kwargs) -> dict[NamedMetaPath, Optional[Path]]:
        inst = cls(appname=name, appauthor=author, roaming=roaming, **kwargs)
        return inst.as_path_dict()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
