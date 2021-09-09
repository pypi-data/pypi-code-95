from .client import *
from .utils import pickle_obj
from .utils import UnicornData

__authors__ = "Tong Zhang"
__copyright__ = "(c) 2018-2021, Facility for Rare Isotope beams," \
                " Michigan State University"
__contact__ = "Tong Zhang <zhangt@frib.msu.edu>"
__version__ = "0.4.3"

__doc__ = \
"""Python client to communicate with UNICORN web service.

Manage the UNICORN service data via CLI or scripting:

Examples:
---------
>>> from unicorn import AdminClient
>>> client = AdminClient(base_url='xxx')
>>> # define f
>>> client.create(**f)
>>> client.update(**f)
>>> client.delete(**f)

And commands:

*fn-push*: Push data to UNICORN from external xlsx file
*fn-delete*: Delete data from UNICORN

Function API client could be used to get execution results from UNICORN,

Examples:
--------
>>> from unicorn import ApiClient
>>> client = ApiClient(base_url='xxx')
>>> client.get('f1',x=1)

:version: %s
:authors: %s
""" % (__version__, __authors__)
