import unittest

import json

from citibox.gcloudlogger.src.gcloud_formatter import GCloudFormatter
from citibox.gcloudlogger.test_helpers.logger_test_case import LoggerTestCase

class FakeException(Exception):
    def __init__(self, *args, **kwargs):
        self._tb = None
        super().__init__(*args, **kwargs)

class TestGcloudFormatter(LoggerTestCase):
    logger = None
    _formatter = GCloudFormatter

    def test_formatter(self):
        self.logger.info(
            "This is just a test, let's see what happens",
            extra={
                "extra_1": 123,
                "extra_2": "this is an extra"
            }
        )

        logged_result = json.loads(self.memory_logger.last_record)
        self.assertIn("message", logged_result)
        self.assertEqual("This is just a test, let's see what happens", logged_result.get('message'))

        self.assertIn("extra_1", logged_result)
        self.assertIn("extra_2", logged_result)
        self.assertIn("timestamp", logged_result)

    def test_formatter_with_exception(self):
        try:
            raise FakeException("this is failing for sure")
        except FakeException as e:
            self.logger.error(
                f'oops, it failed: {e}',
            )

        last_log = json.loads(self.memory_logger.last_record)
        self.assertIn("message", last_log)
        self.assertEqual("oops, it failed: this is failing for sure", last_log.get('message'))
        self.assertIn("timestamp", last_log)
