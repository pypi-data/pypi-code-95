# -*- coding: utf-8 -*-
"""
    test_DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import os

import requests
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.data import IdGenerator
from pip_services3_commons.refer import References, Descriptor

from ..Dummy import Dummy
from ..DummyController import DummyController
from ..services.DummyRestService import DummyRestService

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    "connection.host", "localhost",
    "connection.port", 3001,
    "swagger.content", "swagger yaml or json content",  # for test only
    "swagger.enable", "true"
)

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')


class TestDummyRestService:
    controller = None
    service = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()

        cls.service = DummyRestService()
        cls.service.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller,
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service
        )

        cls.service.set_references(references)

    def setup_method(self, method):
        self.service.open(None)

    def teardown_method(self, method):
        self.service.close(None)

    def test_crud_operations(self):
        # Create one dummy
        response = self.invoke('POST', "/dummies", {"body": DUMMY1.to_json()})

        dummy1 = Dummy(**response)
        assert dummy1 is not None
        assert DUMMY1.key == dummy1.key
        assert DUMMY1.content == dummy1.content

        # Create another dummy
        response = self.invoke('POST', "/dummies", {"body": DUMMY2.to_json()})

        dummy2 = Dummy(**response)

        assert dummy2 is not None
        assert DUMMY2.key == dummy2.key
        assert DUMMY2.content == dummy2.content

        # Get all dummies
        response = self.invoke('GET', '/dummies', None)

        assert response is not None
        assert len(response['data']) == 2

        # Update the dummy
        dummy1.content = 'Updated Content 1'
        response = self.invoke('PUT', '/dummies', {'body': dummy1.to_json()})

        dummy = Dummy(**response)

        assert dummy.content == 'Updated Content 1'
        assert dummy.key == dummy1.key

        dummy1 = dummy

        # Delete dummy
        self.invoke('DELETE', f'/dummies/{dummy1.id}')

        # Try to get delete dummy
        response = self.invoke('GET', f'/dummies/{dummy1.id}')

        assert response is None

        assert 6 == self.service.get_number_of_calls()

    def invoke(self, method, route, entity=None):
        route = "http://localhost:3001" + route

        # Call the service
        if entity:
            entity = json.dumps(entity)
        response = requests.request(method, route, json=entity, timeout=5)
        if response.status_code != 204:
            return response.json()

    def test_get_open_api_spec_from_string(self):
        response = requests.request('GET', 'http://localhost:3001/swagger')

        open_api_content = rest_config.get_as_string('swagger.content')
        assert open_api_content == response.text

    def test_get_open_api_spec_from_file(self):
        self.service.close(None)

        open_api_content = 'swagger yaml content from file'
        filename = 'dummy_' + IdGenerator.next_long() + '.tmp'

        # create temp file
        with open(filename, 'w') as f:
            f.write(open_api_content)

        # recreate service with new configuration
        service_config = ConfigParams.from_tuples(
            "connection.protocol", "http",
            "connection.host", "localhost",
            "connection.port", 3001,
            "swagger.path", filename,  # for test only
            "swagger.enable", "true"
        )
        ctrl = DummyController()

        self.service = DummyRestService()
        self.service.configure(service_config)

        references = References.from_tuples(
            Descriptor('pip-services-dummies', 'controller', 'default', 'default', '1.0'), ctrl,
            Descriptor('pip-services-dummies', 'service', 'rest', 'default', '1.0'), self.service
        )
        self.service.set_references(references)

        self.service.open(None)

        response = requests.request('GET', 'http://localhost:3001/swagger')
        assert response.text == open_api_content

        # delete temp file
        os.remove(filename)
