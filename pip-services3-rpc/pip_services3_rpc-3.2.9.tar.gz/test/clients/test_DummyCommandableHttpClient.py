# -*- coding: utf-8 -*-
"""
    tests.rest.test_DummyCommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import Descriptor, References

from .DummyClientFixture import DummyClientFixture
from .DummyCommandableHttpClient import DummyCommandableHttpClient
from ..DummyController import DummyController
from ..services.DummyCommandableHttpService import DummyCommandableHttpService

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3001
)


class TestDummyCommandableHttpClient:
    fixture: DummyClientFixture
    service: DummyCommandableHttpService
    client: DummyCommandableHttpClient

    @classmethod
    def setup_class(cls):
        controller = DummyController()

        cls.service = DummyCommandableHttpService()
        cls.service.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), controller,
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service
        )

        cls.service.set_references(references)

        cls.service.open(None)

        time.sleep(0.5)

    @classmethod
    def teardown_class(cls):
        cls.service.close(None)

    def setup_method(self):
        self.client = DummyCommandableHttpClient()
        self.fixture = DummyClientFixture(self.client)

        self.client.configure(rest_config)
        self.client.set_references(References())

        self.client.open(None)

    def teardown_method(self):
        self.client.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
