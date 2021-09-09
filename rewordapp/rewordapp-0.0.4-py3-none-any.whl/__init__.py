"""Top-level module for rewordapp.

- allow end-user to transform data.
"""

from rewordapp.config import version
from rewordapp.config import edition

__version__ = version
__edition__ = edition

__all__ = [
    'version',
    'edition',
]
