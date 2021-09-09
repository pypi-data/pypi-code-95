"""Flywheel Core HTTP API Client."""
import importlib.metadata

from fw_http_client import ConnectionError  # pylint: disable=redefined-builtin
from fw_http_client import ClientError, ServerError, errors

from .client import CoreClient
from .config import CoreConfig

__version__ = importlib.metadata.version(__name__)
__all__ = [
    "CoreClient",
    "CoreConfig",
    "errors",
    "ConnectionError",
    "ClientError",
    "ServerError",
]
