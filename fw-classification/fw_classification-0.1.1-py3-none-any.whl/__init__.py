"""fw_classification module.

isort:skip_file
"""
import importlib.metadata

__version__ = importlib.metadata.version(__name__)

from .classify import Profile, run_classification
from .adapters import available_adapters
