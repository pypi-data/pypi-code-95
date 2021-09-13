"""Top-level package for openflowthrough."""

from pkg_resources import get_distribution

from .main import OpenFlowThrough

__all__ = ["OpenFlowThrough"]
__author__ = """Drew Meyers"""
__email__ = "drewm@mit.edu"
__version__ = get_distribution("openflowthrough").version
