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


class GidAppToolsBaseError(Exception):
    """
    Base Exception For GidAppTools.
    """


class BaseMetaDataError(GidAppToolsBaseError):
    """
    Base Error for Meta Data Errors.
    """


class NotSetupError(BaseMetaDataError):
    def __init__(self, app_meta_data) -> None:
        self.app_meta_data = app_meta_data
        self.message = f'{self.app_meta_data.__class__.__name__!r} has to set up from the base_init_file first!'
        super().__init__(self.message)


class NotBaseInitFileError(BaseMetaDataError):
    """
    Raised if the calling file is not the base __init__.py file of the App.
    """

    def __init__(self, calling_file: Path) -> None:
        self.calling_file = calling_file
        self.calling_folder = calling_file.parent
        self.message = f"This function has to be called from the '__init__.py' file in the base directory of the App, actual calling file: {self.calling_file.as_posix()!r}"
        super().__init__(self.message)


class BaseMetaPathsError(GidAppToolsBaseError):
    """
    Base error for meta_paths.
    """


class AppNameMissingError(BaseMetaPathsError):

    def __init__(self) -> None:
        self.message = "The name of the App was not found in the 'kwargs_holder' or in the env ('APP_NAME')."
        super().__init__(self.message)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
