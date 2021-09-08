import unittest
import json

from unittest import mock

from citibox.gcloudlogger.src.base_record import BaseRecord
from citibox.gcloudlogger.contrib.django.django_record_factory import DjangoRecordFactory


class FakeHttpResponse:
    content = json.dumps({"some_key": "some_value"})
    data = '{"some_key": "some_value"}'
    status_code = "200 Ok"

    def items(self):
        """
        Mocks django.http.response.HttpResponse.items method
        :return: dict
        """
        return {
            'header_1': 'h1',
            'header_2': 'h2'
        }

class FakeLogger:
    def warning(self, message: str):
        pass

@mock.patch('citibox.gcloudlogger.contrib.django.django_record_factory.HttpRequest')
class TestDjangoRecordFactory(unittest.TestCase):

    def test_process_request_get_http(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "GET"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1",
            "USER_AGENT": "cosicas_raras",
        }
        request_mock.GET.lists.return_value = [
            ("param", "value")
        ]

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record, BaseRecord)
        self.assertEquals(f'{request_mock.method} 200 Ok {request_mock.path}', base_record.message)
        self.assertIn("headers", base_record_dict.get('request'))
        self.assertIn("host", base_record_dict)
        self.assertIn("path", base_record_dict)
        self.assertEquals("value", base_record_dict.get('request').get("params").get("param"))
        self.assertEquals("header_1", base_record_dict.get('request').get("headers").get("HEADER_1"))
        self.assertEquals(json.loads(FakeHttpResponse.content), base_record_dict.get("response").get("body"))

    def test_process_request_post_http(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "POST"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1"
        }
        request_mock.POST = {
            "param": "value"
        }

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record, BaseRecord)
        self.assertEquals(f'{request_mock.method} 200 Ok {request_mock.path}', base_record.message)
        self.assertIn("headers", base_record_dict.get('request'))
        self.assertIn("host", base_record_dict)
        self.assertIn("path", base_record_dict)
        self.assertEquals("value", base_record_dict.get('request').get("body").get("param"))
        self.assertEquals("header_1", base_record_dict.get('request').get("headers").get("HEADER_1"))
        self.assertEquals(json.loads(FakeHttpResponse.content), base_record_dict.get("response").get("body"))

    def test_process_request_post_pubsub_http(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "POST"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1",
            "HTTP_USER_AGENT": DjangoRecordFactory.PUBSUB_USER_AGENT
        }
        request_mock.POST = {
            "message": {
                "attributes": {"attr_1": "AA"}
            }
        }

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record, BaseRecord)
        self.assertEquals(f'{request_mock.method} 200 Ok {request_mock.path}', base_record.message)
        self.assertIn("headers", base_record_dict.get('request'))
        self.assertIn("host", base_record_dict)
        self.assertIn("path", base_record_dict)
        self.assertEquals("AA", base_record_dict.get("attr_1"))
        self.assertEquals("header_1", base_record_dict.get('request').get("headers").get("HEADER_1"))
        self.assertEquals(json.loads(FakeHttpResponse.content), base_record_dict.get("response").get("body"))

    def test_process_request_post_pubsub_http_without_attributes(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "POST"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1",
            "HTTP_USER_AGENT": DjangoRecordFactory.PUBSUB_USER_AGENT
        }
        request_mock.POST = {
            "message": {
                "attributes": {}
            }
        }

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()

        self.assertIsInstance(base_record, BaseRecord)
        self.assertEquals(f'{request_mock.method} 200 Ok {request_mock.path}', base_record.message)
        self.assertIn("headers", base_record_dict.get('request'))
        self.assertIn("host", base_record_dict)
        self.assertIn("path", base_record_dict)
        self.assertEquals("header_1", base_record_dict.get('request').get("headers").get("HEADER_1"))
        self.assertNotIn("attr_1", base_record_dict)
        self.assertEquals(json.loads(FakeHttpResponse.content), base_record_dict.get("response").get("body"))

    def test_process_request_without_user_info(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "GET"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1",
            "USER_AGENT": "cosicas_raras",
        }
        request_mock.GET.lists.return_value = [
            ("param", "value")
        ]

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()

        self.assertIsNone(base_record_dict.get('request').get('headers').get('user_info'))

    def test_process_request_with_user_info(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "GET"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1",
            "USER_AGENT": "cosicas_raras",
            "HTTP_USER_INFO": "CourierApp/4.5.4 Android/11",
        }
        request_mock.GET.lists.return_value = [
            ("param", "value")
        ]

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()
        user_info = base_record_dict.get('user_info')

        self.assertEquals(user_info['app_name'], 'CourierApp')
        self.assertEquals(user_info['app_version'], '4.5.4')
        self.assertEquals(user_info['so_name'], 'Android')
        self.assertEquals(user_info['so_version'], '11')

    def test_process_request_with_user_info_wrong(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "GET"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1",
            "USER_AGENT": "cosicas_raras",
            "HTTP_USER_INFO": "CourierApp/4.5.4",
        }
        request_mock.GET.lists.return_value = [
            ("param", "value")
        ]

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()
        user_info = base_record_dict.get('user_info')

        self.assertEquals(user_info['app_name'], 'Bad format')
        self.assertEquals(user_info['app_version'], 'Bad format')
        self.assertEquals(user_info['so_name'], 'Bad format')
        self.assertEquals(user_info['so_version'], 'Bad format')

    def test_process_request_with_user_info_wrong_simple(self, request_mock):
        request_mock.get_host.return_value = "fake_host.com"
        request_mock.path = "/fake/path"
        request_mock.method = "GET"
        request_mock.META = {
            "HTTP_HEADER_1": "header_1",
            "USER_AGENT": "cosicas_raras",
            "HTTP_USER_INFO": "perico",
        }
        request_mock.GET.lists.return_value = [
            ("param", "value")
        ]

        base_record = DjangoRecordFactory(
            logger=FakeLogger(),
            response=FakeHttpResponse(),
            request=request_mock,
            request_body={},
            view_kwargs={}
        ).build()
        base_record_dict = base_record.to_dict()
        user_info = base_record_dict.get('user_info')

        self.assertEquals(user_info['app_name'], 'Bad format')
        self.assertEquals(user_info['app_version'], 'Bad format')
        self.assertEquals(user_info['so_name'], 'Bad format')
        self.assertEquals(user_info['so_version'], 'Bad format')
