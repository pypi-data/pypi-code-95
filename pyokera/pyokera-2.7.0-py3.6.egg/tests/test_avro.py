# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Integration tests for avro in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-return
# pylint: disable=duplicate-code
# pylint: disable=line-too-long
import os
import pytest

from fastavro import reader
from okera.tests import file_format_test_common as fileFormat

LOCAL_DIR_PREFIX = '/tmp'
LOCAL_AVRO_DIR = 'test-avro'
TEST_DIR_PREFIX = 'avro-random-testing'
FILE_FORMAT = 'AVRO'

OKERA_HOME = os.environ["OKERA_HOME"]
TEST_AVRO_SAMPLE_SCHEMA_PATH = OKERA_HOME + \
                               '/tools/schema-tools/src/main/resources/test-schemas/'
TEST_DB = 'avro_test_db'
TEST_TABLE = TEST_DB + ".avro_tbl"

class AvroIntegrationTest(fileFormat.FileFormatTestBase):

    def _test_avro_files(self, local_avro_path, iters, path):

        if not os.listdir(local_avro_path):
            pytest.fail("Cannot find any generated files in test folder " + \
                         local_avro_path)

        processed_count = 0
        for file in os.listdir(local_avro_path):
            # Skip non-avro files.
            if not file.endswith(".avro"):
                continue
            else:
                processed_count += 1
                local_file_path = '%s/%s' % (local_avro_path, file)

                # Convert to json from avro file for comparison.
                output = []
                with open(local_file_path, 'rb') as f:
                    avro_reader = reader(f)
                    for record in avro_reader:
                        output.append(record)

                s3_file_path = '%s/%s/%s' % (TEST_DIR_PREFIX, path, file)
                # Upload generated avro file to s3 location.
                full_path = self._upload_s3(local_file_path, s3_file_path)

                print("Processing " + local_file_path)

                # Run comparison test using the avro file uploaded to the s3 location.
                self._test_path(full_path, output, TEST_DB, TEST_TABLE,
                                allow_missing=True, file_format=FILE_FORMAT)

        print("Total ignored samples: " + str(iters - processed_count) + "/" +
              str(iters))

    def _run_avro_random_tests(self, iters, path):
        iters = self._get_test_iters(iters)
        local_avro_path = '%s/%s/%s' % (LOCAL_DIR_PREFIX, path, LOCAL_AVRO_DIR)

        # Generate the avro file in the same temp path using java library.
        # Jar Location $OKERA_HOME/tools/schema-tools/
        self._generate_avro(local_avro_path, TEST_AVRO_SAMPLE_SCHEMA_PATH, iters)

        # Test all avro files in the folder.
        self._test_avro_files(local_avro_path, iters, path)

    def test_basic_random_schemas(self):
        test_name = 'avro-basic'
        self._cleanup(TEST_DIR_PREFIX, test_name, local_dir=LOCAL_DIR_PREFIX,
                      test_dirs=[LOCAL_AVRO_DIR])
        self._run_avro_random_tests(None, test_name)
        # Only cleanup on success, this helps with S3 consistency issues.
        self._cleanup(TEST_DIR_PREFIX, test_name, local_dir=LOCAL_DIR_PREFIX,
                      test_dirs=[LOCAL_AVRO_DIR])
