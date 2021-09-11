# pcrunner/__init__.py
# vim: ai et ts=4 sw=4 sts=4 ft=python fileencoding=utf-8

"""
pcrunner
--------

Main package for Passive Check Runner
"""

__version__ = "unknown"

try:
    from importlib.metadata import PackageNotFoundError, version

except ImportError:
    from pkg_resources import DistributionNotFound, get_distribution

    try:
        __version__ = get_distribution("pcrunner").version
    except DistributionNotFound:
        pass
else:
    try:
        __version__ = version("pcrunner")
    except PackageNotFoundError:
        pass
