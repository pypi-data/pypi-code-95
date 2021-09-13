""" This is a simple Python library for interacting with the REST interface of an instance of Cordra.
"""

from .cordraMethods import (
    create_object, 
    read_object, 
    read_payload_info, 
    read_payload, 
    update_object, 
    delete_object, 
    find_objects, 
    create_token, 
    read_token, 
    delete_token
)
from .cordraObject import CordraObject
from .cordraClient import CordraClient
from .dataset import Dataset

def get_version():
    """Get the version of the code from egg_info.
    Returns:
      the package version number
    """
    from pkg_resources import get_distribution, DistributionNotFound

    try:
        version = get_distribution(__name__.split('.')[0]).version # pylint: disable=no-member
    except DistributionNotFound: # pragma: no cover
        version = "unknown, try running `python setup.py egg_info`"

    return version


__version__ = get_version()

__all__ = [
    "__version__",
    "create_object", 
    "read_object", 
    "read_payload_info", 
    "read_payload", 
    "update_object", 
    "delete_object", 
    "find_objects", 
    "create_token", 
    "read_token", 
    "delete_token",
    "CordraObject",
    "CordraClient",
    "Dataset"
]