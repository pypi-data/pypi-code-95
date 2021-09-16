# Copyright 2017 Okera Inc. All Rights Reserved.
#
# Tests that should run on any configuration. The server auth can be specified
# as an environment variables before running this test.

# pylint: disable=no-member
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=bad-continuation
# pylint: disable=bad-indentation
# pylint: disable=len-as-condition
# pylint: disable=no-self-use
# pylint: disable=line-too-long
# pylint: disable=too-many-locals
# pylint: disable=pointless-string-statement
import unittest

from decimal import Decimal
import numpy
import os
from tzlocal import get_localzone
import pytest

from okera import version, _thrift_api
from okera.tests import pycerebro_test_common as common
from okera._thrift_api import TAccessPermissionLevel, TRecordServiceException

# The timestamp values are TZ specific, switch based on this.
# TODO: this is an awful way to do this.
TIME_ZONE = get_localzone().zone

DEFAULT_PRESTO_PORT = os.environ['ODAS_TEST_PORT_PRESTO_COORD_HTTPS']

class BasicTest(common.TestBase):
    @staticmethod
    def __table_exists(name, tbls):
        found_table = False
        for tbl in tbls:
            if tbl.name == name:
                found_table = True

        return found_table

    def test_version(self):
        self.assertTrue(version())

    def test_connection(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        self.assertEqual("1.0", planner.get_protocol_version())
        planner.close()
        worker = common.get_worker(ctx)
        self.assertEqual("1.0", worker.get_protocol_version())
        worker.close()

    def test_random_host(self):
        ctx = common.get_test_context()
        host, port = ctx._OkeraContext__pick_host('abc', 123)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 123)

        host, port = ctx._OkeraContext__pick_host(['abc:234'], 123)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 234)

        host, port = ctx._OkeraContext__pick_host('abc:234', 123)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 234)

        for _ in range(0, 10):
            host, port = ctx._OkeraContext__pick_host(['abc', 'def'], 123)
            self.assertTrue(host in ['abc', 'def'])
            self.assertEqual(port, 123)

        # Test some invalid args
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host(None, None)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host("abc:123:45", 123)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host([1], 123)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host(1, 123)
        with self.assertRaises(ValueError):
            ctx._OkeraContext__pick_host('123', None)

    def test_pick_host(self):
        opt = {'PIN_HOST':1}
        opt2 = {'PIN_HOST':'def'}
        opt3 = {'PIN_HOST':'678'}

        ctx = common.get_test_context()
        host, port = ctx._OkeraContext__pick_host('abc', 123, opt)
        self.assertEqual(host, 'abc')
        self.assertEqual(port, 123)

        # Should always pick the first one
        for _ in range(0, 10):
            host, port = ctx._OkeraContext__pick_host(['ghi', 'abc', 'def'], 123, opt)
            self.assertEqual(host, 'abc')
            self.assertEqual(port, 123)

            host, port = ctx._OkeraContext__pick_host(['abc', 'def'], 123, opt2)
            self.assertEqual(host, 'def')
            self.assertEqual(port, 123)

        network_hosts = [
            _thrift_api.TNetworkAddress("678", 3),
            _thrift_api.TNetworkAddress("456", 4)]
        for _ in range(0, 10):
            host, port = ctx._OkeraContext__pick_host(network_hosts, None, opt)
            self.assertEqual(host, '456')
            self.assertEqual(port, 4)

            host, port = ctx._OkeraContext__pick_host(network_hosts, None, opt3)
            self.assertEqual(host, '678')

    def test_basic(self):
        ctx = common.get_test_context()
        # Can either be None or a token depending on the dev setup
        self.assertTrue(ctx.get_auth() is None or ctx.get_auth() == 'TOKEN')
        if ctx.get_auth() == 'TOKEN':
            self.assertTrue(ctx.get_token() is not None)

        ctx.disable_auth()
        self.assertTrue(ctx.get_auth() is None)

        ctx.enable_token_auth('ab.cd')
        self.assertEqual('TOKEN', ctx.get_auth())
        self.assertEqual('ab.cd', ctx.get_token())

        ctx.enable_token_auth('user')
        self.assertTrue(ctx.get_auth() is None)
        self.assertEqual('user', ctx._get_user())

    def test_planner(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        self.assertEqual('1.0', planner.get_protocol_version())
        planner.close()

        # Should be able to make more
        with common.get_planner(ctx) as planner:
            self.assertEqual('1.0', planner.get_protocol_version())

    def test_worker(self):
        ctx = common.get_test_context()
        worker = common.get_worker(ctx)
        self.assertEqual('1.0', worker.get_protocol_version())
        worker.close()

        # Should be able to make more
        with common.get_worker(ctx) as worker:
            self.assertEqual('1.0', worker.get_protocol_version())

    def test_catalog(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        dbs = planner.list_databases()
        self.assertTrue('okera_sample' in dbs)
        datasets = planner.list_datasets('okera_sample')
        self.assertTrue(datasets is not None)
        dataset_names = planner.list_dataset_names('okera_sample')
        self.assertTrue('okera_sample.sample' in dataset_names, msg=dataset_names)
        self.assertTrue('okera_sample.users' in dataset_names, msg=dataset_names)
        planner.close()

    def test_ddl(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        result = planner.execute_ddl("show databases")
        planner.close()
        print(result)
        self.assertTrue(len(result) > 3)

    def test_plan(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        plan = planner.plan("tpch.nation")
        self.assertEqual(1, len(plan.tasks))
        planner.close()

    def test_task_split(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        #large file no compression creates splits
        plan = planner.plan("rs.alltypes_large_s3")
        self.assertTrue(len(plan.tasks) > 1)

        #large file with compression creates no splits
        plan = planner.plan("rs.alltypes_large_s3_gz")
        self.assertEqual(1, len(plan.tasks))

        #large file with compression, without ext creates no splits
        plan = planner.plan("rs.alltypes_large_s3_gz_no_ext")
        self.assertEqual(1, len(plan.tasks))

        #large file with lzo compression creates splits
        plan = planner.plan("rs.alltypes_large_s3_lzo")
        self.assertTrue(len(plan.tasks) > 1)
        planner.close()

    def test_all_types_json(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        json = planner.scan_as_json("rs.alltypes")
        planner.close()
        self.assertEqual(2, len(json))
        r1 = json[0]
        r2 = json[1]
        self.assertEqual(12, len(r1))
        self.assertEqual(12, len(r2))
        self.assertEqual(True, r1['bool_col'])
        self.assertEqual(6, r2['tinyint_col'])
        self.assertEqual(1, r1['smallint_col'])
        self.assertEqual(8, r2['int_col'])
        self.assertEqual(3, r1['bigint_col'])
        self.assertEqual(10.0, r2['float_col'])
        self.assertEqual(5.0, r1['double_col'])
        self.assertEqual('world', r2['string_col'])
        self.assertEqual('vchar1', r1['varchar_col'])
        self.assertEqual('char2', r2['char_col'])
        self.assertEqual('3.1415920000', str(r1['decimal_col']))
        self.assertEqual('2016-01-01 00:00:00.000', str(r2['timestamp_col']))

    def test_requesting_user(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        json = planner.scan_as_json("rs.alltypes", requesting_user="testuser")
        planner.close()
        self.assertEqual(2, len(json))
        r1 = json[0]
        r2 = json[1]
        self.assertEqual({'int_col' : 2, 'string_col' : 'hello'}, r1)
        self.assertEqual({'int_col' : 8, 'string_col' : 'world'}, r2)

        planner = common.get_planner(ctx)
        pd = planner.scan_as_pandas("rs.alltypes", requesting_user="testuser")
        planner.close()
        self.assertEqual(2, len(pd))
        self.assertEqual(['int_col', 'string_col'], list(pd.columns))

        planner = common.get_planner(ctx)
        ddl = planner.execute_ddl(
            'describe okera_sample.users', requesting_user="testuser")
        self.assertEqual([
            [
                'ccn',
                'string',
                'Sensitive data, should not be accessible without masking.',
                ''],
            ['dob', 'string', 'Formatted as DD-month-YY', ''],
            ['gender', 'string', '', ''],
            ['uid', 'string', 'Unique user id', ''],
        ], sorted(ddl, key=lambda item: item[0]))

        planner = common.get_planner(ctx)
        with self.assertRaises(_thrift_api.TRecordServiceException):
            planner.execute_ddl(
                'describe okera_system.attributes', requesting_user="testuser")

    def test_all_types_pandas(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        pd = planner.scan_as_pandas("rs.alltypes")
        planner.close()
        self.assertEqual(2, len(pd))
        self.assertEqual(12, len(pd.columns))
        self.assertEqual(True, pd['bool_col'][0])
        self.assertEqual(False, pd['bool_col'][1])
        self.assertEqual(0, pd['tinyint_col'][0])
        self.assertEqual(6, pd['tinyint_col'][1])
        self.assertEqual(1, pd['smallint_col'][0])
        self.assertEqual(7, pd['smallint_col'][1])
        self.assertEqual(2, pd['int_col'][0])
        self.assertEqual(8, pd['int_col'][1])
        self.assertEqual(3, pd['bigint_col'][0])
        self.assertEqual(9, pd['bigint_col'][1])
        self.assertEqual(4.0, pd['float_col'][0])
        self.assertEqual(10.0, pd['float_col'][1])
        self.assertEqual(5.0, pd['double_col'][0])
        self.assertEqual(11.0, pd['double_col'][1])
        self.assertEqual(b'hello', pd['string_col'][0])
        self.assertEqual(b'world', pd['string_col'][1])
        self.assertEqual(b'vchar1', pd['varchar_col'][0])
        self.assertEqual(b'vchar2', pd['varchar_col'][1])
        self.assertEqual(b'char1', pd['char_col'][0])
        self.assertEqual(b'char2', pd['char_col'][1])
        self.assertEqual('3.1415920000', str(pd['decimal_col'][0]))
        self.assertEqual('1234.5678900000', str(pd['decimal_col'][1]))

        self.assertEqual('2015-01-01 00:00:00+00:00', str(pd['timestamp_col'][0]))
        self.assertEqual('2016-01-01 00:00:00+00:00', str(pd['timestamp_col'][1]))

    def test_all_types_null_pandas(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        pd = planner.scan_as_pandas("rs.alltypes_null")
        planner.close()
        self.assertEqual(1, len(pd))
        self.assertEqual(12, len(pd.columns))
        for i in range(0, len(pd.columns)):
            self.assertTrue(numpy.isnan(pd.iloc[0, i]), msg=pd)

    def test_all_types_empty(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        pd = planner.scan_as_pandas("rs.alltypes_empty")
        planner.close()
        self.assertEqual(
            ['bool_col', 'tinyint_col', 'smallint_col', 'int_col', 'bigint_col',
             'float_col', 'double_col', 'string_col', 'varchar_col', 'char_col',
             'timestamp_col', 'decimal_col'],
            list(pd.columns), msg=pd)
        self.assertEqual(0, len(pd), msg=pd)
        self.assertEqual(12, len(pd.columns), msg=pd)

    def test_all_types_null_json(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        json = planner.scan_as_json("rs.alltypes_null")
        planner.close()
        self.assertEqual(1, len(json), msg=json)
        self.assertEqual(12, len(json[0]), msg=json[0])
        for v in json[0]:
            self.assertTrue(json[0][v] is None, msg=json[0])

    def test_all_types_empty_json(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        json = planner.scan_as_json("rs.alltypes_empty")
        planner.close()
        self.assertEqual(0, len(json), msg=json)

    def test_filter_with_empty_rows_pandas(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        pd = planner.scan_as_pandas(
            "SELECT * FROM okera_sample.users where gender = 'lol'"
        )
        planner.close()
        self.assertEqual(0, len(pd), msg=pd)

    def test_column_order_scan_as_pandas(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        self.assertEqual(
            list(planner.scan_as_pandas("okera_sample.users").columns),
            ['uid', 'dob', 'gender', 'ccn'])
        self.assertEqual(
            list(planner.scan_as_pandas("select dob, uid from okera_sample.users")
                 .columns),
            ['dob', 'uid'])
        self.assertEqual(
            list(planner.scan_as_pandas("rs.alltypes_s3").columns),
            ['bool_col', 'tinyint_col', 'smallint_col', 'int_col', 'bigint_col',
             'float_col', 'double_col', 'string_col', 'varchar_col', 'char_col',
             'timestamp_col', 'decimal_col'])
        self.assertEqual(
            list(planner.scan_as_pandas(
                "select decimal_col, bigint_col from rs.alltypes_s3").columns),
            ['decimal_col', 'bigint_col'])

    def test_binary_data(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            planner.execute_ddl("create database if not exists binarydb")
            planner.execute_ddl("""
                create external table if not exists binarydb.sample (record binary)
                ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' STORED AS TEXTFILE
                LOCATION 's3://cerebrodata-test/fs_test_do_not_add_files_here/sample'""")

            df = planner.scan_as_pandas("binarydb.sample")
            self.assertEqual(2, len(df), msg=df)
            self.assertEqual(2, df['record'].count(), msg=df)
            self.assertEqual(b'This is a sample test file.', df['record'][0], msg=df)

            planner.execute_ddl("drop table binarydb.sample")
            planner.execute_ddl("drop database binarydb")

    def test_warnings(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            warnings = []
            result = planner.scan_as_json("okera_sample.sample", warnings=warnings)
            self.assertEqual(2, len(result))
            self.assertEqual(0, len(warnings))

            result = planner.scan_as_json("rs.alltypes_empty", warnings=warnings)
            self.assertEqual(0, len(result))
            self.assertEqual(1, len(warnings))
            self.assertTrue("has no data files" in warnings[0])

    def test_impersonation(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth('testuser')
        with common.get_planner(ctx) as planner:
            # Spot check a few
            dbs = []
            for r in planner.execute_ddl('show databases'):
                dbs.append(r[0])

            self.assertTrue('okera_sample' in dbs, msg=dbs)
            self.assertTrue('rs' in dbs, msg=dbs)
            self.assertFalse('customer' in dbs, msg=dbs)

            dbs2 = planner.list_databases()
            #execute_ddl does not ignore internal dbs
            #list_databases ignores internal dbs
            dbs = [d for d in dbs if not d.startswith("_")]
            self.assertEqual(dbs, dbs2)

            tbl_names = planner.list_dataset_names('rs')
            self.assertTrue('rs.alltypes' in tbl_names, msg=tbl_names)
            self.assertTrue('rs.alltypes_s3' in tbl_names, msg=tbl_names)
            self.assertFalse('rs.s3_nation' in tbl_names, msg=tbl_names)

            tbls = planner.list_datasets('rs')
            self.assertEqual(len(tbl_names), len(tbls))

            result = planner.scan_as_json('okera_sample.whoami')[0]
            self.assertEqual(result['user'], 'testuser')

    def test_get_objects_at_path(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            planner.execute_ddl("drop database if exists getobjectsdb cascade")
            planner.execute_ddl("create database if not exists getobjectsdb")
            planner.execute_ddl("""
                create external table if not exists getobjectsdb.t1(s string)
                location 's3://cerebrodata-test/prefixtests/root/alltypes/'""")
            planner.execute_ddl("""
                create external table if not exists getobjectsdb.t2(s string)
                location 's3://cerebrodata-test/prefixtests/root/alltypes-suffix/'""")
            planner.execute_ddl("""
                create external table if not exists getobjectsdb.t3(s string)
                location 's3://cerebrodata-test/prefixtests/root-suffix/alltypes/'""")

            result = planner.get_catalog_objects_at(
                "s3://cerebrodata-test/prefixtests/root")
            self.assertEqual(2, len(result), msg=result)

            result = planner.get_catalog_objects_at(
                "s3://cerebrodata-test/prefixtests/root/alltypes/")
            self.assertEqual(1, len(result), msg=result)

    def verify_decimal_value_json(self,
                                  planner,
                                  dec_in,
                                  prec,
                                  scale,
                                  expected=None,
                                  decimal_type=Decimal):
      if not expected:
        expected = decimal_type(dec_in)
      else:
        expected = decimal_type(expected)
      sql = 'select CAST({} as DECIMAL({},{})) as mycol'.format(dec_in, prec, scale)
      res = planner.scan_as_json(sql, decimal_type=decimal_type)[0]['mycol']
      self.assertEqual(res, expected)

    def verify_decimal_value_pandas(self,
                                  planner,
                                  dec_in,
                                  prec,
                                  scale,
                                  expected=None):
      if not expected:
        expected = Decimal(dec_in)
      sql = 'select CAST({} as DECIMAL({},{})) as mycol'.format(dec_in, prec, scale)
      res = planner.scan_as_pandas(sql).values[0][0]
      self.assertEqual(res, expected)

    def test_decimal_serialization_json(self):
      ctx = common.get_test_context()
      with common.get_planner(ctx) as p:
        self.verify_decimal_value_json(p, '100.12', 38, 2)
        self.verify_decimal_value_json(p, '-200.34', 38, 2)
        self.verify_decimal_value_json(p, '-300.56', 38, 2)
        self.verify_decimal_value_json(p, '-500.90', 38, 2)
        self.verify_decimal_value_json(p, '20000000.1234', 38, 4)
        self.verify_decimal_value_json(p, '-123456778989.5678', 38, 4)
        self.verify_decimal_value_json(p, '-234455566666.9012', 38, 4)
        self.verify_decimal_value_json(p, '89888833364747.3456', 38, 4)
        self.verify_decimal_value_json(p, '-8723333445555.7890', 38, 4)
        self.verify_decimal_value_json(p, '18446744073709551616.0000', 38, 4)
        self.verify_decimal_value_json(p, '-18446744073709551616.0000', 38, 4)
        self.verify_decimal_value_json(p, '-18446744073709551616.0000', 38, 0)
        self.verify_decimal_value_json(p, '17014118346046923173168730371588410579', 38,
                                       0, Decimal('1.701411834604692317316873037E+37'))
        self.verify_decimal_value_json(p, '-17014118346046923173168730371588410579', 38,
                                       0, Decimal('-1.701411834604692317316873037E+37'))
        self.verify_decimal_value_json(p, '100.12', 38, 2, decimal_type=str)
        self.verify_decimal_value_json(p, '-200.34', 38, 2, decimal_type=str)
        self.verify_decimal_value_json(p, '-300.56', 38, 2, decimal_type=str)
        self.verify_decimal_value_json(p, '-500.90', 38, 2, decimal_type=str)
        self.verify_decimal_value_json(p, '20000000.1234', 38, 4, decimal_type=str)
        self.verify_decimal_value_json(p, '-123456778989.5678', 38, 4, decimal_type=str)
        self.verify_decimal_value_json(p, '-234455566666.9012', 38, 4, decimal_type=str)
        self.verify_decimal_value_json(p, '89888833364747.3456', 38, 4, decimal_type=str)
        self.verify_decimal_value_json(p, '-8723333445555.7890', 38, 4, decimal_type=str)
        self.verify_decimal_value_json(p, '18446744073709551616.0000', 38, 4, decimal_type=str)
        self.verify_decimal_value_json(p, '-18446744073709551616.0000', 38, 4, decimal_type=str)
        self.verify_decimal_value_json(p, '-18446744073709551616', 38, 0, decimal_type=str)
        self.verify_decimal_value_json(p, '17014118346046923173168730371588410579', 38,
                                       0, Decimal('1.701411834604692317316873037E+37'), decimal_type=str)
        self.verify_decimal_value_json(p, '-17014118346046923173168730371588410579', 38,
                                       0, Decimal('-1.701411834604692317316873037E+37'), decimal_type=str)

    def test_decimal_serialization_pandas(self):
      ctx = common.get_test_context()
      with common.get_planner(ctx) as p:
        self.verify_decimal_value_pandas(p, '100.12', 38, 2)
        self.verify_decimal_value_pandas(p, '-200.34', 38, 2)
        self.verify_decimal_value_pandas(p, '-300.56', 38, 2)
        self.verify_decimal_value_pandas(p, '-500.90', 38, 2)
        self.verify_decimal_value_pandas(p, '20000000.1234', 38, 4)
        self.verify_decimal_value_pandas(p, '-123456778989.5678', 38, 4)
        self.verify_decimal_value_pandas(p, '-234455566666.9012', 38, 4)
        self.verify_decimal_value_pandas(p, '89888833364747.3456', 38, 4)
        self.verify_decimal_value_pandas(p, '-8723333445555.7890', 38, 4)
        self.verify_decimal_value_pandas(p, '18446744073709551616.0000', 38, 4)
        self.verify_decimal_value_pandas(p, '-18446744073709551616.0000', 38, 4)
        self.verify_decimal_value_pandas(p, '17014118346046923173168730371588410579', 38,
                                       0, Decimal('1.701411834604692317316873037E+37'))
        self.verify_decimal_value_pandas(p, '-17014118346046923173168730371588410579', 38,
                                       0, Decimal('-1.701411834604692317316873037E+37'))

    def test_create_from_show_create_table(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            ## Test by modifying output of show create, by replacing table name,
            ## create the new table, and delete the same after verification

            ## Test1: parquet table.
            test_table = "bytes_type_show_created"
            res = planner.execute_ddl("SHOW CREATE TABLE rs_complex_parquet.bytes_type")
            self.assertEqual(len(res), 1)

            ## extract the output, which is a create table statement. Modify
            create_ddl = res[0][0]
            create_ddl = create_ddl.replace("bytes_type", test_table)
            self.assertTrue(test_table in create_ddl)
            planner.execute_ddl("DROP TABLE IF EXISTS rs_complex_parquet." + test_table)
            planner.execute_ddl(create_ddl)

            ## Verify the table has been created
            res = planner.execute_ddl("SHOW TABLES IN rs_complex_parquet")
            tlist = []
            tlist.append(test_table)
            self.assertTrue(tlist in res)

            ## verify the new table is query-able
            sql = 'SELECT * FROM rs_complex_parquet.' + test_table
            query_result = planner.scan_as_json(sql)
            self.assertTrue(len(query_result) > 0)

            ## drop the newly created test table
            drop_table_ddl = "DROP TABLE rs_complex_parquet." + test_table
            planner.execute_ddl(drop_table_ddl)


            ## Test2: customer avro table
            res = planner.execute_ddl("SHOW CREATE TABLE customer.acxiom_cnsmr_xref")
            test_table = "acxiom_cnsmr_xref_show_created"

            ## extract the output, which is a create table statement. Modify
            create_ddl = res[0][0]
            create_ddl = create_ddl.replace("customer.acxiom_cnsmr_xref",
                                                      "customer." + test_table)
            planner.execute_ddl("DROP TABLE IF EXISTS customer." + test_table)
            planner.execute_ddl(create_ddl)

            ## Verify the table has been created
            res = planner.execute_ddl("SHOW TABLES IN customer")
            tlist.clear()
            tlist.append(test_table)
            self.assertTrue(tlist in res)

            ## verify the new table is query-able
            sql = 'SELECT * FROM customer.' + test_table
            query_result = planner.scan_as_json(sql)
            self.assertEqual(len(query_result), 0)

            ## drop the newly created test table
            drop_table_ddl = "DROP TABLE customer." + test_table
            planner.execute_ddl(drop_table_ddl)

    def test_get_datasets_databases_with_privilege(self):
        ATTR = ['priv_filter_test', 'attr1']
        DB1 = 'test_access_db1'
        DB2 = 'test_access_db2'
        DB3 = 'test_access_db3'
        DB4 = 'test_access_db4'
        DB5 = 'test_access_db5'
        DB6 = 'test_access_db6'
        DB7 = 'test_access_db7'
        TBL1 = 'tbl1'
        TBL2 = 'tbl2'
        ROLE = 'test_access_level_role'
        USER = 'test_access_level_user'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for db in [DB1, DB2, DB3, DB4]:
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db)
                conn.execute_ddl('CREATE DATABASE %s' % db)
                for tbl in [TBL1, TBL2]:
                    conn.execute_ddl('CREATE TABLE %s.%s (col1 int, col2 int)' % (
                        db, tbl))
            for db in [DB5, DB6, DB7]:
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db)
                conn.execute_ddl('CREATE DATABASE %s' % db)

            conn.execute_ddl('CREATE ATTRIBUTE IF NOT EXISTS %s.%s' % (ATTR[0], ATTR[1]))
            conn.execute_ddl('DROP ROLE IF EXISTS %s' % ROLE)
            conn.execute_ddl('CREATE ROLE %s' % ROLE)
            conn.execute_ddl('GRANT VIEW_AUDIT ON TABLE %s.%s TO ROLE %s' % (
                DB1, TBL1, ROLE))
            conn.execute_ddl('GRANT VIEW_AUDIT ON DATABASE %s TO ROLE %s' % (DB2, ROLE))
            conn.execute_ddl('''GRANT SELECT ON TABLE %s.%s
                                HAVING ATTRIBUTE %s.%s
                                TO ROLE %s''' % (DB3, TBL1, ATTR[0], ATTR[1], ROLE))
            conn.execute_ddl('GRANT CREATE ON DATABASE %s TO ROLE %s' % (DB5, ROLE))
            conn.execute_ddl('GRANT CREATE_AS_OWNER ON DATABASE %s TO ROLE %s' % (DB6, ROLE))
            conn.execute_ddl('GRANT ALL ON DATABASE %s TO ROLE %s' % (DB7, ROLE))
            conn.execute_ddl('ALTER TABLE %s.%s ADD ATTRIBUTE %s.%s' % (
                DB3, TBL1, ATTR[0], ATTR[1]))
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (ROLE, USER))

            ctx.enable_token_auth(token_str=USER)

            # This will list all datasets with any access
            tables = conn.list_datasets(db=DB1)
            assert len(tables) == 1
            assert BasicTest.__table_exists(TBL1, tables)
            tables = conn.list_datasets(db=DB2)
            assert len(tables) == 2
            assert BasicTest.__table_exists(TBL1, tables)
            assert BasicTest.__table_exists(TBL2, tables)
            tables = conn.list_datasets(db=DB3)
            assert len(tables) == 1
            tables = conn.list_datasets(db=DB4)
            assert len(tables) == 0

            # This will list all datasets with SELECT access
            tables = conn.list_datasets(db=DB1, privilege=TAccessPermissionLevel.SELECT)
            assert len(tables) == 0
            tables = conn.list_datasets(db=DB2, privilege=TAccessPermissionLevel.SELECT)
            assert len(tables) == 0
            tables = conn.list_datasets(db=DB3, privilege=TAccessPermissionLevel.SELECT)
            assert len(tables) == 1
            tables = conn.list_datasets(db=DB4, privilege=TAccessPermissionLevel.SELECT)
            assert len(tables) == 0

            # This will list all datasets with VIEW_AUDIT access
            tables = conn.list_datasets(
                db=DB1, privilege=TAccessPermissionLevel.VIEW_AUDIT)
            assert len(tables) == 1
            assert BasicTest.__table_exists(TBL1, tables)
            tables = conn.list_datasets(
                db=DB2, privilege=TAccessPermissionLevel.VIEW_AUDIT)
            assert len(tables) == 2
            assert BasicTest.__table_exists(TBL1, tables)
            assert BasicTest.__table_exists(TBL2, tables)
            tables = conn.list_datasets(
                db=DB3, privilege=TAccessPermissionLevel.VIEW_AUDIT)
            assert len(tables) == 0
            tables = conn.list_datasets(
                db=DB4, privilege=TAccessPermissionLevel.VIEW_AUDIT)
            assert len(tables) == 0

            # This will list all databases with any privilege
            dbs = conn.list_databases()
            assert DB1 in dbs
            assert DB2 in dbs
            assert DB3 in dbs
            assert DB4 not in dbs
            assert DB7 in dbs

            # This will list all databases with view audit privilege
            dbs = conn.list_databases(privilege=TAccessPermissionLevel.VIEW_AUDIT)
            assert DB1 in dbs
            assert DB2 in dbs
            assert DB3 not in dbs
            assert DB4 not in dbs
            assert DB7 in dbs

            # This will list all databases with SELECT (for which all but one of
            # our DBs won't be in)
            dbs = conn.list_databases(privilege=TAccessPermissionLevel.SELECT)
            assert DB1 not in dbs
            assert DB2 not in dbs
            assert DB3 in dbs
            assert DB4 not in dbs
            assert DB7 in dbs

            # This will list all databases with SELECT and VIEW_AUDIT
            dbs = conn.list_databases(
                privilege=[TAccessPermissionLevel.SELECT, TAccessPermissionLevel.VIEW_AUDIT])
            assert DB1 in dbs
            assert DB2 in dbs
            assert DB3 in dbs
            assert DB4 not in dbs
            assert DB5 not in dbs
            assert DB7 in dbs

            # This will list all databases with CREATE
            dbs = conn.list_databases(privilege=TAccessPermissionLevel.CREATE)
            assert DB5 in dbs
            assert DB6 not in dbs
            assert DB7 in dbs

            # This will list all databases with CREATE_AS_OWNER
            dbs = conn.list_databases(privilege=TAccessPermissionLevel.CREATE_AS_OWNER)
            assert DB5 not in dbs
            assert DB6 in dbs
            assert DB7 in dbs

            # This will list all databases with ALL
            dbs = conn.list_databases(privilege=TAccessPermissionLevel.ALL)
            assert DB5 not in dbs
            assert DB6 not in dbs
            assert DB7 in dbs

            # This will list all databases with CREATE and CREATE_AS_OWNER
            dbs = conn.list_databases(
                privilege=[TAccessPermissionLevel.ALL, TAccessPermissionLevel.CREATE, TAccessPermissionLevel.CREATE_AS_OWNER])
            assert DB5 in dbs
            assert DB6 in dbs
            assert DB7 in dbs

    def test_quarantine_dbs(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            conn.execute_ddl("drop crawler if exists okera_quarantine")
            conn.execute_ddl("drop database if exists okera_quarantine")
            conn.execute_ddl("create database okera_quarantine")
            conn.execute_ddl("create crawler okera_quarantine source 's3://cerebrodata-test/empty/'")
            result = conn.list_databases()
            assert "okera_quarantine" not in result
            assert "_okera_crawler_okera_quarantine" not in result
            result_presto = conn.scan_as_pandas("show schemas", dialect='presto')
            assert "okera_quarantine" not in result_presto
            assert "_okera_crawler_okera_quarantine" not in result_presto

    def test_get_datasets_with_low_privs(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:

            def sensitive_data_check(dataset, is_view, should_exist):
                if not is_view:
                    if should_exist:
                        assert dataset.input_format
                        assert dataset.output_format
                    else:
                        assert not dataset.input_format
                        assert not dataset.output_format
                else:
                    if should_exist:
                        assert dataset.view_expanded_text
                    else:
                        assert not dataset.view_expanded_text

            def get_datasets(conn):

                datasets = conn.list_datasets(db='okera_system')
                dataset_map = {}
                for dataset in datasets:
                    dataset_map[dataset.name] = dataset

                return dataset_map

            datasets = get_datasets(conn)
            assert 'audit_logs' in datasets
            assert 'steward_audit_logs' in datasets
            sensitive_data_check(
                datasets['audit_logs'], is_view=False, should_exist=True)
            sensitive_data_check(
                datasets['steward_audit_logs'], is_view=True, should_exist=True)


            USER = 'datasets_priv_user'
            ROLE = 'datasets_priv_role'
            conn.execute_ddl('DROP ROLE IF EXISTS %s' % ROLE)
            conn.execute_ddl('CREATE ROLE %s' % ROLE)
            conn.execute_ddl('GRANT SELECT ON DATABASE okera_system TO ROLE %s' % ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (ROLE, USER))

            ctx.enable_token_auth(token_str=USER)
            datasets = get_datasets(conn)
            assert 'audit_logs' in datasets
            assert 'steward_audit_logs' in datasets
            sensitive_data_check(
                datasets['audit_logs'], is_view=False, should_exist=False)
            sensitive_data_check(
                datasets['steward_audit_logs'], is_view=True, should_exist=False)

    def test_no_sandbox(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            dbs = conn.list_databases()
            assert 'okera_sandbox' not in dbs

    def test_create_unparseable_view(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as planner:
            test_db = "invalid_view_db"
            ## Create a view with unparseable query.
            test_view = "unparseable_view"

            planner.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % test_db)
            planner.execute_ddl("CREATE DATABASE %s " % test_db)

            # Verify that we cannot CREATE internal view with unparseable statement.
            try:
                planner.execute_ddl(
                    "CREATE VIEW %s.%s as select 1 as `#foo`" % (test_db, test_view))
                pytest.fail("Expected to fail parsing unparseable view %s.%s"
                    % (test_db, test_view))
            except TRecordServiceException as ex:
                print(ex)
                self.assertTrue("AnalysisException" in ex.detail)
                self.assertTrue("TableLoadingException" in ex.detail)
                self.assertTrue(
                    "Failed to parse view-definition statement of view: %s.%s due to"
                    % (test_db, test_view) in ex.detail)
                self.assertTrue("#foo" in ex.detail)

            # Verify that we cannot ALTER internal view with unparseable statement.
            planner.execute_ddl(
                "CREATE VIEW %s.%s as select 1 as `foo`" % (test_db, test_view))
            try:
                planner.execute_ddl(
                    "ALTER VIEW %s.%s as select 1 as `#foo`" % (test_db, test_view))
                pytest.fail("Expected to fail parsing unparseable view %s.%s"
                    % (test_db, test_view))
            except TRecordServiceException as ex:
                print(ex)
                self.assertTrue("AnalysisException" in ex.detail)
                self.assertTrue("TableLoadingException" in ex.detail)
                self.assertTrue(
                    "Failed to parse view-definition statement of view: %s.%s due to"
                    % (test_db, test_view) in ex.detail)
                self.assertTrue("#foo" in ex.detail)

            # Verify that we DO NOT ALLOW CREATE external view with unparseable statement.
            try:
              planner.execute_ddl("DROP VIEW %s.%s " % (test_db, test_view))
              planner.execute_ddl(
                  "CREATE EXTERNAL VIEW %s.%s as select 1 as `#foo`"
                  % (test_db, test_view))
              pytest.fail("Expected to fail parsing unparseable view %s.%s"
                    % (test_db, test_view))
            except TRecordServiceException as ex:
                print(ex)
                self.assertTrue("AnalysisException" in ex.detail)
                self.assertTrue("TableLoadingException" in ex.detail)
                self.assertTrue(
                    "Failed to parse view-definition statement of view: %s.%s due to"
                    % (test_db, test_view) in ex.detail)
                self.assertTrue("#foo" in ex.detail)

            # Verify that we ALLOW CREATE external view with unparseable statement and
            # skip_analysis keyword.
            planner.execute_ddl(
                "CREATE EXTERNAL VIEW %s.%s (id int) skip_analysis " \
                "as select 1 as `#foo`" % (test_db, test_view))

            # External view with unparseable query should load for describe statements.
            res = planner.execute_ddl("DESCRIBE %s.%s " % (test_db, test_view))
            self.assertEqual(len(res), 1)
            res = planner.execute_ddl("DESCRIBE FORMATTED %s.%s " % (test_db, test_view))
            self.assertTrue(test_db in res)
            self.assertTrue("VIRTUAL_VIEW" in res)
            self.assertTrue("#foo" in res)

            planner.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % test_db)

    def test_add_partition(self):
        db = 'test_db_file_partition'
        add = "ALTER TABLE %s.tbl ADD PARTITION '%s'"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, db)
            create = '''
            CREATE EXTERNAL TABLE %s.tbl(c1 STRING, c2 STRING)
            PARTITIONED BY (year int, month int)
            ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
            STORED AS TEXTFILE
            LOCATION 's3://cerebrodata-test/partition-ymdata'
            TBLPROPERTIES('okera.auto_partition_recovery.disable'='true')
            '''
            conn.execute_ddl(create % db)
            res = conn.scan_as_json('%s.tbl' % db)
            self.assertTrue(len(res) == 0)

            conn.execute_ddl(
                add % (db, 's3://cerebrodata-test/partition-ymdata/year=2016/month=1'))
            conn.execute_ddl(
                add % (db, 's3://cerebrodata-test/partition-ymdata/year=2017/month=3/'))
            res = conn.scan_as_json('%s.tbl' % db)
            res = sorted(res, key = lambda i: i['c1'])
            self.assertTrue(len(res) == 2)
            self.assertEqual(1, res[0]['month'])
            self.assertEqual(2016, res[0]['year'])
            self.assertEqual('2016-1', res[0]['c1'])
            self.assertEqual(3, res[1]['month'])
            self.assertEqual(2017, res[1]['year'])
            self.assertEqual('2017-3', res[1]['c1'])

            # This is currently a no-op, as per all ALTER TABLE ADD PARTITION calls
            conn.execute_ddl(
                add % (db, 's3://cerebrodata-test/partition-ymdata/year=2016/month=1'))

    def test_path_resolution(self):
        # This test creates some path resolution aliases by creating conflicts with
        # the default database.
        # Tables:
        #  - name.tbl
        #  - default.name
        NAME = 'test_path_resolution'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP TABLE IF EXISTS default.%s' % NAME)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % NAME)
            conn.execute_ddl('CREATE DATABASE %s' % NAME)
            conn.execute_ddl("""
                CREATE TABLE %s.tbl(s string)""" % NAME)
            res = conn.scan_as_json('select * from %s.tbl' % NAME)
            self.assertEqual(0, len(res))

            # Create the alias conflict and try again
            conn.execute_ddl("""
                CREATE EXTERNAL TABLE default.%s(s string)
                LOCATION 'dbfs:/foo/bar' """ % NAME)

            res = conn.scan_as_json('select * from %s.tbl' % NAME)
            self.assertEqual(0, len(res))

    def test_complex_type_keywords(self):
        DB = "complex_types_keywords_test"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, DB)
            conn.execute_ddl("""
              create table %s.tbl (
                  attributes array<struct<`Attribute`:struct<Value:bigint,_id:string, policyproperties:string, comment:string>>>
              ) stored as parquet
            """ % DB)
            conn.execute_ddl("describe %s.tbl" % DB)

    def test_legacy_hud(self):
        DB = "legacy_hudi_test_db"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, DB)
            conn.execute_ddl(
        """
        CREATE EXTERNAL TABLE %s.hudi_nonpartitioned
        LIKE PARQUET 's3://cerebrodata-test/hudi_parquet/year=2015/month=03/day=16/5f541af5-ca07-4329-ad8c-40fa9b353f35-0_2-103-391_20200210090618.parquet'
        ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
        STORED AS INPUTFORMAT
          'com.uber.hoodie.hadoop.HoodieInputFormat'
        OUTPUTFORMAT
          'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
        LOCATION 's3://cerebrodata-test/hudi_parquet/year=2015/month=03/day=16/';
        """ % DB)
            desc = conn.execute_ddl("DESCRIBE FORMATTED %s.hudi_nonpartitioned" % DB)
            self.assertTrue('com.uber.hoodie.hadoop.HoodieInputFormat' in desc)
            data = conn.scan_as_json('%s.hudi_nonpartitioned' % DB)
            self.assertEqual(38, len(data))

    def test_dataset_path_rename(self):
        # Keep DB name the same for the `test_dataset_path_XXX` tests
        DB = "test_dataset_path_db"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % (DB),
                "CREATE DATABASE %s" % (DB),
                """CREATE EXTERNAL TABLE %s.tbl1 (
                    N_NATIONKEY SMALLINT,
                    N_NAME STRING,
                    N_REGIONKEY SMALLINT,
                    N_COMMENT STRING)
                    STORED AS PARQUET
                    LOCATION 's3://cerebrodata-test/dataset-rename-test'""" % (DB),
                "CREATE VIEW %s.view1 AS SELECT * FROM %s.tbl1" % (DB, DB),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = conn.get_catalog_objects_at(
                "s3://cerebrodata-test/dataset-rename-test", include_views=True)
            assert 's3://cerebrodata-test/dataset-rename-test' in res
            objs = res['s3://cerebrodata-test/dataset-rename-test']
            assert len(objs) == 2
            assert ("%s.tbl1" % DB) in objs
            assert ("%s.view1" % DB) in objs

            conn.execute_ddl('ALTER TABLE %s.tbl1 RENAME TO %s.tbl2' % (DB, DB))
            conn.execute_ddl('ALTER VIEW %s.view1 RENAME TO %s.view2' % (DB, DB))

            res = conn.get_catalog_objects_at(
                "s3://cerebrodata-test/dataset-rename-test", include_views=True)
            assert 's3://cerebrodata-test/dataset-rename-test' in res
            objs = res['s3://cerebrodata-test/dataset-rename-test']
            assert len(objs) == 2
            assert ("%s.tbl2" % DB) in objs
            assert ("%s.view2" % DB) in objs

    def test_dataset_path_mixed_case(self):
        # Keep DB name the same for the `test_dataset_path_XXX` tests
        DB = "test_dataset_path_db"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % (DB),
                "CREATE DATABASE %s" % (DB),
                """CREATE EXTERNAL TABLE %s.TBL1 (
                    N_NATIONKEY SMALLINT,
                    N_NAME STRING,
                    N_REGIONKEY SMALLINT,
                    N_COMMENT STRING)
                    STORED AS PARQUET
                    LOCATION 's3://cerebrodata-test/dataset-rename-test'""" % (DB),
                """CREATE EXTERNAL TABLE %s.TBL2 (
                    N_NATIONKEY SMALLINT,
                    N_NAME STRING,
                    N_REGIONKEY SMALLINT,
                    N_COMMENT STRING)
                    STORED AS PARQUET
                    LOCATION 's3://cerebrodata-test/dataset-rename-test'""" % (DB),
                "CREATE VIEW %s.VIEW1 AS SELECT * FROM %s.TBL1" % (DB, DB),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = conn.get_catalog_objects_at(
                "s3://cerebrodata-test/dataset-rename-test", include_views=True)
            assert 's3://cerebrodata-test/dataset-rename-test' in res
            objs = res['s3://cerebrodata-test/dataset-rename-test']
            assert len(objs) == 3
            assert ("%s.tbl1" % DB) in objs
            assert ("%s.tbl2" % DB) in objs
            assert ("%s.view1" % DB) in objs

            conn.execute_ddl('DROP TABLE %s.TbL1' % (DB))
            conn.execute_ddl('DROP VIEW %s.ViEw1' % (DB))
            conn.execute_ddl('DROP DATABASE %s CASCADE' % (DB))

            res = conn.get_catalog_objects_at(
                "s3://cerebrodata-test/dataset-rename-test", include_views=True)
            assert 's3://cerebrodata-test/dataset-rename-test' not in res


if __name__ == "__main__":
    unittest.main()
