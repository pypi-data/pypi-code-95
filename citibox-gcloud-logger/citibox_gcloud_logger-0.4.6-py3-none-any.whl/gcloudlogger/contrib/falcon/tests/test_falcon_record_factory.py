import unittest
import json

from unittest import mock

from citibox.gcloudlogger.src.base_record import BaseRecord
from citibox.gcloudlogger.contrib.falcon.falcon_record_factory import FalconRecordFactory


@mock.patch('citibox.gcloudlogger.contrib.falcon.falcon_record_factory.falcon.Response')
@mock.patch('citibox.gcloudlogger.contrib.falcon.falcon_record_factory.falcon.Request')
class TestFalconRecordFactory(unittest.TestCase):

    def test_process_request_get_http(self, request_mock, response_mock):
        request_mock.method = "GET"
        request_mock.host = "PYTEST"
        request_mock.path = "/test_path"
        request_mock.headers = {
            "header-a": "A",
            "USER_INFO": "LockerApp/1.8.4 Android/10"
        }
        request_mock.params = {"parameter_1": "1"}

        response_mock.body = '{"status": "ok"}'
        response_mock.status = "200 Ok"

        base_record = FalconRecordFactory(request=request_mock, response=response_mock, params={}).build()
        base_record_dict = base_record.to_dict()

        self.assertEquals(f'{request_mock.method} 200 {request_mock.path}', base_record.message)
        self.assertIn("headers", base_record_dict.get('request'))
        self.assertIn("host", base_record_dict)
        self.assertIn("path", base_record_dict)
        self.assertEquals("1", base_record_dict.get('request').get("params").get("parameter_1"))
        self.assertEquals("A", base_record_dict.get('request').get("headers").get("header-a"))
        self.assertEquals(json.loads(response_mock.body), base_record_dict.get("response").get("body"))

    def test_process_request_post_http(self, request_mock, response_mock):
        request_mock.method = "POST"
        request_mock.host = "PYTEST_POST"
        request_mock.path = "/test_path"
        request_mock.headers = {"header-a": "A"}
        request_mock.media = {"parameter_1": "1"}

        response_mock.body = '{"status": "ok"}'
        response_mock.status = "200 Ok"

        base_record = FalconRecordFactory(request=request_mock, response=response_mock, params={}).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record, BaseRecord)
        self.assertEquals(f'{request_mock.method} 200 {request_mock.path}', base_record.message)
        self.assertIn("body", base_record_dict.get('request'))
        self.assertIn("headers", base_record_dict.get('request'))
        self.assertIn("host", base_record_dict)
        self.assertIn("path", base_record_dict)
        self.assertEquals("1", base_record_dict.get('request').get("body").get("parameter_1"))
        self.assertEquals("A", base_record_dict.get('request').get("headers").get("header-a"))
        self.assertEquals(json.loads(response_mock.body), base_record_dict.get("response").get('body'))

    def test_process_request_post_pubsub(self, request_mock, response_mock):
        request_mock.method = "POST"
        request_mock.host = "PYTEST"
        request_mock.path = "/test_path"
        request_mock.headers = {"header-a": "A"}
        request_mock.user_agent = FalconRecordFactory.PUBSUB_USER_AGENT
        request_mock.media = {"message": {"attributes": {"attr_1": "AA"}}}

        response_mock.body = '{"status": "ok"}'
        response_mock.status = "200 Ok"

        base_record = FalconRecordFactory(request=request_mock, response=response_mock, params={}).build()
        base_record_dict = base_record.to_dict()

        self.assertEquals(f'{request_mock.method} 200 {request_mock.path}', base_record.message)
        self.assertIn("headers", base_record_dict.get('request'))
        self.assertIn("host", base_record_dict)
        self.assertIn("path", base_record_dict)
        self.assertEquals("A", base_record_dict.get('request').get("headers").get("header-a"))
        self.assertEquals("AA", base_record_dict.get('attr_1'))

    def test_status_code_must_be_integer(self, request_mock, response_mock):
        request_mock.method = "POST"
        request_mock.host = "PYTEST_POST"
        request_mock.path = "/test_path"
        request_mock.headers = {"header-a": "A"}
        request_mock.media = {"parameter_1": "1"}

        response_mock.body = '{"status": "ok"}'
        response_mock.status = "200 Ok"

        base_record = FalconRecordFactory(request=request_mock, response=response_mock, params={}).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record_dict.get('response').get('status_code'), int)

    def test_status_code_with_null_value(self, request_mock, response_mock):
        request_mock.method = "POST"
        request_mock.host = "PYTEST_POST"
        request_mock.path = "/test_path"
        request_mock.headers = {"header-a": "A"}
        request_mock.media = {"parameter_1": "1"}

        response_mock.body = '{"status": "ok"}'
        response_mock.status = None

        base_record = FalconRecordFactory(request=request_mock, response=response_mock, params={}).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record_dict.get('response').get('status_code'), int)


    def test_status_code_wrong_format(self, request_mock, response_mock):
        request_mock.method = "POST"
        request_mock.host = "PYTEST_POST"
        request_mock.path = "/test_path"
        request_mock.headers = {"header-a": "A"}
        request_mock.media = {"parameter_1": "1"}

        response_mock.body = '{"status": "ok"}'
        response_mock.status = 'ok 200'

        base_record = FalconRecordFactory(request=request_mock, response=response_mock, params={}).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record_dict.get('response').get('status_code'), int)
