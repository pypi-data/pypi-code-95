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

from gidapptools.utility import NamedMetaPath
from gidapptools.errors import NotSetupError
from gidapptools.meta_data.config_kwargs import ConfigKwargs
from gidapptools.types import general_path_type

from gidapptools.meta_data.meta_info import MetaInfoFactory, MetaInfo
from gidapptools.meta_data.meta_paths import MetaPathsFactory, MetaPaths
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaFactory

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

meta_factory_type = Union[MetaInfoFactory, MetaPathsFactory]


class AppMetaData:
    factories: dict[str, meta_factory_type] = {'meta_info': MetaInfoFactory,
                                               'meta_paths': MetaPathsFactory}

    def __init__(self) -> None:
        self.meta_info: MetaInfo = None
        self.meta_paths: MetaPaths = None
        self.is_setup = False

    def check_is_setup(self):
        if self.is_setup is False:
            raise NotSetupError(f'{app_meta_data.__class__.__name__!r} has to set up from the base_init_file first!')

    @classmethod
    def set_meta_info_factory(cls, factory) -> None:
        if not isinstance(factory, AbstractMetaFactory):
            raise TypeError(f"'factory' needs to be a subclass of {AbstractMetaFactory.__name__!r}")
        cls.factories['meta_info'] = factory

    @classmethod
    def set_meta_paths_factory(cls, factory) -> None:
        if not isinstance(factory, AbstractMetaFactory):
            raise TypeError(f"'factory' needs to be a subclass of {AbstractMetaFactory.__name__!r}")
        cls.factories['meta_paths'] = factory

    def _initialize_other(self) -> None:
        pass

    def _initialize_data(self, config_kwargs: ConfigKwargs) -> None:
        self.meta_info = self.factories['meta_info'].build(config_kwargs=config_kwargs)
        self.meta_paths = self.factories['meta_paths'].build(config_kwargs=config_kwargs)

    def setup(self, init_path: general_path_type, **kwargs) -> None:
        config_kwargs = ConfigKwargs(base_configuration=kwargs)
        config_kwargs['init_path'] = init_path
        self._initialize_data(config_kwargs=config_kwargs)
        self._initialize_other()
        self.is_setup = True


app_meta_data = AppMetaData()


def setup_meta_data(init_path: general_path_type, **kwargs) -> None:
    app_meta_data.setup(init_path=init_path, **kwargs)


def get_meta_info() -> MetaInfo:
    app_meta_data.check_is_setup()
    return app_meta_data.meta_info


def get_meta_paths() -> MetaPaths:
    app_meta_data.check_is_setup()
    return app_meta_data.meta_paths


    # region[Main_Exec]
if __name__ == '__main__':
    from faked_pack_src import call_and_return
    call_and_return(setup_meta_data, folder_to_create=[Path(r"C:\Users\Giddi\Downloads\server_logs\this"), (NamedMetaPath.DATA, 'that'), ('user_log_dir', 'something')])
    info = get_meta_info()
    print(info.as_dict())

# endregion[Main_Exec]
