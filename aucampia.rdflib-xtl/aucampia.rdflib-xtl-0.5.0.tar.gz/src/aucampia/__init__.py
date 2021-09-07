#!/usr/bin/env python3
# vim: set filetype=python tw=100 cc=+1:
# https://setuptools.readthedocs.io/en/latest/pkg_resources.html#id5
# https://www.python.org/dev/peps/pep-0420/#namespace-packages-today
"""
This is a namespace package in line with PEP-0420.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore
