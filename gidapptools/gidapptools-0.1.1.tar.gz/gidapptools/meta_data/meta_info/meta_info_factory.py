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

from gidapptools.meta_data.meta_info.meta_info_holder import MetaInfo
from gidapptools.utility import general_path_type, meta_data_from_path

from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaFactory
from gidapptools.meta_data.config_kwargs import ConfigKwargs
# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MetaInfoFactory(AbstractMetaFactory):
    product_class = MetaInfo
    product_name = 'meta_info'
    prefix_arg_getters = '_arg_get_'

    def __init__(self, config_kwargs: ConfigKwargs) -> None:
        super().__init__(config_kwargs=config_kwargs)

        self.init_path = Path(config_kwargs.get('init_path'))
        self.package_metadata = meta_data_from_path(self.init_path)
        self.arg_getters_map: dict[str, Callable] = None
        self.needed_arg_names: list[str] = None

    def setup(self) -> None:
        self.arg_getters_map = self._collect_arg_getters_map()
        self.needed_arg_names = self._retrieve_needed_arg_names()
        self.is_setup = True

    def _collect_arg_getters_map(self) -> dict[str, Callable]:
        arg_getters_map = {}
        for meth_name, meth_obj in inspect.getmembers(self, inspect.ismethod):
            if meth_name.startswith(self.prefix_arg_getters):
                arg_name = meth_name.removeprefix(self.prefix_arg_getters)
                arg_getters_map[arg_name] = meth_obj
        return arg_getters_map

    def _retrieve_needed_arg_names(self) -> list[str]:
        parameters = inspect.signature(self.product_class).parameters
        return list(parameters)

    def _build_meta_info_args(self) -> dict[str, Any]:
        meta_info_kwargs = {arg_name: self.config_kwargs.get(arg_name, None) for arg_name in self._retrieve_needed_arg_names()}
        for arg_name, arg_value in meta_info_kwargs.items():

            if arg_value is not None:
                continue

            arg_value_getter = self.arg_getters_map.get(arg_name, partial(self._default_arg_getter, arg_name))

            meta_info_kwargs[arg_name] = arg_value_getter()
        return {k: v for k, v in meta_info_kwargs.items() if v is not None}

    def _default_arg_getter(self, arg_name: str) -> Any:
        return self.package_metadata.get(arg_name.casefold())

    def _arg_get_url(self):
        url_text = self.package_metadata.get('project-url')
        parts = map(lambda x: x.strip(), url_text.split(','))
        for part in parts:
            if part.startswith('http'):
                return part

    def _build(self) -> MetaInfo:
        if self.is_setup is False:
            # TODO: maybe raise error instead
            self.setup()
        meta_info_kwargs = self._build_meta_info_args()
        instance = self.product_class(**meta_info_kwargs)
        return instance


# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
