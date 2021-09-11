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
from collections.abc import MutableMapping, Mapping

from gidapptools.utility import NamedMetaPath, MiscEnum, KwargDict

if TYPE_CHECKING:
    from gidapptools.meta_data.meta_info.meta_info_holder import MetaInfo
    from gidapptools.meta_data.meta_paths.meta_paths_holder import MetaPaths

    meta_items_type = Union[MetaInfo, MetaPaths, object]
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ConfigKwargs(KwargDict):

    def __init__(self, base_configuration: dict = None, **kwargs) -> None:
        super().__init__(base_defaults=base_configuration, **kwargs)
        self._path_overwrites: dict[NamedMetaPath, Path] = {}
        self.created_meta_items: dict[str, "meta_items_type"] = {}

    def _post_init(self):
        for key, value in self.data.items():
            if NamedMetaPath.is_in_value(key) is True:
                self._path_overwrites[NamedMetaPath(key)] = self.data.pop(key)

    def add_path_overwrite(self, name: Union[NamedMetaPath, str], path: Path) -> None:
        name = name if isinstance(name, NamedMetaPath) else NamedMetaPath(str(name))
        self._path_overwrites[name] = path

    def __setitem__(self, key, item) -> None:
        if key == 'path_overwrites':
            raise KeyError('Not allowed to set path_overwrites this way, use "add_path_overwrite".')
        return super().__setitem__(key, item)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            for meta_item in self.created_meta_items.values():
                if hasattr(meta_item, key):
                    return getattr(meta_item, key)
            if key == 'path_overwrites':
                return self._path_overwrites
            raise


# region[Main_Exec]

if __name__ == '__main__':
    x = ConfigKwargs()
# endregion[Main_Exec]
