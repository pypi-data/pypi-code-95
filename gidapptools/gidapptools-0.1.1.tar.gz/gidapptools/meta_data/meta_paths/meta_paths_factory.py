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

from gidapptools.utility import NamedMetaPath, EnvName
from gidapptools.errors import AppNameMissingError
from gidapptools.meta_data.meta_paths.meta_paths_holder import MetaPaths
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaFactory
from gidapptools.meta_data.meta_paths.appdirs_implementations import GidAppDirs
from gidapptools.meta_data.config_kwargs import ConfigKwargs
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MetaPathsFactory(AbstractMetaFactory):
    appdirs_class = GidAppDirs
    product_class = MetaPaths
    product_name = 'meta_paths'

    def __init__(self, config_kwargs: ConfigKwargs) -> None:
        super().__init__(config_kwargs=config_kwargs)
        self.code_base_dir = Path(self.config_kwargs.get('init_path')).parent

    def get_path_dict(self) -> dict[NamedMetaPath, Optional[Path]]:
        defaults = {'name': os.getenv(EnvName.APP_NAME),
                    'author': os.getenv(EnvName.APP_AUTHOR)}
        _kwargs = self.config_kwargs.get_kwargs_for(self.appdirs_class.get_path_dict_direct, defaults)
        if _kwargs.get('name') is None:
            raise AppNameMissingError()

        path_overwrites = self.config_kwargs.get('path_overwrites', {})
        path_dict = self.appdirs_class.get_path_dict_direct(**_kwargs)
        return path_dict | path_overwrites

    def setup(self) -> None:
        self.path_dict = self.get_path_dict()
        self.is_setup = True

    def _build(self) -> None:
        if self.is_setup is False:
            self.setup()
        _kwargs = self.config_kwargs.get_kwargs_for(self.product_class, defaults={'code_base_dir': self.code_base_dir, 'paths': self.path_dict})
        instance = self.product_class(**_kwargs)

        return instance


# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
