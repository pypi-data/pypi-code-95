# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.clients.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Clients module implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['DummyClientFixture', 'DummyCommandableHttpClient', 'DummyDirectClient', 'DummyRestClient',
'IDummyClient', 'TestDummyCommandableHttpClient', 'TestDummyDirectClient', 'TestDummyRestClient']

from .DummyClientFixture import DummyClientFixture
from .DummyCommandableHttpClient import DummyCommandableHttpClient
from .DummyDirectClient import DummyDirectClient
from .DummyRestClient import DummyRestClient
from .IDummyClient import IDummyClient
from .test_DummyCommandableHttpClient import TestDummyCommandableHttpClient
from .test_DummyDirectClient import TestDummyDirectClient
from .test_DummyRestClient import TestDummyRestClient