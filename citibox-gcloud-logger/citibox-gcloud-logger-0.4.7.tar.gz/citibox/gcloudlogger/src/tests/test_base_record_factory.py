import unittest
from typing import Optional
from unittest import mock

from citibox.gcloudlogger.src import LogException
from citibox.gcloudlogger.src.base_record import Body, Params, RequestHeaders, ResponseHeaders, UserInfo, ExceptionInfo
from citibox.gcloudlogger.src.base_record_factory import BaseLogRecordFactory


class BaseRecordFactoryImplementation(BaseLogRecordFactory):
    def _get_user_info(self) -> Optional[UserInfo]:
        return mock.create_autospec(UserInfo, spec_set=True)

    def _build_response_body(self) -> Body:
        return mock.create_autospec(Body, spec_set=True)

    def _build_response_headers(self) -> ResponseHeaders:
        return mock.create_autospec(ResponseHeaders, spec_set=True)

    def _build_request_headers(self) -> RequestHeaders:
        return mock.create_autospec(ResponseHeaders, spec_set=True)

    def _build_request_params(self) -> Params:
        return mock.create_autospec(Params, spec_set=True)

    def _build_request_body(self) -> Body:
        return mock.create_autospec(Body, spec_set=True)

    def _get_request_uri_path(self) -> str:
        return 'some/path/'

    def _get_request_view_params(self) -> dict:
        return {
            'some': 'params'
        }

    def _get_method(self) -> str:
        return 'method'

    def _get_host(self) -> str:
        return 'host.com'

    def _get_status_code(self) -> str:
        return '200'

    def _build_pubsub_request_attributes(self) -> dict:
        return {
            'some': 'params'
        }


class TestBaseRecordFactory(unittest.TestCase):

    def test_build_exception_without_exception_implemented(self):
        factory = BaseRecordFactoryImplementation()
        exception = factory._build_exception()
        self.assertIsNone(exception)

    def test_build_exception_with_empty_exception(self):
        factory = BaseRecordFactoryImplementation()
        factory.exception = None
        exception = factory._build_exception()
        self.assertIsNone(exception)

    def test_build_exception_with_exception_info(self):
        log_exception = mock.create_autospec(LogException, spec_set=True)
        type(log_exception).exception = Exception()
        log_exception.exception.args = ('whatever', )
        type(log_exception).traceback = 'sometraceback'

        factory = BaseRecordFactoryImplementation()
        factory.exception = log_exception
        exception = factory._build_exception()
        self.assertIsInstance(exception, ExceptionInfo)
        self.assertEquals(exception._name, 'Exception')
        self.assertEquals(exception._args, ['whatever', ])
        self.assertEquals(exception._traceback, 'sometraceback')
