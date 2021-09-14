import unittest

import json
import traceback
from datetime import datetime

from citibox.gcloudlogger.src.json_encoder import _JsonEncoder


class FakeException(Exception):
    def __init__(self, *args, **kwargs):
        self._tb = None
        super().__init__(*args, **kwargs)


class StringableClass:
    def __init__(self, value_1):
        self.value_1 = value_1

    def __str__(self):
        return str(self.value_1)


class NonStringableClass:
    def __init__(self):
        pass

    def __str__(self):
        raise Exception("you should not try this")


class TestJsonEncoder(unittest.TestCase):
    def test_date_json(self):
        some_date = datetime.now()

        my_data = {
            "date": some_date
        }

        result = json.dumps(my_data, cls=_JsonEncoder)

        date_regex = '^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
        self.assertRegex(json.loads(result).get('date'), date_regex)

    def test_log_with_exception(self):
        exc = FakeException("this should break things")

        my_data = {
            "exception": exc,
        }

        result = json.dumps(my_data, cls=_JsonEncoder)
        self.assertEqual("this should break things", json.loads(result).get('exception'))

    def test_anything_else(self):
        my_data = {
            "integer": 1,
            "string": "something",
            "class_with_str": StringableClass("something more")
        }

        result = json.dumps(my_data, cls=_JsonEncoder)
        self.assertEqual('{"integer": 1, "string": "something", "class_with_str": "something more"}', result)

    def test_strange_returns_none(self):
        my_data = {
            "klass": NonStringableClass()
        }

        result = json.dumps(my_data, cls=_JsonEncoder)
        self.assertEqual('{"klass": null}', result)
