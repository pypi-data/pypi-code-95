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

from rich.console import Console as RichConsole

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def make_dprint(**console_kwargs) -> Callable:
    use_seperator: bool = console_kwargs.pop('use_seperator', True)
    seperator_char: str = console_kwargs.pop('seperator_char', '-')
    use_print_count: bool = console_kwargs.pop('use_print_count', True)

    extra_newline: bool = console_kwargs.pop('extra_newline', True)

    prefix: Optional[str] = console_kwargs.pop('prefix', None)

    console_kwargs = {'soft_wrap': True} | console_kwargs
    console = RichConsole(**console_kwargs)
    print_count = 0

    convert_table = {'odict_keys': list, }

    def _convert_stupid_fake_iterables(in_object: Any):
        try:
            if in_object.__class__.__name__ in convert_table:
                return convert_table.get(in_object.__class__.__name__)(in_object)
        except Exception:
            return in_object
        return in_object

    def _dprint(*args, **kwargs) -> None:
        nonlocal print_count
        print_count += 1
        if use_seperator is True:
            title = "" if use_print_count is False else f"Output No.{print_count}"
            console.rule(title=title, characters=seperator_char)
        if extra_newline is True:
            kwargs['end'] = '\n\n'
        if prefix:
            console.print(prefix, end='')
        args = list(map(_convert_stupid_fake_iterables, args))
        console.print(*args, **kwargs)

    return _dprint


dprint = make_dprint()

# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
