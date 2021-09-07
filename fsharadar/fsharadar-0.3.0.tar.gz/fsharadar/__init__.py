
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .pipe_loader import get_pipeline_loader

__all__ = [
    'get_pipeline_loader',
]

