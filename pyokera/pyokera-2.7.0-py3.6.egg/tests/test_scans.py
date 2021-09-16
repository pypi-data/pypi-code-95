# Copyright 2017 Okera Inc. All Rights Reserved.
#
# Tests that should run on any configuration. The server auth can be specified
# as an environment variables before running this test.
# pylint: disable=bad-continuation,bad-indentation,global-statement,unused-argument
# pylint: disable=no-self-use
import time
import unittest
import json
import numpy

from okera._thrift_api import TTypeId

from okera.tests import pycerebro_test_common as common
import cerebro_common as cerebro

retry_count = 0

class BasicTest(common.TestBase):
    def test_sparse_data(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            df = planner.scan_as_pandas("rs.sparsedata")
            self.assertEqual(96, len(df), msg=df)
            self.assertEqual(68, df['age'].count(), msg=df)
            self.assertEqual(10.0, df['age'].min(), msg=df)
            self.assertEqual(96.0, df['age'].max(), msg=df)
            self.assertEqual(b'sjc', df['defaultcity'].max(), msg=df)
            self.assertEqual(86, df['description'].count(), msg=df)

    def test_nulls(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            df = planner.scan_as_pandas("select string_col from rs.alltypes_null")
            self.assertEqual(1, len(df), msg=df)
            self.assertTrue(numpy.isnan(df['string_col'][0]), msg=df)

            df = planner.scan_as_pandas(
                "select length(string_col) as c from rs.alltypes_null")
            self.assertEqual(1, len(df), msg=df)
            self.assertTrue(numpy.isnan(df['c'][0]), msg=df)

    def test_timestamp_functions(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json("""
                select date_add('2009-01-01', 10) as c from okera_sample.sample""")
            self.assertTrue(len(json) == 2, msg=json)
            self.assertEqual('2009-01-11 00:00:00.000', str(json[0]['c']), msg=json)
            self.assertEqual('2009-01-11 00:00:00.000', str(json[1]['c']), msg=json)

    def test_duplicate_cols(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json("""
                select record, record from okera_sample.sample""")
            self.assertTrue(len(json) == 2, msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record']),
                             msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record_2']),
                             msg=json)

        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json("""
                select record, record as record_2, record from okera_sample.sample""")
            self.assertTrue(len(json) == 2, msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record']),
                             msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record_2']),
                             msg=json)
            self.assertEqual('This is a sample test file.', str(json[0]['record_2_2']),
                             msg=json)

    def test_large_decimals(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json("select num from rs.large_decimals2")
            self.assertTrue(len(json) == 6, msg=json)
            self.assertEqual('9012248907891233.020304050670',
                             str(json[0]['num']), msg=json)
            self.assertEqual('2343.999900000000', str(json[1]['num']), msg=json)
            self.assertEqual('900.000000000000', str(json[2]['num']), msg=json)
            self.assertEqual('32.440000000000', str(json[3]['num']), msg=json)
            self.assertEqual('54.230000000000', str(json[4]['num']), msg=json)
            self.assertEqual('4525.340000000000', str(json[5]['num']), msg=json)

        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            df = planner.scan_as_pandas("select num from rs.large_decimals2")
            self.assertTrue(len(df) == 6, msg=df)
            self.assertEqual('9012248907891233.020304050670',
                             str(df['num'][0]), msg=df)
            self.assertEqual('2343.999900000000', str(df['num'][1]), msg=df)
            self.assertEqual('900.000000000000', str(df['num'][2]), msg=df)
            self.assertEqual('32.440000000000', str(df['num'][3]), msg=df)
            self.assertEqual('54.230000000000', str(df['num'][4]), msg=df)
            self.assertEqual('4525.340000000000', str(df['num'][5]), msg=df)

    def test_date(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json("select * from datedb.date_csv")
            self.assertTrue(len(json) == 2, msg=json)
            self.assertEqual('Robert', str(json[0]['name']), msg=json)
            self.assertEqual(100, json[0]['id'], msg=json)
            self.assertEqual('1980-01-01', str(json[0]['dob']), msg=json)
            self.assertEqual('Michelle', str(json[1]['name']), msg=json)
            self.assertEqual(200, json[1]['id'], msg=json)
            self.assertEqual('1991-12-31', str(json[1]['dob']), msg=json)

        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            pd = planner.scan_as_pandas("select * from datedb.date_csv")
            self.assertTrue(len(pd) == 2, msg=pd)
            self.assertEqual(b'Robert', pd['name'][0], msg=pd)
            self.assertEqual(100, pd['id'][0], msg=pd)
            self.assertEqual('1980-01-01', str(pd['dob'][0]), msg=pd)
            self.assertEqual(b'Michelle', pd['name'][1], msg=pd)
            self.assertEqual(200, pd['id'][1], msg=pd)
            self.assertEqual('1991-12-31', str(pd['dob'][1]), msg=pd)

    def test_scan_as_json_max_records(self):
        sql = "select * from okera_sample.sample"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json(sql, max_records=1, max_client_process_count=1)
            self.assertTrue(len(json) == 1, msg='max_records not respected')
            json = planner.scan_as_json(sql, max_records=100, max_client_process_count=1)
            self.assertTrue(len(json) == 2, msg='max_records not respected')

    def test_scan_as_pandas_max_records(self):
        sql = "select * from okera_sample.sample"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            pd = planner.scan_as_pandas(sql, max_records=1, max_client_process_count=1)
            self.assertTrue(len(pd.index) == 1, msg='max_records not respected')
            pd = planner.scan_as_pandas(sql, max_records=100, max_client_process_count=1)
            self.assertTrue(len(pd.index) == 2, msg='max_records not respected')

    def test_scan_retry(self):
        global retry_count

        sql = "select * from okera_sample.sample"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            # First a sanity check
            pd = planner.scan_as_pandas(sql, max_records=1, max_client_process_count=1)
            self.assertTrue(len(pd.index) == 1, msg='test_scan_retry sanity check failed')

            # Patch scan_as_pandas to throw an IOError 2 times
            retry_count = 0
            def test_hook_retry(func_name, retries, attempt):
                if func_name != "plan":
                    return
                global retry_count
                retry_count = retry_count + 1
                if attempt < 2:
                    raise IOError('Fake Error')

            planner.test_hook_retry = test_hook_retry
            pd = planner.scan_as_pandas(sql, max_records=1, max_client_process_count=1)

            assert(retry_count == 3) # count = 2 failures + 1 success
            self.assertTrue(len(pd.index) == 1, msg='Failed to get data with retries')

    def test_worker_retry(self):
        global retry_count

        ctx = common.get_test_context()
        with common.get_worker(ctx) as worker:
            # First a sanity check
            v = worker.get_protocol_version()
            self.assertEqual('1.0', v)

            # Patch get_protocol_version to throw an IOError 2 times
            retry_count = 0
            def test_hook_retry(func_name, retries, attempt):
                if func_name != "get_protocol_version":
                    return
                global retry_count
                retry_count = retry_count + 1
                if attempt < 2:
                    raise IOError('Fake Error')

            worker.test_hook_retry = test_hook_retry
            v = worker.get_protocol_version()

            assert(retry_count == 3) # count = 2 failures + 1 success
            self.assertEqual('1.0', v)

    def test_overwrite_file(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            planner.execute_ddl("DROP TABLE IF EXISTS rs.dim")
            planner.execute_ddl("""CREATE EXTERNAL TABLE rs.dim
                (country_id INT, country_name STRING, country_code STRING)
                ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
                LOCATION 's3://cerebro-datasets/starschema_demo/country_dim/'
                TBLPROPERTIES ('skip.header.line.count'='1')""")

            # Copy one version of the file into the target location
            cerebro.run_shell_cmd('aws s3 cp ' +\
                's3://cerebro-datasets/country_dim_src/country_DIM.csv ' +\
                's3://cerebro-datasets/starschema_demo/country_dim/country_DIM.csv')
            before = planner.scan_as_json('rs.dim')[0]
            self.assertEqual("France", before['country_name'], msg=str(before))

            # Copy another version. This file has the same length but a different
            # character. S3 maintains time in ms timestamp, so sleep a bit.
            time.sleep(1)

            cerebro.run_shell_cmd('aws s3 cp ' +\
                's3://cerebro-datasets/country_dim_src/country_DIM2.csv ' +\
                's3://cerebro-datasets/starschema_demo/country_dim/country_DIM.csv')
            i = 0
            while i < 10:
                after = planner.scan_as_json('rs.dim')[0]
                if 'france' in after['country_name']:
                    return
                self.assertEqual("France", after['country_name'], msg=str(after))
                time.sleep(.1)
                i = i + 1
            self.fail(msg="Did not updated result in time.")

    def test_scan_as_json_newline_delimiters(self):
        sql1 = '''select
         *
        from
        okera_sample.sample'''
        sql2 = '''select
        *
        from
        okera_sample.sample'''
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json(sql1, max_records=100, max_client_process_count=1)
            self.assertTrue(
                len(json) == 2,
                msg='could parse query with newline and space delimiters')
            json = planner.scan_as_json(sql2, max_records=100, max_client_process_count=1)
            self.assertTrue(
                len(json) == 2,
                msg='could parse query with newline delimiters')

    def test_scan_as_json_using_with_clause(self):
        sql1 = '''WITH male_customers AS
         (SELECT * FROM okera_sample.users WHERE gender = 'M')
         SELECT * FROM male_customers;'''
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json = planner.scan_as_json(sql1, max_records=100, max_client_process_count=1)
            self.assertTrue(
                len(json) == 100,
                msg='could parse query that starts with "with"')

    def test_scan_as_json_serialization(self):
        sql = "select * from rs.alltypes"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            json.loads(json.dumps(planner.scan_as_json(sql)))

    def test_das_6218(self):
        DB = "das_6218"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, DB)
            self._create_all_types(conn, DB)

            # Verify schema from catalog, plan and data are all timestamp
            schema = conn.plan('%s.alltypes' % DB).schema
            self.assertEqual(schema.cols[10].type.type_id, TTypeId.TIMESTAMP_NANOS)
            df = conn.scan_as_pandas('SELECT timestamp_col FROM %s.alltypes' % DB)
            self.assertEqual(str(df.dtypes[0]), 'datetime64[ns, UTC]')
            catalog_schema = conn.list_datasets(DB, name='alltypes')[0].schema
            self.assertEqual(
                catalog_schema.cols[10].type.type_id, TTypeId.TIMESTAMP_NANOS)
            print(df)

            # Create a view that is proper with the explicit cast.
            conn.execute_ddl('''
                CREATE VIEW %s.v1(ts STRING)
                AS
                SELECT cast(timestamp_col AS STRING) FROM %s.alltypes''' % (DB, DB))
            # Verify schema from catalog, plan and data are all strings
            catalog_schema = conn.list_datasets(DB, name='v1')[0].schema
            self.assertEqual(catalog_schema.cols[0].type.type_id, TTypeId.STRING)
            schema = conn.plan('%s.v1' % DB).schema
            self.assertEqual(schema.cols[0].type.type_id, TTypeId.STRING)
            df = conn.scan_as_pandas('%s.v1' % DB)
            self.assertEqual(str(df.dtypes[0]), 'object')
            print(df)

            # We want to carefully construct a view that has mismatched types with
            # the view definition. The view just selects a timestamp columns but we
            # will force the catalog type to be string, instead of timestamp.
            # This forces the planner to produce an implicit cast.
            conn.execute_ddl('''
                CREATE EXTERNAL VIEW %s.v2(ts STRING)
                SKIP_ANALYSIS USING VIEW DATA AS
                "SELECT timestamp_col FROM %s.alltypes"''' % (DB, DB))
            # Verify schema from catalog, plan and data are all strings
            catalog_schema = conn.list_datasets(DB, name='v2')[0].schema
            self.assertEqual(catalog_schema.cols[0].type.type_id, TTypeId.STRING)
            schema = conn.plan('%s.v2' % DB).schema
            self.assertEqual(schema.cols[0].type.type_id, TTypeId.STRING)
            df = conn.scan_as_pandas('%s.v2' % DB)
            self.assertEqual(str(df.dtypes[0]), 'object')
            print(df)

    def test_zd_1633(self):
        DB = "zd_1633"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, DB)
            conn.execute_ddl('''
                CREATE EXTERNAL TABLE %s.t(
                  s STRING)
                STORED AS TEXTFILE
                LOCATION 's3://cerebrodata-test/zd-1627/'
                ''' % DB)
            res = conn.scan_as_json('%s.t' % DB)
            # Default quote, only 1 row
            self.assertEqual(1, len(res))

            # No quote, should be 2 rows now
            conn.execute_ddl("ALTER TABLE %s.t SET SERDEPROPERTIES('quoteChar'='')" % DB)
            res = conn.scan_as_json('%s.t' % DB)
            self.assertEqual(2, len(res))

            # Recreate using table properties
            conn.execute_ddl('DROP TABLE %s.t' % DB)
            conn.execute_ddl('''
                CREATE EXTERNAL TABLE %s.t(
                  s STRING)
                STORED AS TEXTFILE
                LOCATION 's3://cerebrodata-test/zd-1627/'
                TBLPROPERTIES('okera.text-table.default-quote-char'='')
                ''' % DB)
            res = conn.scan_as_json('%s.t' % DB)
            self.assertEqual(2, len(res))

            # Explicit serde properties overrides table properties
            conn.execute_ddl('''
                ALTER TABLE %s.t SET SERDEPROPERTIES('quoteChar'='"')''' % DB)
            res = conn.scan_as_json('%s.t' % DB)
            self.assertEqual(1, len(res))

            # Table with two cols
            conn.execute_ddl('DROP TABLE %s.t' % DB)
            conn.execute_ddl('''
                CREATE EXTERNAL TABLE %s.t(
                  c1 STRING, c2 STRING)
                STORED AS TEXTFILE
                LOCATION 's3://cerebrodata-test/customers/c1/zd1633_2/'
                TBLPROPERTIES('skip.header.line.count'='1')
                ''' % DB)
            conn.execute_ddl(
                "ALTER TABLE %s.t SET SERDEPROPERTIES('field.delim'=',')" % DB)
            res = conn.scan_as_json('%s.t' % DB)
            self.assertEqual(1, len(res))

            # Remove quote handling
            conn.execute_ddl("ALTER TABLE %s.t SET SERDEPROPERTIES('quoteChar'='')" % DB)
            res = conn.scan_as_json('%s.t' % DB)
            self.assertEqual(2, len(res))
            self.assertEqual('"123', res[1]['c2'])

    def test_scan_delta_dummy_metadata(self):
        DB = "delta_dummy_scan_db"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, DB)
            conn.execute_ddl('''
      CREATE EXTERNAL TABLE %s.airline_events_delta (
          col array<string>)
      WITH SERDEPROPERTIES (
          'path'='s3://cerebrodata-test/delta/airlines/airline_events/',
          'serialization.format'='1')
      STORED AS TEXTFILE
      LOCATION 's3://cerebrodata-test/delta/airlines/airline_events/'
      TBLPROPERTIES (
          'totalSize'='66153', 'numRows'='-1', 'rawDataSize'='-1',
          'okera.delta.infer-schema'='true',
          'COLUMN_STATS_ACCURATE'='false',
          'spark.sql.sources.schema.part.0'='{\"type\":\"struct\",\"fields\":[]}',
          'numFiles'='1', 'spark.sql.partitionProvider'='catalog',
          'spark.sql.sources.schema.numParts'='1', 'spark.sql.sources.provider'='delta',
          'spark.sql.create.version'='3.0.1')
                ''' % DB)
            res = conn.scan_as_json('%s.airline_events_delta' % DB)
            self.assertEqual(1326, len(res))

    def test_pandas_index(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            # We scan a small table but with a tiny min task size, so that it is
            # guaranteed to generate more than one task. We then verify that our
            # overall row indices are correct.
            df = planner.scan_as_pandas("okera_sample.sample", min_task_size=1)

            indices = []
            for i, row in df.iterrows():
                indices.append(i)

            assert len(indices) == 2
            assert indices[0] == 0
            assert indices[1] == 1

if __name__ == "__main__":
    unittest.main()
