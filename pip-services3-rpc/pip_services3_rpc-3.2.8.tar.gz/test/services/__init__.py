# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.clients.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Clients module implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['DummyCommandableHttpService', 'DummyRestService']

from .DummyCommandableHttpService import DummyCommandableHttpService
from .DummyRestService import DummyRestService
from .DummyRestOperations import DummyRestOperations