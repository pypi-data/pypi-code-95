# -*- coding: utf-8 -*-
"""
    test_DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import requests
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor
from pip_services3_components.info import ContextInfo

from pip_services3_rpc.services import StatusRestService

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3002
)


class TestStatusRestService():
    service = None

    @classmethod
    def setup_class(cls):
        cls.service = StatusRestService()
        cls.service.configure(rest_config)

        contextInfo = ContextInfo()
        contextInfo.name = "Test"
        contextInfo.description = "This is a test container"

        references = References.from_tuples(
            Descriptor("pip-services", "context-info", "default", "default", "1.0"), contextInfo,
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service
        )

        cls.service.set_references(references)

    def setup_method(self, method):
        self.service.open(None)

    def teardown_method(self, method):
        self.service.close(None)

    def test_status(self):
        result = self.invoke("/status")

        assert result.text is not None

    def invoke(self, route):
        params = {}
        route = "http://localhost:3002" + route
        response = None
        timeout = 5

        # Call the service
        response = requests.request('GET', route, params=params, timeout=timeout)
        return response
