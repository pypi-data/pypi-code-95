# -*- coding: utf-8 -*-
"""
    test_DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime
import json
import time

import pytz
import requests
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor

from ..Dummy import Dummy
from ..DummyController import DummyController
from ..services.DummyRestService import DummyRestService

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3006
)

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')


class TestDummyOperations:
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
        cls.service.open(None)

    def teardown_class(self, method=None):
        self.service.close(None)

    def test_about_operations(self):
        headers = {
            'x-forwarded-for': 'client_ip, proxy1, proxy2',
            'socket': 'remoteAddress',
            'remoteAddress': 'remote_addr_value:3000',
            'user': 'User_Test1',
        }

        about = self.invoke('/about', headers=headers)
        assert about['server']['name'] == 'unknown'
        assert about['server']['protocol'] == 'POST'
        assert about['server']['host'] == 'localhost'
        assert about['server']['port'] == '3006'
        assert about['server']['addresses'] is not None
        assert about['server']['url'] == 'http://localhost:3006/about'
        assert about['client']['address'] == 'client_ip'
        assert about['client']['platform'] == 'unknown'
        assert about['client']['user'] == 'User_Test1'

        # Test detect other params
        headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3_1 like Mac OS X) '
                                 'AppleWebKit/603.1.30 (KHTML, like Gecko) '
                                 'Version/10.0 Mobile/14E304 Safari/602.1 '}
        req_body = {
            'connection': {
                'socket': {'remoteAddress': '8.8.0.0'},
            },
        }

        about = self.invoke('/about', headers=headers, entity=req_body)
        assert about['client']['address'] == '8.8.0.0'
        assert about['client']['client'] == 'safari'
        assert about['client']['platform'] == 'mobile'

        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        req_body = {
            'connection': {'remoteAddress': '4.4.0.0'},
        }

        about = self.invoke('/about', headers=headers, entity=req_body)
        assert about['client']['address'] == '4.4.0.0'
        assert about['client']['client'] == 'firefox'
        assert about['client']['platform'] == 'windows 6.1'

        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.5; rv:42.0) Gecko/20100101 Chrome/42.0'}
        req_body = {'socket': {'remoteAddress': '0.0.0.0'}, }

        about = self.invoke('/about', headers=headers, entity=req_body)
        assert about['client']['address'] == '0.0.0.0'
        assert about['client']['client'] == 'chrome'
        assert about['client']['platform'] == 'mac 10.5'

    def invoke(self, route, method='POST', entity=None, headers=None):
        route = "http://localhost:3006" + route

        # Call the service
        if entity:
            entity = json.dumps(entity)
        response = requests.request(method, route, headers=headers, json=entity, timeout=5)
        return response.json()
