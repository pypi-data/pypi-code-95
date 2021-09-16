# Copyright Okera Inc. All Rights Reserved.
#
# Tests for KV store API
#

import copy
import os
import unittest

from okera.tests import pycerebro_test_common as common
from okera._thrift_api import TKvStoreGetParams, TKvStorePutParams, TRecordServiceException

class KvStoreTest(common.TestBase):
    def _get_kv(self, conn, key):
        request = TKvStoreGetParams()
        request.key = key
        return conn.service.client.GetFromKvStore(request).value

    def _put_kv(self, conn, key, value):
        request = TKvStorePutParams()
        request.key = key
        request.value = value
        return conn.service.client.PutToKvStore(request)

    def test_basic(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._put_kv(conn, 'k1', 'value')
            value = self._get_kv(conn, 'k1')
            self.assertEqual(value, 'value')

            self._put_kv(conn, 'k1', 'value2')
            value = self._get_kv(conn, 'k1')
            self.assertEqual(value, 'value2')

            self._put_kv(conn, 'k1', '')
            value = self._get_kv(conn, 'k1')
            self.assertEqual(value, '')

            value = self._get_kv(conn, 'k2')
            self.assertEqual(value, None)

if __name__ == "__main__":
    unittest.main()
