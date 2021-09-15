from __future__ import absolute_import

import atexit
from pkg_resources import get_distribution, DistributionNotFound

import importlib_resources

try:
    from importlib_resources import as_file
except ImportError:
    from importlib_resources.trees import as_file

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

try:
    version = get_distribution(__name__).version
except DistributionNotFound:
    version = "unknown version"
__version__ = version

LATEST_VERSIONS = {
    "detx": "detx/detx_v3.detx",
}


def data_path(filename, raise_missing=True):
    """Return the absolute filepath for a given filename in test data"""
    ref = importlib_resources.files("km3net_testdata.data") / filename
    file_manager = ExitStack()
    atexit.register(file_manager.close)
    file_path = file_manager.enter_context(as_file(ref))
    if raise_missing and not file_path.exists():
        raise RuntimeError("Unknown or missing file: {0}".format(filename))
    return str(file_path)


def latest(dataformat, raise_missing=True):
    """Return the path to the latest version of the given dataformat"""
    filename = LATEST_VERSIONS.get(dataformat, "latest." + dataformat)
    return data_path(filename, raise_missing=raise_missing)


__all__ = ["data_path"]
