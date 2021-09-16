# Copyright 2021 Okera Inc. All Rights Reserved.
#
# Tests for ORC support
# pylint: disable=bad-continuation,bad-indentation,global-statement,unused-argument
# pylint: disable=no-self-use
import unittest

from okera.tests import pycerebro_test_common as common
import cerebro_common as cerebro

DB = "orc_test_db"

class OrcTest(common.TestBase):
    def test_binary_data(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            tbl = "%s.%s" % (DB, "binary_data")
            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % (DB),
                "CREATE DATABASE %s" % (DB),
                """CREATE EXTERNAL TABLE %s (
                    bytes1 binary,
                    string1 string
                )
                STORED AS ORC
                LOCATION 's3://cerebrodata-test/orc/binary_data/'""" % (tbl),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            results = conn.scan_as_json(tbl)

            # Extracted from https://github.com/apache/orc/blob/7de5d89/examples/expected/TestOrcFile.testStringAndBinaryStatistics.jsn.gz
            expected_results = [
                {'string1': 'foo', 'bytes1': '\x00\x01\x02\x03\x04'},
                {'string1': 'bar', 'bytes1': '\x00\x01\x02\x03'},
                {'string1': None, 'bytes1': '\x00\x01\x02\x03\x04\x05'},
                {'string1': 'hi', 'bytes1': None}]

            assert results == expected_results

if __name__ == "__main__":
    unittest.main()
