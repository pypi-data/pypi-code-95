import pkg_resources

__version__ = pkg_resources.get_distribution('emutils').version

from .correlated import *