import pkg_resources

__version__ = pkg_resources.get_distribution('emutils').version

from ._train import *