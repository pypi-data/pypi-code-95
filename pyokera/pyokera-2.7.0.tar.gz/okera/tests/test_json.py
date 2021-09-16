# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for json schema discovery
#
# pylint: disable=line-too-long
# pylint: disable=too-many-locals
# pylint: disable=duplicate-code

from datetime import datetime, timedelta
import decimal
from urllib.parse import urlparse
import json
import os
import time
import unittest

import boto3
import requests

from okera import _thrift_api
from okera.tests import pycerebro_test_common as common
from okera.tests import file_format_test_common as fileFormat
from okera._thrift_api import TTypeId

TEST_DB = 'json_test_db'
TEST_TABLE = TEST_DB + ".tbl"
DEFAULT_ENABLE_PRESTO = False

S3_TEST_FILES = [
    's3://cerebrodata-test/chase/json-empty/chase-json-test.json',
    's3://cerebrodata-test/chase/json-simple/chase-json-test.json',
    's3://cerebrodata-dev/json-random-testing/cases/case1/data.json',
    's3://cerebrodata-dev/json-random-testing/cases/case1/data2.json',
    's3://cerebrodata-dev/json-random-testing/cases/case1/data3.json',
    's3://cerebrodata-dev/json-random-testing/cases/case1/data4.json',
    's3://cerebrodata-dev/json-random-testing/cases/case1/data5.json',
    's3://cerebrodata-dev/json-random-testing/cases/len-mismatch/data.json',
    's3://cerebrodata-dev/json-random-testing/cases/merge-basic/data.json',
    's3://cerebrodata-dev/json-random-testing/cases/merge2/data.json',
    's3://cerebrodata-dev/json-random-testing/cases/merge3/data.json',
    's3://cerebrodata-dev/json-random-testing/cases/merge4/data.json',

    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1211.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1211_fees.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1216.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1216_with_subscriptionLimit.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_1.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_2.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_3.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_4.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_5.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_6.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_7.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_8.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_9.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_parquet_ledger_balance.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_parquet_ledger_transaction.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_parquet_party.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_parquet_product.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1238_parquet_subscription.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1269.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1269_avro2.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1269_avro_null_fields.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1269_partitioned-files.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1269_problem_file.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1269_success1.json',
    's3://cerebro-customers/chase/jsonified/downloads_chase_zd1269_success2.json',

    # simdjson website example jsons
    's3://cerebrodata-dev/simdjson/jsonexamples/small/jsoniter_scala/che-1.geo.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/small/jsoniter_scala/che-2.geo.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/small/jsoniter_scala/che-3.geo.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/small/smalldemo.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/google_maps_api_compact_response.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/mesh.json',
]

S3_TEST_ERROR_FILES = [
    # Fails to infer the schema, top level is array, not record which is not valid.
    's3://cerebrodata-dev/simdjson/jsonexamples/small/truenull.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/amazon_cellphones.ndjson',

    # Fails with json.decoder.JSONDecodeError: Expecting property name enclosed
    # in double quotes: line 1 column 2 (char 1)
    's3://cerebrodata-dev/simdjson/jsonexamples/small/adversarial.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/small/demo.json',

    # Column name in file has a quote in it, which is not a valid column name
    's3://cerebrodata-dev/simdjson/jsonexamples/small/flatadversarial.json',

    # Longer than 500K in one record
    's3://cerebrodata-dev/simdjson/jsonexamples/marine_ik.json',
    's3://cerebrodata-dev/simdjson/jsonexamples/update-center.json',
]

# URLs that return json. The second argument is if the JSON has a root level key
# that is really the entire table
TEST_URLS = [
    # These work. Taken from: https://github.com/jdorfman/awesome-json-datasets
    ('https://blockchain.info/unconfirmed-transactions?format=json', 'txs'),
    ('https://data.police.uk/api/leicestershire/neighbourhoods', ''),
    ('https://data.police.uk/api/forces', ''),
    ('https://pokeapi.co/api/v2/pokemon/1/', 'abilities'),
    ('https://pokeapi.co/api/v2/ability/1', 'effect_changes'),
    ('https://data.parliament.scot/api/members', ''),
    ('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson', 'features'),
    ('http://showtimes.everyday.in.th/api/v2/movie/', None),
    ('http://showtimes.everyday.in.th/api/v2/theater/', None),
    ('https://www.govtrack.us/api/v2/role?current=true&role_type=representative&limit=438', 'objects'),
    ('https://data.nasa.gov/resource/2vr3-k9wn.json', ''),
    ('http://api.nobelprize.org/v1/country.json', 'countries'),
    ('http://api.nobelprize.org/v1/laureate.json', 'laureates'),
    ('http://api.nobelprize.org/v1/prize.json', 'prizes'),
    ('https://raw.githubusercontent.com/Biuni/PokemonGO-Pokedex/master/pokedex.json', 'pokemon'),
    ('https://raw.githubusercontent.com/prust/wikipedia-movie-data/master/movies.json', ''),

    # simdjson test cases
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/apache_builds.json', 'jobs'),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/github_events.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/google_maps_api_compact_response.json', None),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/google_maps_api_response.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/instruments.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/mesh.json', None),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/mesh.pretty.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/random.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/repeat.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/repeat.json', 'result'),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/tree-pretty.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/twitter.json', 'statuses'),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/twitter_api_compact_response.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/twitter_timeline.json', ''),
    ('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/twitterescaped.json', 'statuses'),
]

TEST_ERROR_URLS = [
    # These work but the contents of these change constantly
    #('https://blockchain.info/latestblock', None),
    #('http://api.open-notify.org/iss-now.json', None),
    #('http://api.open-notify.org/astros.json', None),
    #('https://api.exchangerate-api.com/v4/latest/USD', None),
    #('https://api.exchangerate-api.com/v4/latest/GBP', None),
    #('https://data.gov.au/geoserver/abc-local-stations/wfs?request=GetFeature&typeName=ckan_d534c0e9_a9bf_487b_ac8f_b7877a09d162&outputFormat=json', None),

    # FIXME: Keys normalize to _ instead of -
    #('https://data.police.uk/api/crimes-street-dates', ''),
    #('https://www.govtrack.us/api/v2/role?current=true&role_type=senator', 'objects'),

    # FIXME: Keys normalize @ to empty so column is missing
    #('https://data.nasa.gov/resource/y77d-th95.json', ''),

    # FIXME: Keys have fields with spaces in them
    #('https://api.github.com/gists', ''),

    # TODO: keys are ints which is generating sometihing invalid?
    #('https://www.ncdc.noaa.gov/cag/global/time-series/globe/land_ocean/ytd/12/1880-2016.json', None),

    # TODO: schema length over 4000
    #('https://api.github.com/events', ''),

    # The top level is an array (not record, so this is an invalid json)
    #('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/marine_ik.json', ''),
    # This contains a single record over 500K
    #('https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/numbers.json', ''),
]

TEST_DB = 'json_test_db'
TEST_TABLE = TEST_DB + ".tbl"
S3 = boto3.resource('s3')
TEST_BUCKET = 'cerebrodata-dev'
TEST_DIR_PREFIX = 'json-random-testing'
FILE_FORMAT = 'JSON'

class JsonIntegrationTest(fileFormat.FileFormatTestBase):

    def __test_s3(self, path, allow_missing=False, test_scan_api=False):
        # Read it directly using python libraries
        o = urlparse(path, allow_fragments=False)
        obj = S3.Object(o.netloc, o.path.lstrip('/'))
        expected_json = []
        for line in obj.get()['Body'].read().decode('utf-8').strip().split('\n'):
            expected_json.append(json.loads(line))
        self._test_path(path, expected_json, TEST_DB, TEST_TABLE, allow_missing,
                        test_scan_api=test_scan_api, file_format=FILE_FORMAT)

    def __test_url(self, url, key, expected_json=None):
        print("Testing (%s, %s)" % (url, key))
        expected_json = json.loads(requests.get(url).text)
        if key is None:
            expected_json = [expected_json]
            self._test_path(url, expected_json, TEST_DB, TEST_TABLE, allow_missing=True,
                            file_format=FILE_FORMAT)
            return

        # There is a key, we need to transform the data
        if key:
            expected_json = expected_json[key]
        elif isinstance(expected_json, dict):
            expected_json = [expected_json]

        data = []
        for record in expected_json:
            data.append(json.dumps(record))
        path = self._write_s3(TEST_DIR_PREFIX, 'json-http-testing/data.json',
                              '\n'.join(data))
        self._test_path(path, expected_json, TEST_DB, TEST_TABLE, allow_missing=True,
                        file_format=FILE_FORMAT)

    def _run_random_tests(self, generator, iters, path):
        # Run random generator tests
        if iters is None:
            iters = 100

        for idx in range(0, iters):
            generator.new_schema()
            data = generator.generate()
            print("Generated json for test case%s:\n%s" % \
                  (idx, json.dumps(data, indent=2, sort_keys=True)))
            filename = '%s/test-%s.json' % (path, idx)
            output = []
            for record in data:
                output.append(json.dumps(record))
            full_path = self._write_s3(TEST_DIR_PREFIX, filename, '\n'.join(output))
            self._test_path(full_path, data, TEST_DB, TEST_TABLE, allow_missing=True,
                            file_format=FILE_FORMAT)

    @unittest.skip("Example for use during development to test a specific dataset.")
    def test_single_dataset(self):
        self.__test_s3('s3://cerebrodata-test/chase/json-simple/chase-json-test.json')

    @unittest.skip("Example for use during development to test a specific dataset.")
    def test_single_url(self):
        self.__test_url('https://blockchain.info/latestblock', None)

    def test_s3(self):
        for f in S3_TEST_FILES:
            self.__test_s3(f, allow_missing=True, test_scan_api=True)

    def valid_json_api(self, url):
        ctx = common.get_test_context()
        disable_prop = "WITH SERDEPROPERTIES('new.line.json'='true') "
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('CREATE DATABASE IF NOT EXISTS %s' % TEST_DB)

            # Explicit schema
            conn.execute_ddl('DROP TABLE IF EXISTS %s' % TEST_TABLE)
            conn.execute_ddl(
                ("CREATE EXTERNAL TABLE %s(revenue BIGINT) STORED AS JSON " +
                 "LOCATION '%s'") % (TEST_TABLE, url))
            json = conn.scan_as_json(TEST_TABLE, max_records=2)
            # TODO: not sure how stable this live endpoint is so making the validation
            # less strict
            self.assertEqual(2, len(json))
            self.assertEqual(1, len(json[0]))
            self.assertTrue('revenue' in json[0])

            # Explicitly disable new line json, this won't scan right
            conn.execute_ddl('DROP TABLE %s' % TEST_TABLE)
            conn.execute_ddl(
                ("CREATE EXTERNAL TABLE %s(revenue BIGINT) %s " +
                 "STORED AS JSON " +
                 "LOCATION '%s'") % (TEST_TABLE, disable_prop, url))
            json = conn.scan_as_json(TEST_TABLE, max_records=2)
            self.assertEqual([], json)

            # Infer full schema
            conn.execute_ddl('DROP TABLE %s' % TEST_TABLE)
            conn.execute_ddl(
                ("CREATE EXTERNAL TABLE %s " +
                 "LIKE JSON '%s' " +
                 "STORED AS JSON " +
                 "LOCATION '%s'") % (TEST_TABLE, url, url))
            json = conn.scan_as_json(TEST_TABLE, max_records=2)
            self.assertEqual(2, len(json))
            self.assertTrue(len(json[0]) > 20)
            self.assertTrue('revenue' in json[0])
            self.assertTrue('symbol' in json[0])

            # Disable new line json, we won't infer it right
            conn.execute_ddl('DROP TABLE %s' % TEST_TABLE)
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    ("CREATE EXTERNAL TABLE %s " +
                     "LIKE JSON '%s' %s " +
                     "STORED AS JSON " +
                     "LOCATION '%s'") % (TEST_TABLE, url, disable_prop, url))
            print(ex_ctx.exception)
            self.assertTrue('Failed to read JSON schema' in str(ex_ctx.exception))

    def test_json_api(self):
        # this endpoint responds with 403, disabling this one for now
        url = 'https://financialmodelingprep.com/api/v3/income-statement/AAPL?' +\
            'limit=10&apikey='
        # Hardcoded apikey

        # self.valid_json_api(url + 'demo')
        # Dynamically returned api key
        # self.valid_json_api(url + '${script:/get-financialmodelingprep-apikey.sh}')

    def test_json_api_path(self):
        ctx = common.get_test_context()
        path_prop = "WITH SERDEPROPERTIES('json.records-start.path'='content') "
        url = 'https://gist.githubusercontent.com/nongli/' +\
            'd7e30635e466a9352bbcaacfb36a1c09/raw/' +\
            'fea92d963c724fd2d6e1e71fd2c9cba7daa3e277/gistfile1.txt'

        with common.get_planner(ctx) as conn:
            conn.execute_ddl('CREATE DATABASE IF NOT EXISTS %s' % TEST_DB)

            conn.execute_ddl('DROP TABLE IF EXISTS %s' % TEST_TABLE)
            conn.execute_ddl(
                ("CREATE EXTERNAL TABLE %s " +
                 "LIKE JSON '%s' %s" +
                 "STORED AS JSON " +
                 "LOCATION '%s'") % (TEST_TABLE, url, path_prop, url))
            json = conn.scan_as_json(TEST_TABLE)
            self.assertEqual(1, len(json))
            self.assertEqual(len(json[0]), 5)
            self.assertEqual(json[0]['bdrid'], '3095')
            self.assertEqual(json[0]['subtype'], 'OFFICE')

            # Set the config on the DB, it should apply to all tables in it
            conn.execute_ddl('DROP DATABASE %s CASCADE' % TEST_DB)
            conn.execute_ddl('CREATE DATABASE %s' % TEST_DB)
            conn.execute_ddl(
                ("ALTER DATABASE %s SET DBPROPERTIES(" + \
                "'json.records-start.path'='content')") % TEST_DB)
            conn.execute_ddl(
                ("CREATE EXTERNAL TABLE %s " +
                 "LIKE JSON '%s'" +
                 "STORED AS JSON " +
                 "LOCATION '%s'") % (TEST_TABLE, url, url))
            json = conn.scan_as_json(TEST_TABLE)
            self.assertEqual(1, len(json))
            self.assertEqual(len(json[0]), 5)
            self.assertEqual(json[0]['bdrid'], '3095')
            self.assertEqual(json[0]['subtype'], 'OFFICE')

    def test_json_count(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            data = conn.scan_as_json(
                'select count(*) as cnt from rs_json_format.airlines_mini',
                strings_as_utf8=False,
                min_task_size=5 * 1000)
            # for this dataset we expect exactly 1 task splits as json is not splittable
            self.assertTrue(len(data) == 1)
            sum = 0
            for cnt in data:
                sum += cnt['cnt']
            self.assertEqual(sum, 100)

    @unittest.skipIf(common.TEST_LEVEL != "all", "This writes to the same location in s3")
    def test_type_conversion(self):
        # This test does not use schema infernce and instead explicitly creates the
        # types with some interesting values
        data = {
            'c1': 0,
            'c2': None,
            'c3': '',
            'c4': '123',
            'c5': '4.56',
            'c6': 'value',
            'c7': 'vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv',
            'c8': '2020-01-01',
            'c9': '2020-01-01 01:01:01',
        }

        types = [
            ('STRING', None),
            ('BOOLEAN', bool),
            ('TINYINT', int),
            ('SMALLINT', int),
            ('INT', int),
            ('BIGINT', int),
            ('FLOAT', float),
            ('DOUBLE', float),
            ('DATE', None),
            ('TIMESTAMP', None),

            ('VARCHAR(1)', None),
            ('VARCHAR(5)', None),
            ('VARCHAR(40)', None),

            ('CHAR(1)', None),
            ('CHAR(5)', None),
            ('CHAR(40)', None),

            ('DECIMAL(1, 0)', None),
            ('DECIMAL(10, 1)', decimal.Decimal),
            ('DECIMAL(19, 2)', decimal.Decimal),
            ('DECIMAL(38, 10)', decimal.Decimal),
        ]

        for t in types:
            cols = []
            for i in range(1, len(data) + 1):
                cols.append('c' + str(i) + ' ' + t[0])

            record = data.copy()
            if t[0] in ['DATE', 'TIMESTAMP']:
                # If it's date/timestamp we need to NULL out the other columns and
                # adjust the expected values
                for i in range(1, len(data) + 1):
                    if i in [8, 9]:
                        continue
                    record['c' + str(i)] = None
                if t[0] == 'DATE':
                    record['c9'] = record['c8']
            elif t[0].startswith('VARCHAR') or t[0].startswith('CHAR'):
                # Fix up VARCHAR, the result can't go over the length
                for i in range(1, len(data) + 1):
                    n = int(t[0].split('(')[1].split(')')[0])
                    c = 'c' + str(i)
                    if record[c] is None:
                        continue
                    v = str(record[c])
                    record[c] = v[0:min(len(v), n)]

                    # For CHAR, we need to pad to the max length
                    if t[0].startswith('CHAR'):
                        for _ in range(0, n - len(v)):
                            record[c] += ' '
            elif t[0] == 'DECIMAL(1, 0)':
                # This is not a great way to write these tests
                for i in range(1, len(data) + 1):
                    c = 'c' + str(i)
                    record[c] = None
                record['c1'] = 0
            elif t[0] == 'DECIMAL(10, 1)':
                # This is not a great way to write these tests
                for i in range(1, len(data) + 1):
                    c = 'c' + str(i)
                    record[c] = None
                record['c1'] = 0.0
                record['c4'] = 123.0
            elif t[0] == 'DECIMAL(19, 2)':
                # This is not a great way to write these tests
                for i in range(1, len(data) + 1):
                    c = 'c' + str(i)
                    record[c] = None
                record['c1'] = 0.0
                record['c4'] = 123.0
                record['c5'] = 4.56
            elif t[0] == 'DECIMAL(38, 10)':
                # This is not a great way to write these tests
                for i in range(1, len(data) + 1):
                    c = 'c' + str(i)
                    record[c] = None
                record['c1'] = 0.0
                record['c4'] = 123.00
                record['c5'] = 4.56

            contents = []
            for _ in range(0, 3):
                contents.append(json.dumps(data))

            path = self._write_s3(TEST_DIR_PREFIX, 'type-conversion/data.json',
                                  '\n'.join(contents))
            create = '''
        CREATE EXTERNAL TABLE %s(%s)
        STORED AS JSON
        LOCATION '%s' ''' % \
            (TEST_TABLE, ', '.join(cols), path)
            self._test_path(path, [record, record, record], TEST_DB, TEST_TABLE,
                            sql=create, required_type=t[1],
                            file_format=FILE_FORMAT)

    @unittest.skipIf(common.TEST_LEVEL != "all",
                     "Not very stable, downloads from internet.")
    def test_urls(self):
        for url in TEST_URLS:
            self.__test_url(url[0], url[1])

    @unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
    def test_basic_random_schemas(self):
        self._cleanup(TEST_DIR_PREFIX, 'basic/')
        generator = common.JsonGenerator(
            seed=int(time.time() * 1000))
        self._run_random_tests(generator, None, 'basic')
        # Only cleanup on success, this helps with S3 consistency issues.
        self._cleanup(TEST_DIR_PREFIX, 'basic/')

    @unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
    def test_basic_schema_merge(self):
        self._cleanup(TEST_DIR_PREFIX, 'merge/')
        generator = common.JsonGenerator(
            seed=int(time.time() * 1000),
            min_records=2,
            max_recursion=3,
            max_records=3,
            null_probability=0,
            empty_record_probability=0,
            missing_fields_probability=0,
            generate_variadic_schema=True)
        self._run_random_tests(generator, None, 'merge')
        # Only cleanup on success, this helps with S3 consistency issues.
        self._cleanup(TEST_DIR_PREFIX, 'merge/')

    @unittest.skip("Finding too many bugs")
    def test_medium_random_schemas(self):
        self._cleanup(TEST_DIR_PREFIX, 'medium/')
        generator = common.JsonGenerator(
            seed=int(time.time() * 1000),
            null_probability=.15,
            min_fields=1,
            max_fields=7,
            max_array_len=4,
            max_recursion=6)
        self._run_random_tests(generator, None, 'medium')
        # Only cleanup on success, this helps with S3 consistency issues.
        self._cleanup(TEST_DIR_PREFIX, 'medium/')

    @unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
    def test_long_running(self):
        # Runs the test for a fixed amount of time or until the max failures are
        # hit. This will archive the test files to S3 for async debugging.
        print("\n\n----------------------------------------------------------------")
        generator = common.JsonGenerator(
            seed=int(time.time() * 1000),
            null_probability=.05,
            empty_record_probability=.05,
            missing_fields_probability=.05,
            min_fields=1,
            max_fields=7,
            max_array_len=4,
            max_recursion=6,
            generate_empty_record_all_types=True,
            generate_variadic_schema=True)
        self._test_long_running(generator)

    @unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
    def test_larger_long_running(self):
        # Runs the test for a fixed amount of time or until the max failures are
        # hit. This will archive the test files to S3 for async debugging.
        print("\n\n----------------------------------------------------------------")
        generator = common.JsonGenerator(
            seed=int(time.time() * 1000),
            null_probability=.05,
            empty_record_probability=0.01,
            missing_fields_probability=.05,
            min_fields=3,
            max_fields=7,
            max_array_len=5,
            max_recursion=6,
            min_records=100,
            max_records=200,
            generate_empty_record_all_types=True,
            generate_variadic_schema=True)
        self._test_long_running(generator)

    @unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
    def test_even_larger_long_running(self):
        # Runs the test for a fixed amount of time or until the max failures are
        # hit. This will archive the test files to S3 for async debugging.
        print("\n\n----------------------------------------------------------------")
        generator = common.JsonGenerator(
            types=[[TTypeId.STRING]],
            seed=int(time.time() * 1000),
            null_probability=.05,
            empty_record_probability=0,
            missing_fields_probability=0,
            min_fields=1,
            max_fields=2,
            max_array_len=5,
            max_recursion=1,
            min_records=10000,
            max_records=50000,
            generate_empty_record_all_types=False,
            generate_variadic_schema=False)
        self._test_long_running(generator)

    def _test_long_running(self, generator):
        # Max failures and duration to run
        max_failures = 5
        duration_sec = 30
        test_presto = DEFAULT_ENABLE_PRESTO
        if 'JSON_TEST_MAX_FAILURES' in os.environ:
            max_failures = int(os.environ['JSON_TEST_MAX_FAILURES'])
        if 'JSON_TEST_DURATION_SECS' in os.environ:
            duration_sec = int(os.environ['JSON_TEST_DURATION_SECS'])
        if 'JSON_TEST_PRESTO' in os.environ:
            test_presto = os.environ['JSON_TEST_PRESTO'].lower() == 'true'

        total_tests = 0
        total_success = 0
        total_skips = 0
        failures = []

        # Generate a random directory to store failures
        start = datetime.now()
        directory = start.strftime("%Y-%m-%d-%H-%M-%S")
        print("Generating test data in: s3://%s/%s/%s/" %\
              (TEST_BUCKET, TEST_DIR_PREFIX, directory))
        print("    Test presto: %s" % test_presto)
        end = start + timedelta(seconds=duration_sec)

        while datetime.now() < end:
            total_tests += 1
            generator.new_schema()

            # If testing with presto, we need to generate with a record idx so we can
            # sort the result set for comparison.
            data = generator.generate(generate_record_idx=test_presto)
            filename = '%s/test-case-%s/data.json' % (directory, total_tests)

            output = []
            for record in data:
                output.append(json.dumps(record))
            full_path = self._write_s3(TEST_DIR_PREFIX, filename, '\n'.join(output))

            sql, skip = self._test_path(
                full_path, data, TEST_DB, TEST_TABLE, allow_missing=True, batch_mode=True,
                test_presto=test_presto, sort_by_record_idx=test_presto,
                file_format=FILE_FORMAT)
            if not sql:
                total_success += 1
                continue
            if skip:
                total_skips += 1
                continue
            failures.append((full_path, sql))

            if len(failures) >= max_failures:
                break

        print("\n----------------------------------------------------------------")
        print("Total tests duration: %s" % (datetime.now() - start))
        print("Total tests runs: %s" % total_tests)
        print("Total successful: %s" % total_success)
        print("Total skips: %s" % total_skips)
        print("Total failures: %s" % len(failures))

        if not failures:
            return

        print("Tests which failed.\n")
        for (path, sql) in failures:
            print("----------------------------------------------------------------")
            print("Path: %s" % path)
            print("SQL: %s\n" % sql)

        self.fail("Found failures")
