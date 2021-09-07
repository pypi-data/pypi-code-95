"""moose tools"""
import pkg_resources


__app__: str = pkg_resources.safe_name(__name__)

__version__ = pkg_resources.get_distribution(__app__).version


