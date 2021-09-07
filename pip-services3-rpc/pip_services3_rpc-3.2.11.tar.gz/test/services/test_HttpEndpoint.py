# -*- coding: utf-8 -*-
"""
    test_DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import requests
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor

from pip_services3_rpc.services import HttpEndpoint
from ..Dummy import Dummy
from ..DummyController import DummyController
from ..services.DummyRestService import DummyRestService

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3004
)


class TestHttpEndpointService():
    service = None
    endpoint = None

    @classmethod
    def setup_class(cls):
        controller = DummyController()
        cls.service = DummyRestService()
        cls.service.configure(ConfigParams.from_tuples(
            'base_route', '/api/v1'
        ))

        cls.endpoint = HttpEndpoint()
        cls.endpoint.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), controller,
            Descriptor('pip-services-dummies', 'service', 'rest', 'default', '1.0'), cls.service,
            Descriptor('pip-services', 'endpoint', 'http', 'default', '1.0'), cls.endpoint
        )

        cls.service.set_references(references)
        cls.endpoint.open(None)
        cls.service.open(None)

    def teardown_method(self):
        self.service.close(None)
        self.endpoint.close(None)

    def test_crud_operations(self):
        response = self.invoke("/api/v1/dummies", {'body': DUMMY1.to_json()})

        dummy1 = Dummy(**response)

        assert dummy1 is not None
        assert DUMMY1.key == dummy1.key
        assert DUMMY1.content == dummy1.content

    def invoke(self, route, entity):

        route = "http://localhost:3004" + route

        # Call the service
        data = json.dumps(entity)
        response = requests.request('POST', route, json=data, timeout=5)
        return response.json()

