from json import loads
from requests import get

__title__ = 'AminoLab'
__author__ = 'LilZevi'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-2022 LilZevi'
__version__ = '1.6'

from .aminolab import *
from .utils import *


__newest__ = loads(get("https://pypi.python.org/pypi/AminoLab/json").text)["info"]["version"]

if __version__ != __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
else:
    print(f"version : {__version__}")
