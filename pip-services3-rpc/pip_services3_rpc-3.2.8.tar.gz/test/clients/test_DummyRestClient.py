# -*- coding: utf-8 -*-
"""
    tests.rest.test_DummyRestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import Descriptor, References

from .DummyClientFixture import DummyClientFixture
from .DummyRestClient import DummyRestClient
from ..DummyController import DummyController
from ..services.DummyRestService import DummyRestService

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3000,
    "options.correlation_id_place", "headers",
)


class TestDummyRestClient:
    fixture = None
    service = None
    client = None

    @classmethod
    def setup_class(cls):
        controller = DummyController()

        cls.service = DummyRestService()
        cls.service.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), controller,
            Descriptor("pip-services-dummies", "service", "rest", "default", "1.0"), cls.service,
        )

        cls.service.set_references(references)

        cls.service.open(None)

    def teardown_class(self):
        self.service.close(None)

    def setup_method(self):
        self.client = DummyRestClient()
        self.fixture = DummyClientFixture(self.client)

        self.client.configure(rest_config)
        self.client.set_references(References())

        self.client.open(None)

    def teardown_method(self, method):
        self.client.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
