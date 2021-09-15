"""Common code"""
from .check_update import check_update
from .database import build_database_url
from .discord_common import make_embed
from .discord_common import error_embed
from .make_logger import make_logger

__version__ = "0.0.3"

__all__ = [
    "__version__",
    "make_logger",
    "make_embed",
    "error_embed",
    "build_database_url",
    "check_update",
]
