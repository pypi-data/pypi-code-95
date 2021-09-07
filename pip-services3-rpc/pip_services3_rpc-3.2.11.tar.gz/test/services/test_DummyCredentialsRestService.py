# -*- coding: utf-8 -*-
"""
    test_DummyCredentialsRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import os

import requests
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor

from ..Dummy import Dummy
from ..DummyController import DummyController
from ..services.DummyRestService import DummyRestService


def get_fullpath(filepath):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), filepath))


port = 3007

rest_config = ConfigParams.from_tuples(
    'connection.protocol',
    'https',
    'connection.host',
    'localhost',
    'connection.port',
    port,
    'credential.ssl_key_file', get_fullpath('../credentials/ssl_key_file'),
    'credential.ssl_crt_file', get_fullpath('../credentials/ssl_crt_file')
)

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')


class TestDummyCredentialsRestService:
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
        response = self.invoke("/dummies", {"body": DUMMY1.to_json()})

        dummy1 = Dummy(**response)
        assert dummy1 is not None
        assert DUMMY1.key == dummy1.key
        assert DUMMY1.content == dummy1.content

        # Create another dummy
        response = self.invoke("/dummies", {"body": DUMMY2.to_json()})

        dummy2 = Dummy(**response)

        assert dummy2 is not None
        assert DUMMY2.key == dummy2.key
        assert DUMMY2.content == dummy2.content

        # dummy_del = self.invoke('/dummies/<id>')

        assert 2 == self.service.get_number_of_calls()

    def invoke(self, route, entity):
        params = {}
        route = f"https://localhost:{port}{route}"
        response = None
        timeout = 5
        try:
            # Call the service
            data = json.dumps(entity)
            response = requests.request('POST', route, params=params, json=data, timeout=timeout, verify=False)
            return response.json()
        except Exception as ex:
            raise ex
