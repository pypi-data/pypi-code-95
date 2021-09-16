# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Common methods for file format testing
#
# pylint: disable=line-too-long
# pylint: disable=too-many-locals
import json
import os
import subprocess
import shutil
import boto3
import requests

from okera.tests import pycerebro_test_common as common
from okera._thrift_api import TRecordServiceException

DEFAULT_PRESTO_PORT = int(os.environ['ODAS_TEST_PORT_PRESTO_COORD_HTTPS'])
DEFAULT_ENABLE_PRESTO = False
DEFAULT_ENABLE_SCAN_API = True
SCAN_API_RECORDS = 100

S3 = boto3.resource('s3')
TEST_BUCKET = 'cerebrodata-dev'

OKERA_HOME = os.environ["OKERA_HOME"]
OKERA_JAVA_VERSION = os.environ["OKERA_JAVA_VERSION"]
SCHEMA_TOOLS_JAR_NAME = OKERA_HOME + '/tools/schema-tools/target/schema-tools-' + \
    OKERA_JAVA_VERSION + '.jar'

class FileFormatTestBase(common.TestBase):

    @staticmethod
    def _get_test_iters(iters_default_value=None):
        # Run random generator tests
        if iters_default_value is not None:
            return iters_default_value
        if common.test_level_lt('checkin'):
            return 100
        if common.test_level_lt('ci'):
            return 1000
        return 5000

    @staticmethod
    def _get_test_unique_folder():
        # Use build_tag as unique identifier to avoid concurrent test run collisions.
        return os.getenv("BUILD_TAG", 'local')

    @staticmethod
    def _upload_s3(local_file_path, s3_file_path):
        s3_file_path = '%s/%s' % (FileFormatTestBase._get_test_unique_folder(),
                                  s3_file_path)
        S3.Bucket(TEST_BUCKET).upload_file(local_file_path, s3_file_path)
        return 's3://%s/%s' % (TEST_BUCKET, s3_file_path)

    @staticmethod
    def _write_s3(test_dir_prefix, path, data):
        test_dir_prefix = '%s/%s' % (FileFormatTestBase._get_test_unique_folder(),
                                     test_dir_prefix)
        filename = '%s/%s' % (test_dir_prefix, path)
        o = S3.Object(TEST_BUCKET, filename)
        o.put(Body=data)
        return 's3://%s/%s' % (TEST_BUCKET, filename)

    @staticmethod
    def _write_local_json_file(local_json_path, json_data):
        output = []
        for record in json_data:
            output.append(json.dumps(record))
        #print("output is: " + '\n'.join(output))
        with open(local_json_path, 'w') as outfile:
            outfile.write('\n'.join(output))

    @staticmethod
    def _read_local_json_file(local_json_path):
        expected_json = []
        with open(local_json_path, 'r') as data:
            for line in data:
                expected_json.append(json.loads(line))
        return expected_json

    @staticmethod
    def _generate_parquet(json_folder_path, parquet_folder_path):
        try:
            subprocess.check_output(['java', '-jar', SCHEMA_TOOLS_JAR_NAME, '--parquet',
                                     '--from-json', '--ignore-schema-errors',
                                     '--input-json-folder', json_folder_path,
                                     '--output-parquet-folder', parquet_folder_path],
                                    stderr=subprocess.STDOUT, timeout=300,
                                    universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise ValueError(e.output)

    @staticmethod
    def _generate_avro(avro_folder_path, test_schema_path, iters):
        try:
            subprocess.check_output(['java', '-jar', SCHEMA_TOOLS_JAR_NAME, '--avro',
                                     '--ignore-schema-errors',
                                     '--input-avro-schema', test_schema_path,
                                     '--output-avro-folder', avro_folder_path,
                                     '--sample-count', str(iters)],
                                    stderr=subprocess.STDOUT, timeout=300,
                                    universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise ValueError(e.output)

    @staticmethod
    def _recreate_dir(dir_name):
        try:
            shutil.rmtree(dir_name, ignore_errors=True)
            # put back empty folder, tests rely on the folder to exist.
            print('Creating directory: ' + dir_name)
            os.mkdir(dir_name)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    @staticmethod
    def _cleanup(test_dir_prefix, test_name, local_dir='', test_dirs=None):
        bucket = S3.Bucket(TEST_BUCKET)
        test_dir_prefix = '%s/%s' % (FileFormatTestBase._get_test_unique_folder(),
                                     test_dir_prefix)
        prefix = '%s/%s' % (test_dir_prefix, test_name)
        bucket.objects.filter(Prefix=prefix).delete()
        if (local_dir != ''):
            test_dir = '%s/%s' % (local_dir, test_name)
            FileFormatTestBase._recreate_dir(test_dir)
            for test_dir in test_dirs:
                full_local_dir = '%s/%s/%s' % (local_dir, test_name, test_dir)
                FileFormatTestBase._recreate_dir(full_local_dir)

    def _test_path(self, path, expected_json, test_db, test_table,
                   allow_missing=False, batch_mode=False,
                   test_presto=DEFAULT_ENABLE_PRESTO, sql=None, required_type=None,
                   sort_by_record_idx=False, test_scan_api=DEFAULT_ENABLE_SCAN_API,
                   file_format='JSON'):
        """ Runs schema inference and verification for the json file at path. Returns
            (SQL, skipped) on failure/skip and None on success.
        """
        if not sql:
            sql = '''
      CREATE EXTERNAL TABLE %s LIKE %s '%s'
      STORED AS %s
      LOCATION '%s' ''' % (test_table, file_format, path, file_format, path)
        presto_port = None
        if test_presto:
            presto_port = DEFAULT_PRESTO_PORT
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=presto_port) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % test_db)
            conn.execute_ddl('CREATE DATABASE %s' % test_db)
            try:
                conn.execute_ddl(sql)
            except TRecordServiceException as ex:
                # Skip failures if the schema is longer than 4000
                if batch_mode and 'exceeds maximum type length' in ex.detail:
                    return sql, True
                raise
            if not batch_mode:
                print("SQL: %s" % sql)
            actual_schema = conn.plan(test_table).schema
            # Use max_task_count to make the results stable
            actual_json_pyokera = conn.scan_as_json(test_table, strings_as_utf8=True,
                                                    max_task_count=1,
                                                    dialect='okera')
            if presto_port:
                actual_json_presto = conn.scan_as_json(
                    'SELECT * FROM %s' % test_table, strings_as_utf8=True,
                    max_task_count=1, dialect='presto')

            if test_scan_api:
                url = 'http://%s:%s/scan/%s?records=%s' % \
                    (os.getenv('ODAS_TEST_HOST'), os.getenv('ODAS_TEST_PORT_PLANNER_UI'),\
                    test_table, SCAN_API_RECORDS)
                actual_scan_json = json.loads(requests.get(url).text)

            # Verify count with multiple tasks splits generated returns correct results.
            # This is done by passing the min_task_size=5K.
            # We had issues with boundary conditions around the json file splits.
            # This test will ensure the count is correct with and without multiple tasks.
            # FIXME: we have a bug with avro small file split size, we need to fix and
            # enable this for all datatypes.
            if file_format.lower() != 'avro':
                data = conn.scan_as_json(
                    'SELECT COUNT(*) AS count FROM %s ' % test_table,
                    strings_as_utf8=False, min_task_size=5 * 1000)
                sum = 0
                for cnt in data:
                    sum += cnt['count']
                # compare results against the presto data size.
                # We don't have to requery for count.
                self.assertEqual(sum, len(actual_json_pyokera))

        self.assertTrue(actual_schema is not None)
        # Verify scanning with pyokera
        res = FileFormatTestBase.compare_json(
            self, actual_json_pyokera, expected_json, allow_missing,
            empty_struct_equals_null=True, batch_mode=batch_mode,
            required_type=required_type, empty_array_equals_null=True)
        if not res:
            return sql, False

        # Verify presto if enabled
        if presto_port:
            if sort_by_record_idx:
                # Presto return records in a "random" order if the result set is
                # sufficiently large. Sort them by a key that exists to get comparable
                # results.
                actual_json_presto = sorted(actual_json_presto, key=lambda k: k['idx'])
                expected_json = sorted(expected_json, key=lambda k: k['idx'])
            res = FileFormatTestBase.compare_json(
                self, actual_json_presto, expected_json, allow_missing,
                empty_struct_equals_null=True, batch_mode=batch_mode,
                required_type=required_type,
                empty_array_equals_null=True)
            if not res:
                return sql, False

        if test_scan_api:
            res = FileFormatTestBase.compare_json(
                self, actual_scan_json, expected_json[0:SCAN_API_RECORDS],
                allow_missing, empty_struct_equals_null=True,
                batch_mode=batch_mode, required_type=required_type,
                empty_array_equals_null=True)
            if not res:
                return sql, False

        return None, False
