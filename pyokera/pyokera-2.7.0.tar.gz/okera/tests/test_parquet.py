# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Some integration tests for parquet in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-return
# pylint: disable=duplicate-code
# pylint: disable=line-too-long

import time
import os
import pytest

from okera.tests import pycerebro_test_common as common
from okera.tests import file_format_test_common as fileFormat

LOCAL_DIR_PREFIX = '/tmp'
LOCAL_JSON_DIR = 'test-json'
LOCAL_PARQUET_DIR = 'test-parquet'
TEST_DIR_PREFIX = 'parquet-random-testing'
FILE_FORMAT = 'PARQUET'

TEST_DB = 'parquet_test_db'
TEST_TABLE = TEST_DB + ".parq_tbl"

class ParquetIntegrationTest(fileFormat.FileFormatTestBase):

    def _test_parquet_files(self, local_json_path, local_parquet_path, iters, path):
        processed_count = 0

        if not os.listdir(local_parquet_path):
            pytest.fail("Cannot find any generated files in test folder " + \
                         local_parquet_path)

        for file in os.listdir(local_parquet_path):
            # skip .crc files generate by parquet generator.
            if not file.endswith(".parquet"):
                continue
            else:
                processed_count += 1
                json_file_path = '%s/%s.json' % (local_json_path,
                                                 os.path.splitext(file)[0])
                json_data = self._read_local_json_file(json_file_path)
                local_file_path = '%s/%s' % (local_parquet_path, file)
                s3_file_path = '%s/%s/%s' % (TEST_DIR_PREFIX, path, file)
                # Upload generated parquet file to s3 location.
                full_path = self._upload_s3(local_file_path, s3_file_path)

                # Run comparison test using the parquet file uploaded to the s3 location.
                self._test_path(full_path, json_data, TEST_DB, TEST_TABLE,
                                allow_missing=True, file_format=FILE_FORMAT)

        print("Total ignored samples: " + str(iters - processed_count) + "/" +
              str(iters))


    def _run_parquet_random_tests(self, json_generator, iters, path):
        iters = self._get_test_iters(iters)
        local_parquet_path = '%s/%s/%s' % (LOCAL_DIR_PREFIX, path, LOCAL_PARQUET_DIR)
        local_json_path = '%s/%s/%s' % (LOCAL_DIR_PREFIX, path, LOCAL_JSON_DIR)

        for idx in range(0, iters):
            # Generate random JSON data
            json_generator.new_schema()
            #print("Generated json for test case%s:\n%s" % \
            #      (idx, json.dumps(json_data, indent=2, sort_keys=True)))
            local_json_file = '%s/test-%s.json' % (local_json_path, idx)

            # Write to a json file in a local temp path.
            self._write_local_json_file(local_json_file, json_generator.generate())

        # Generate the parquet file in the same temp path using java library.
        # Jar Location $OKERA_HOME/tools/schema-tools/
        self._generate_parquet(local_json_path, local_parquet_path)

        # Test all parquet files in the folder.
        self._test_parquet_files(local_json_path, local_parquet_path, iters, path)

    def test_basic_random_schemas(self):
        test_name = 'parquet-basic'
        self._cleanup(TEST_DIR_PREFIX, test_name, local_dir=LOCAL_DIR_PREFIX,
                      test_dirs=[LOCAL_JSON_DIR, LOCAL_PARQUET_DIR])
        generator = common.JsonGenerator(
            seed=int(time.time() * 1000))
        self._run_parquet_random_tests(generator, None, test_name)
        # Only cleanup on success, this helps with S3 consistency issues.
        self._cleanup(TEST_DIR_PREFIX, test_name, local_dir=LOCAL_DIR_PREFIX,
                      test_dirs=[LOCAL_JSON_DIR, LOCAL_PARQUET_DIR])
