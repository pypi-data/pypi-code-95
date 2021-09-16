# Copyright 2019 Okera Inc. All Rights Reserved.

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
#
# Tests for AuthorizeQuery() API
#
#+-----------------+--------------------+-----------------+---------+---------+---------+---------+---------+-------+
#|       rpc       |        name        |       user      |   mean  |   50%   |   90%   |   99%   |   max   | iters |
#+-----------------+--------------------+-----------------+---------+---------+---------+---------+---------+-------+
#| authorize_query |     get_filter     | nea_test_reader |  15.998 |  11.226 |  11.932 | 240.200 | 240.200 |   50  |
#| authorize_query | yotpo-sparse-tags  |      admin      | 111.243 | 109.553 | 115.560 | 146.309 | 146.309 |   50  |
#| authorize_query | yotpo-sparse-tags  |    TEST_USER    | 458.562 | 450.046 | 465.896 | 683.336 | 683.336 |   50  |
#| authorize_query | yotpo-medium-tags  |      admin      | 176.255 | 167.397 | 195.490 | 435.166 | 435.166 |   50  |
#| authorize_query | yotpo-medium-tags  |    TEST_USER    | 475.739 | 474.005 | 497.712 | 668.227 | 668.227 |   50  |
#| authorize_query | yotpo-sparse-tags2 |      admin      | 117.287 | 108.686 | 112.647 | 310.840 | 310.840 |   50  |
#| authorize_query | yotpo-sparse-tags2 |    TEST_USER    | 487.660 | 479.014 | 502.400 | 724.325 | 724.325 |   50  |
#| authorize_query | yotpo-medium-tags2 |      admin      | 186.848 | 178.087 | 210.168 | 436.644 | 436.644 |   50  |
#| authorize_query | yotpo-medium-tags2 |    TEST_USER    | 526.246 | 523.901 | 541.433 | 751.603 | 751.603 |   50  |
#+-----------------+--------------------+-----------------+---------+---------+---------+---------+---------+-------+


import json
import os
import pytest
import unittest

from okera._thrift_api import TAccessPermissionLevel
from okera._thrift_api import TAuthorizeQueryParams
from okera._thrift_api import TAuthorizeQueryClient
from okera._thrift_api import TErrorCode
from okera._thrift_api import TRecordServiceException
from okera._thrift_api import TRequestContext

from okera.tests import pycerebro_test_common as common

TEST_USER = 'testuser'
SKIP_LEVELS = ["smoke", "dev", "all", "checkin"]

PERF = common.PerfResults()

class AuthorizeQueryTest(common.TestBase):
    @staticmethod
    def normalize(sql):
      return ' '.join(sql.split())

    @classmethod
    def tearDownClass(cls):
        PERF.finalize_results()

    def authorize_query_audit_only(self, conn, query, user=None, db=None, dataset=None):
        request = TAuthorizeQueryParams()
        request.sql = query
        request.requesting_user = user
        request.use_session_local_tables = False
        request.audit_only = True
        if db:
            request.db = [db]
        if dataset:
            request.dataset = dataset
        result = conn.service.client.AuthorizeQuery(request)
        self.assertTrue(result is not None)
        self.assertTrue(result.table is None)
        return result

    # Returns * if the user can directly access the table, the rewritten query if
    # that's required or None if the user must go to ODAS.
    def authorize_table(self, conn, db, table, user=None, use_tmp_tables=False):
        request = TAuthorizeQueryParams()
        request.db = [db]
        request.dataset = table
        request.requesting_user = user
        request.use_session_local_tables = use_tmp_tables
        result = conn.service.client.AuthorizeQuery(request)
        self.assertTrue(result.result_sql is not None or result.table is not None)
        if result.full_access:
            # Full access should return full table metadata
            self.assertTrue(result.table is not None)
            return '*'
        if result.requires_worker:
            return None
        self.assertTrue(result.result_schema is not None)
        return ' '.join(result.result_sql.split())

    @staticmethod
    def cache_key(conn, query, user=None):
        request = TAuthorizeQueryParams()
        request.sql = query
        request.requesting_user = user
        request.client = TAuthorizeQueryClient.OKERA_CACHE_KEY
        result = conn.service.client.AuthorizeQuery(request)
        if result.result_sql is None:
            return None
        return ' '.join(result.result_sql.split())

    @staticmethod
    def cte_rewrite(conn, query, user=None,
                    generate_plan=False, client=None, default_db=None):
        request = TAuthorizeQueryParams()
        request.sql = query
        request.requesting_user = user
        request.cte_rewrite = True
        request.plan_request = generate_plan
        request.client = client
        request.default_db = default_db;
        result = conn.service.client.AuthorizeQuery(request)
        if result.result_sql is None:
            return None, None
        result_sql = ' '.join(result.result_sql.split())
        return result_sql, result.plan, result.referenced_tables

    @staticmethod
    def get_filter(conn, db, tbl, user, level=None, records=None, return_records=False):
        request = TAuthorizeQueryParams()
        request.db = [db]
        request.dataset = tbl
        request.requesting_user = user
        request.privilege_level = level
        request.records = records
        request.client = TAuthorizeQueryClient.REST_API
        request.return_records = return_records
        return conn.service.client.AuthorizeQuery(request)

    def test_sql(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.assertEqual("SELECT 1", self.authorize_query(conn, "select 1"))
            self.assertEqual(
                "SELECT 1", self.authorize_query(conn, "select 1", None, True))
            self.assertEqual(
                "SELECT 1", self.authorize_query(conn, "select 1",
                                                 client=TAuthorizeQueryClient.IMPALA,
                                                 cte=True))

            self.assertEqual(
                "SELECT 'okera' as user",
                self.authorize_query(conn, "select * from okera_sample.whoami"))
            self.assertEqual(
                "SELECT 'okera' as user",
                self.authorize_query(
                    conn, "select * from okera_sample.whoami", None, True))
            self.assertEqual(
                "SELECT 'okera' as `user`",
                self.authorize_query(
                    conn, "select * from okera_sample.whoami",
                    client=TAuthorizeQueryClient.IMPALA, cte=True))

            self.assertEqual(
                "SELECT 'okera' as user",
                self.authorize_query(conn, "select user from okera_sample.whoami"))
            self.assertEqual(
                "SELECT 'okera' as user",
                self.authorize_query(
                    conn, "select user from okera_sample.whoami", None, True))
            self.assertEqual(
                "SELECT 'okera' as `user`",
                self.authorize_query(
                    conn, "select user from okera_sample.whoami",
                    client=TAuthorizeQueryClient.IMPALA, cte=True))

            # Rewrite does not make sense for this table as it is an okera specific
            # construct.
            self.assertEqual(
                None,
                self.authorize_query(conn, "select * from okera_sample.sample"))
            self.assertEqual(
                None,
                self.authorize_query(
                    conn, "select * from okera_sample.sample", None, True))
            # FIXME
            #self.assertEqual(
            #    None,
            #    self.authorize_query(
            #        conn, "select * from okera_sample.sample", None, True,
            #        client=TAuthorizeQueryClient.IMPALA, cte=True))

            self.assertEqual(
                "SELECT int_col FROM rs.alltypes_s3",
                self.authorize_query(conn, "select int_col from rs.alltypes_s3"))
            self.assertEqual(
                "SELECT int_col FROM rs.alltypes_s3_tmp",
                self.authorize_query(
                    conn, "select int_col from rs.alltypes_s3", None, True))
            self.assertEqual(
                "select int_col from `rs`.`alltypes_s3`",
                self.authorize_query(conn, "select int_col from rs.alltypes_s3",
                                     client=TAuthorizeQueryClient.IMPALA, cte=True))

            self.assertEqual(
                "SELECT bool_col, tinyint_col, smallint_col, int_col, bigint_col, " +\
                "float_col, double_col, string_col, varchar_col, char_col, " +\
                "timestamp_col, decimal_col FROM all_table_types.s3",
                self.authorize_query(conn, "select * from all_table_types.s3"))
            self.assertEqual(
                "SELECT bool_col, tinyint_col, smallint_col, int_col, bigint_col, " +\
                "float_col, double_col, string_col, varchar_col, char_col, " +\
                "timestamp_col, decimal_col FROM all_table_types.s3_tmp",
                self.authorize_query(conn, "select * from all_table_types.s3",
                                     None, True))
            self.assertEqual(
                "select * from `all_table_types`.`s3`",
                self.authorize_query(conn, "select * from all_table_types.s3",
                                     client=TAuthorizeQueryClient.IMPALA, cte=True))

            # Now run as testuser
            self.assertEqual(
                "SELECT 'testuser' as user",
                self.authorize_query(
                    conn, "select * from okera_sample.whoami", TEST_USER))
            self.assertEqual(
                "SELECT 'testuser' as user",
                self.authorize_query(
                    conn, "select * from okera_sample.whoami", TEST_USER, True))
            self.assertEqual(
                "SELECT 'testuser' as `user`",
                self.authorize_query(
                    conn, "select * from okera_sample.whoami", TEST_USER,
                    client=TAuthorizeQueryClient.IMPALA, cte=True))

            self.assertEqual(
                "SELECT int_col FROM rs.alltypes_s3",
                self.authorize_query(
                    conn, "select int_col from rs.alltypes_s3", TEST_USER))
            self.assertEqual(
                "SELECT int_col FROM rs.alltypes_s3_tmp",
                self.authorize_query(
                    conn, "select int_col from rs.alltypes_s3", TEST_USER, True))
            self.assertEqual(
                "WITH okera_rewrite_rs__alltypes_s3 AS (" + \
                "SELECT `int_col`, `float_col`, `string_col` " + \
                "FROM `rs`.`alltypes_s3`) " + \
                "select int_col from okera_rewrite_rs__alltypes_s3",
                self.authorize_query(
                    conn, "select int_col from rs.alltypes_s3", TEST_USER,
                    client=TAuthorizeQueryClient.IMPALA, cte=True))

            # * should expand to a subset of the columns
            self.assertEqual(
                "SELECT int_col, float_col, string_col FROM rs.alltypes_s3",
                self.authorize_query(conn, "select * from rs.alltypes_s3", TEST_USER))
            self.assertEqual(
                "SELECT int_col, float_col, string_col FROM rs.alltypes_s3_tmp",
                self.authorize_query(
                    conn, "select * from rs.alltypes_s3", TEST_USER, True))
            self.assertEqual(
                "WITH okera_rewrite_rs__alltypes_s3 AS " + \
                "(SELECT `int_col`, `float_col`, `string_col` " + \
                "FROM `rs`.`alltypes_s3`) select * from okera_rewrite_rs__alltypes_s3",
                self.authorize_query(conn, "select * from rs.alltypes_s3", TEST_USER,
                                     client=TAuthorizeQueryClient.IMPALA, cte=True))

            # Selecting a column wit no access should fail
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.authorize_query(
                    conn, "select bool_col from rs.alltypes_s3", TEST_USER)
            self.assertTrue('does not have privileges' in str(ex_ctx.exception))
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.authorize_query(
                    conn, "select bool_col from rs.alltypes_s3", TEST_USER, True)
            self.assertTrue('does not have privileges' in str(ex_ctx.exception))
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.authorize_query(
                    conn, "select bool_col from rs.alltypes_s3", TEST_USER,
                    client=TAuthorizeQueryClient.IMPALA, cte=True)
            self.assertTrue('does not have privileges' in str(ex_ctx.exception))

    def test_hql_all_transforms(self):
        """ Rewrites aginst the hive ecosystem: okera, hive, impala, spark"""
        db = 'test_hql_all_transforms'
        role = 'test_hsql_role'
        user = 'test_hsql_user'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, db)
            self._create_all_types(conn, db, True)
            self._tag_all_columns(conn, db, 'alltypes', db, 'tag', create_tag=True)

            expected_template = \
                "SELECT " +\
                "%s as `bool_col`, " + \
                "%s as `tinyint_col`, " + \
                "%s as `smallint_col`, " + \
                "%s as `int_col`, " +\
                "%s as `bigint_col`, " +\
                "%s as `float_col`, " + \
                "%s as `double_col`, " +\
                "%s as `string_col`, " + \
                "%s as `varchar_col`, " + \
                "%s as `char_col`, " + \
                "%s as `date_col`, " +\
                "%s as `timestamp_col`, " +\
                "%s as `decimal_col` FROM " + \
                "`test_hql_all_transforms`.`alltypes`"

            fns = {
              'mask': ['FALSE',
                       "CAST(0 AS TINYINT)",
                       "CAST(0 AS SMALLINT)",
                       "CAST(0 AS INT)",
                       "CAST(0 AS BIGINT)",
                       "CAST(0 AS FLOAT)",
                       "CAST(0 AS DOUBLE)",
                       "okera_udfs.`mask`(`string_col`)",
                       "CAST(okera_udfs.`mask`(`varchar_col`) AS VARCHAR(10))",
                       "CAST(okera_udfs.`mask`(`char_col`) AS CHAR(5))",
                       "CAST('1970-01-01 00:00:00' AS DATE)",
                       "CAST('1970-01-01 00:00:00' AS TIMESTAMP)",
                       "CAST(0 AS DECIMAL(24,10))"],
              'null': [
                       "CAST(NULL AS BOOLEAN)",
                       "CAST(NULL AS TINYINT)",
                       "CAST(NULL AS SMALLINT)",
                       "CAST(NULL AS INT)",
                       "CAST(NULL AS BIGINT)",
                       "CAST(NULL AS FLOAT)",
                       "CAST(NULL AS DOUBLE)",
                       "CAST(NULL AS STRING)",
                       "CAST(CAST(NULL AS STRING) AS VARCHAR(10))",
                       "CAST(CAST(NULL AS STRING) AS CHAR(5))",
                       "CAST(CAST(NULL AS TIMESTAMP) AS DATE)",
                       "CAST(CAST(NULL AS TIMESTAMP) AS TIMESTAMP)",
                       "CAST(NULL AS DECIMAL(24,10))"],
              'sha2': [
                       "CAST(okera_udfs.`sha2`(`bool_col`) AS BOOLEAN)",
                       "CAST(okera_udfs.`sha2`(`tinyint_col`) AS TINYINT)",
                       "CAST(okera_udfs.`sha2`(`smallint_col`) AS SMALLINT)",
                       "CAST(okera_udfs.`sha2`(`int_col`) AS INT)",
                       "okera_udfs.`sha2`(`bigint_col`)",
                       "CAST(okera_udfs.`sha2`(`float_col`) AS FLOAT)",
                       "CAST(okera_udfs.`sha2`(`double_col`) AS DOUBLE)",
                       "CAST(okera_udfs.`sha2`(`string_col`) AS STRING)",
                       "CAST(okera_udfs.`sha2`(`varchar_col`) AS VARCHAR(10))",
                       "CAST(okera_udfs.`sha2`(`char_col`) AS CHAR(5))",
                       "CAST('1970-01-01' AS DATE)",
                       "CAST('1970-01-01' AS TIMESTAMP)",
                       "CAST(okera_udfs.`sha2`(`decimal_col`) AS DECIMAL(24,10))"],
              'zero': ['FALSE',
                       "CAST(0 AS TINYINT)",
                       "CAST(0 AS SMALLINT)",
                       "CAST(0 AS INT)",
                       "CAST(0 AS BIGINT)",
                       "CAST(0 AS FLOAT)",
                       "CAST(0 AS DOUBLE)",
                       "''",
                       "CAST('' AS VARCHAR(10))", "CAST('' AS CHAR(5))",
                       "CAST('1970-01-01 00:00:00' AS DATE)",
                       "CAST('1970-01-01 00:00:00' AS TIMESTAMP)",
                       "CAST(0 AS DECIMAL(24,10))"],
            }

            for fn, t in fns.items():
                self._recreate_test_role(conn, role, [user])
                conn.execute_ddl('''
                    GRANT SELECT ON DATABASE %s TRANSFORM %s.%s WITH `%s`()
                    TO ROLE %s
                ''' % (db, db, 'tag', fn, role))

                expected = expected_template % \
                    (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], \
                    t[8], t[9], t[10], t[11], t[12])

                rewrite = self.authorize_query(
                    conn, "select * from %s.alltypes" % db, user,
                    client=TAuthorizeQueryClient.IMPALA, cte=False)
                print()
                print("Function: " + fn)
                print("--------REWRITE---------")
                print(rewrite)
                print("--------EXPECTED---------")
                print(expected)
                self.assertEqual(expected, rewrite)

    def test_implicit_string_cast(self):
        db = "implicit_string_test_db"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, db)
            self._recreate_test_role(conn, 'implicit_cast_role', ['implicit_cast_user'])
            conn.execute_ddl("CREATE ATTRIBUTE IF NOT EXISTS test.string_col")
            conn.execute_ddl("""CREATE TABLE %s.t(
                s1 STRING ATTRIBUTE test.string_col,
                s2 VARCHAR(10) ATTRIBUTE test.string_col,
                s3 CHAR(5) ATTRIBUTE test.string_col)""" % db)
            conn.execute_ddl(
                """GRANT SELECT ON DATABASE %s TRANSFORM test.string_col
                WITH sha2() TO ROLE %s""" % (db, 'implicit_cast_role'))
            self.assertEqual(
                "SELECT CAST(sha2(s1) AS STRING) as s1, " +
                "CAST(sha2(s2) AS VARCHAR(10)) as s2, " +
                "CAST(sha2(s3) AS CHAR(5)) as s3 FROM implicit_string_test_db.t",
                self.authorize_query(conn, "SELECT * FROM %s.t" % db,
                                     'implicit_cast_user', False,
                                     return_full_result=True))
            self.assertEqual(
                "SELECT s1, s2, s3 FROM implicit_string_test_db.t",
                self.authorize_query(conn, "SELECT * FROM %s.t" % db,
                                     'okera', False, return_full_result=True))

    def test_audit_only(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.authorize_query_audit_only(conn, 'select * from bar1')
            self.authorize_query_audit_only(conn, 'select * from bar2', user='user1')
            self.authorize_query_audit_only(
                conn, 'select * from bar3',
                user='user2', db='xyz', dataset='abc.def')
            self.authorize_query_audit_only(
                conn, 'select * from bar4', user='user3',
                db='xyz,abc', dataset='abc.def,foo.bar')

    def test_table(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.assertEqual(None, self.authorize_table(conn, "okera_sample", "sample"))
            self.assertEqual(
                None, self.authorize_table(conn, "okera_sample", "sample", None, True))

            self.assertEqual(
                None, self.authorize_table(conn, "okera_sample", "sample", TEST_USER))
            self.assertEqual(
                None,
                self.authorize_table(conn, "okera_sample", "sample", TEST_USER, True))

            self.assertEqual('*', self.authorize_table(conn, "rs", "alltypes_s3"))
            self.assertEqual(
                '*',
                self.authorize_table(conn, "rs", "alltypes_s3", None, True))
            self.assertEqual(
                "SELECT int_col, float_col, string_col FROM rs.alltypes_s3",
                self.authorize_table(conn, "rs", "alltypes_s3", TEST_USER))
            self.assertEqual(
                "SELECT int_col, float_col, string_col FROM rs.alltypes_s3_tmp",
                self.authorize_table(conn, "rs", "alltypes_s3", TEST_USER, True))

            # This is a view, we want to "flatten"
            self.assertEqual(
                "SELECT 'okera' as user",
                self.authorize_table(conn, "okera_sample", "whoami"))
            self.assertEqual(
                "SELECT 'okera' as user",
                self.authorize_table(conn, "okera_sample", "whoami", None, True))
            self.assertEqual(
                "SELECT 'testuser' as user",
                self.authorize_table(conn, "okera_sample", "whoami", TEST_USER))
            self.assertEqual(
                "SELECT 'testuser' as user",
                self.authorize_table(conn, "okera_sample", "whoami", TEST_USER, True))

            # Do some more interesting view
            self.assertEqual(
                "SELECT bool_col, tinyint_col, smallint_col, int_col, bigint_col, " +
                "float_col, double_col, string_col, varchar_col, char_col, " +
                "timestamp_col, decimal_col FROM abac_db.all_types",
                self.authorize_table(conn, "abac_db", "all_types_view", TEST_USER, True))

            self.assertEqual(
                "SELECT user, mask_ccn(ccn) FROM rs.ccn",
                self.authorize_table(conn, "rs", "ccn_masked", TEST_USER, True))
            self.assertEqual(
                "SELECT int_col, float_col, string_col FROM rs.alltypes_s3_tmp",
                self.authorize_table(conn, "rs", "alltypes_s3", TEST_USER, True))

            # No access
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.authorize_table(conn, "nytaxi", "parquet_data", TEST_USER)
            self.assertTrue('does not have permissions' in str(ex_ctx.exception))

            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.authorize_table(conn, "nytaxi", "parquet_data", TEST_USER, True)
            self.assertTrue('does not have permissions' in str(ex_ctx.exception))

    def test_view(self):
        ctx = common.get_test_context()
        db = 'authorize_view_db'
        role = "authorize_view_test_role"
        testuser = "authorize_view_testuser"

        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ROLE IF EXISTS " + role)
            conn.execute_ddl("CREATE ROLE " + role)
            conn.execute_ddl("GRANT ROLE " + role + " TO GROUP " + testuser)
            conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % db)
            conn.execute_ddl("CREATE DATABASE %s" % db)

            # Test complex type view
            self.assertEqual(
                "SELECT id, s1 FROM authdb.struct_t WHERE s1.f2 > 1",
                self.authorize_table(conn, 'authdb', 'struct_t_where_clause_view',
                                     None, True))

            # Join with no aliases
            conn.execute_ddl(("create view %s.v as " +
                              "select a.*,b.* from okera_sample.sample a " +
                              "join okera_sample.users b on a.record = b.ccn") % db)
            self.assertEqual(
                "SELECT a.record as record, b.uid as uid, b.dob as dob, " +
                "b.gender as gender, b.ccn as ccn FROM okera_sample.sample a " +
                "INNER JOIN okera_sample.users b ON a.record = b.ccn",
                self.authorize_table(conn, db, "v", None, True))

            # Join with alias on one side
            conn.execute_ddl("DROP VIEW %s.v" % db)
            conn.execute_ddl(("create view %s.v as " +
                              "select a.record as r, b.* from okera_sample.sample a " +
                              "join okera_sample.sample b on a.record = b.record") % db)
            self.assertEqual(
                "SELECT a.record as r, b.record as record " +
                "FROM okera_sample.sample a INNER JOIN okera_sample.sample b " +
                "ON a.record = b.record",
                self.authorize_table(conn, db, "v", None, True))

            # Join with alias on both sides
            conn.execute_ddl("DROP VIEW %s.v" % db)
            conn.execute_ddl(("create view %s.v as " +
                              "select a.record as r, b.record as r2 " +
                              "from okera_sample.sample a " +
                              "join okera_sample.sample b on a.record = b.record") % db)
            self.assertEqual(
                "SELECT a.record as r, b.record as r2 " +
                "FROM okera_sample.sample a INNER JOIN okera_sample.sample b " +
                "ON a.record = b.record",
                self.authorize_table(conn, db, "v", None, True))

            conn.execute_ddl("DROP VIEW %s.v" % db)
            conn.execute_ddl(("create view %s.v as " +
                              "select * from okera_sample.sample " +
                              "where record is not null") % db)
            self.assertEqual(
                "SELECT record FROM okera_sample.sample WHERE record IS NOT NULL",
                self.authorize_table(conn, db, "v", None, True))

            conn.execute_ddl("DROP VIEW %s.v" % db)
            conn.execute_ddl(("create view %s.v as " +
                              "select * from okera_sample.sample " +
                              "where record > 'A' and record < 'z'") % db)
            self.assertEqual(
                "SELECT record FROM okera_sample.sample WHERE (record > 'A') " +
                "AND (record < 'z')",
                self.authorize_table(conn, db, "v", None, True))

            conn.execute_ddl("DROP VIEW %s.v" % db)
            conn.execute_ddl(("create view %s.v as " +
                              "select record as r from okera_sample.sample " +
                              "where record > 'A' and record < 'z'") % db)
            self.assertEqual(
                "SELECT record as r FROM okera_sample.sample WHERE (record > 'A') " +
                "AND (record < 'z')",
                self.authorize_table(conn, db, "v", None, True))

            # View with join
            conn.execute_ddl("DROP VIEW %s.v" % db)
            conn.execute_ddl(("create view %s.v as " +
                              "select record as r from okera_sample.sample a " +
                              "join okera_sample.users b on a.record = b.ccn") % db)
            self.assertEqual(
                "SELECT record as r FROM okera_sample.sample a INNER JOIN " +
                "okera_sample.users b ON a.record = b.ccn",
                self.authorize_table(conn, db, "v", None, True))

            conn.execute_ddl("DROP VIEW %s.v" % db)
            conn.execute_ddl(("create view %s.v as " +
                              "select a.record from okera_sample.sample a " +
                              "join okera_sample.users b on a.record = b.ccn") % db)
            self.assertEqual(
                "SELECT a.record as record FROM okera_sample.sample a INNER JOIN " +
                "okera_sample.users b ON a.record = b.ccn",
                self.authorize_table(conn, db, "v", None, True))

            # Some existing views
            self.assertEqual(
                "SELECT uid, dob, gender, mask_ccn(ccn) FROM okera_sample.users",
                self.authorize_table(conn, "okera_sample", "users_ccn_masked",
                                     None, True))
            self.assertEqual(
                "SELECT name, phone, email, userid, lastlogin, creditcardnumber, " + \
                "loc, ipv4_address, ipv6_address FROM abac_db.user_account_data",
                self.authorize_table(conn, "abac_db", "user_account_data_view",
                                     None, True))

            self.assertEqual(
                "SELECT n_nationkey, n_name FROM tpch.nation WHERE n_nationkey < 5",
                self.authorize_table(conn, "rs", "nation_projection", None, True))

            # Try as testuer, should compose
            conn.execute_ddl(
                "GRANT SELECT ON TABLE rs.nation_projection WHERE %s TO ROLE %s" %\
                ("n_name > 'M'", role))
            self.assertEqual(
                "SELECT n_nationkey, n_name FROM tpch.nation WHERE (n_nationkey < 5) " +\
                "AND (n_name > 'M')",
                self.authorize_table(conn, "rs", "nation_projection", testuser, True))

            self.assertEqual(
                "SELECT t1.n_nationkey as n_nationkey, t1.n_name as n_name, " + \
                "t1.n_regionkey as n_regionkey, t1.n_comment as n_comment, " + \
                "t2.n_nationkey as n_nationkey2 FROM tpch.nation t1 " +\
                "INNER JOIN tpch.nation t2 ON t1.n_nationkey = t2.n_nationkey",
                self.authorize_table(conn, "tpch", "nation_join", None, True))

            # FIXME: broken, missing group by
            #self.assertEqual(
            #    "SELECT n_nationkey, count(*) as _c1 FROM tpch.nation",
            #    self.authorize_table(conn, "tpch", "nation_agg", None, True))

    def test_table_subquery(self):
        ctx = common.get_test_context()
        role = "subquery_test_role"
        testuser = "subquery_testuser"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ROLE IF EXISTS " + role)
            conn.execute_ddl("CREATE ROLE " + role)
            conn.execute_ddl("GRANT ROLE " + role + " TO GROUP " + testuser)

            def grant(filter):
                conn.execute_ddl(
                    "GRANT SELECT ON TABLE rs.alltypes_s3 WHERE %s TO ROLE %s" %\
                    (filter, role))
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                grant("int_col in (SELECT bigint_col FROM rs.alltypes_s3)")
                conn.scan_as_json("rs.alltypes_s3", requesting_user=testuser)
            self.assertTrue('Policy filter contains a subquery' in str(ex_ctx.exception))

    def test_tmp_views(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Get the full schema as okera
            full_schema = conn.list_datasets("rs", name="alltypes_s3")[0].schema
            self.assertEqual(12, len(self._visible_cols(full_schema.cols)))

            # Get the schemas a testuser, this should be a subset
            ctx.enable_token_auth(token_str=TEST_USER)
            partial_schema = conn.list_datasets("rs", name="alltypes_s3")[0].schema
            self.assertEqual(3, len(self._visible_cols(partial_schema.cols)))

            # Reading the tmp version should have. It doesn't exist yet.
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                conn.scan_as_json("rs.alltypes_s3_tmp")
            self.assertTrue('does not have privileges' in str(ex_ctx.exception))

            # Authorize this query, this will temporarily add the temp table and it
            # will have the full schema.
            self.authorize_table(conn, "rs", "alltypes_s3", TEST_USER, True)
            result = conn.list_datasets("rs", name="alltypes_s3_tmp")[0]

            # Note: this returns all the columns, which the user is not normally
            # able to see.
            self.assertEqual(12, len(self._visible_cols(result.schema.cols)))
            self.assertEqual(full_schema, result.schema)

            self.assertEqual("rs", result.db[0])
            self.assertEqual("alltypes_s3_tmp", result.name)

            self.assertEqual(
                '*',
                self.authorize_table(conn, "rs", "alltypes_s3_tmp", TEST_USER, True))

            # Do it again
            self.assertEqual(
                '*',
                self.authorize_table(conn, "rs", "alltypes_s3_tmp", TEST_USER, True))

        # Recreate the connection, the temp tables are gone
        with common.get_planner(ctx) as conn:
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.authorize_table(conn, "rs", "alltypes_s3_tmp", TEST_USER, True)
            self.assertTrue('Table does not exist' in str(ex_ctx.exception),
                            msg=str(ex_ctx.exception))

    def test_auth_token_header(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.assertEqual(
                    "SELECT 'okera' as `user`",
                    self.authorize_query(
                        conn, "select * from okera_sample.whoami", token='bad-token'))
            self.assertTrue('Invalid token' in str(ex_ctx.exception),
                            msg=str(ex_ctx.exception))

    def test_filter_clause(self):
        role = "filter_test_role"
        testuser = "filter_testuser"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ROLE IF EXISTS " + role)
            conn.execute_ddl("CREATE ROLE " + role)
            conn.execute_ddl("GRANT ROLE " + role + " TO GROUP " + testuser)

            def grant(filter):
                conn.execute_ddl(
                    "GRANT SELECT ON TABLE rs.alltypes WHERE %s TO ROLE %s" %\
                    (filter, role))

            def revoke(filter):
                conn.execute_ddl(
                    "REVOKE SELECT ON TABLE rs.alltypes WHERE %s FROM ROLE %s" %\
                    (filter, role))

            grant('int_col = 1')
            filter = self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertEqual('int_col = 1', filter.filter)
            self.assertEqual(['1'], filter.filtered_values['int_col'])

            # Two row filters, bad
            grant('int_col = 2')
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertTrue("Access to 'rs.alltypes' is protected by multiple filters" \
                in str(ex_ctx.exception))

            revoke('int_col = 1')
            revoke('int_col = 2')

            # Try some other filters
            grant('int_col = bool_col')
            filter = self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertEqual('int_col = bool_col', filter.filter)
            self.assertEqual(None, filter.filtered_values)
            revoke('int_col = bool_col')

            grant('int_col = 1 or int_col = 2')
            filter = self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertEqual('int_col IN (1, 2)', filter.filter)
            self.assertEqual(['1', '2'], filter.filtered_values['int_col'])
            revoke('int_col = 1 or int_col = 2')

            grant('int_col = 1 and int_col = 2')
            filter = self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertEqual('FALSE', filter.filter)
            self.assertEqual(None, filter.filtered_values)
            revoke('int_col = 1 and int_col = 2')

            grant('int_col in(1, 2, 3)')
            filter = self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertEqual('int_col IN (1, 2, 3)', filter.filter)
            self.assertEqual(['1', '2', '3'], filter.filtered_values['int_col'])
            revoke('int_col in(1, 2, 3)')

            grant('int_col in(1, 2, 3) or int_col = 4')
            filter = self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertEqual('int_col IN (1, 2, 3, 4)', filter.filter)
            self.assertEqual(['1', '2', '3', '4'], filter.filtered_values['int_col'])
            revoke('int_col in(1, 2, 3) or int_col = 4')

            grant('int_col in(1, 2, 3) or float_col = 4')
            filter = self.get_filter(conn, 'rs', 'alltypes', testuser)
            self.assertEqual('int_col IN (1, 2, 3) OR float_col = 4', filter.filter)
            self.assertEqual(None, filter.filtered_values)
            revoke('int_col in(1, 2, 3) or float_col = 4')

    def test_nea_poc(self):
        admin = "nea_test_admin"
        full_reader = "nea_test_full_reader"
        partial_reader = "nea_test_reader"
        insert_reader = "nea_test_insert_reader"
        inserter = "nea_test_inserter"
        updater = "nea_test_updater"

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Set up roles and groups
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % admin)
            conn.execute_ddl("CREATE ROLE %s_role" % admin)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % (admin, admin))
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % full_reader)
            conn.execute_ddl("CREATE ROLE %s_role" % full_reader)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % \
                (full_reader, full_reader))
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % partial_reader)
            conn.execute_ddl("CREATE ROLE %s_role" % partial_reader)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % \
                (partial_reader, partial_reader))
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % insert_reader)
            conn.execute_ddl("CREATE ROLE %s_role" % insert_reader)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % \
                (insert_reader, insert_reader))
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % inserter)
            conn.execute_ddl("CREATE ROLE %s_role" % inserter)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % (inserter, inserter))
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % updater)
            conn.execute_ddl("CREATE ROLE %s_role" % updater)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % (updater, updater))

            tbl = 'okera_system.audit_logs'
            conn.execute_ddl(
                "GRANT ALL ON TABLE %s TO ROLE %s_role" % (tbl, admin))
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s TO ROLE %s_role" % (tbl, full_reader))
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s WHERE v1 TO ROLE %s_role" % \
                (tbl, partial_reader))
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s WHERE v1 TO ROLE %s_role" % \
                (tbl, insert_reader))
            conn.execute_ddl(
                "GRANT INSERT ON TABLE %s WHERE v1 TO ROLE %s_role" % \
                (tbl, insert_reader))
            conn.execute_ddl(
                "GRANT INSERT ON TABLE %s WHERE v2 TO ROLE %s_role" % \
                (tbl, inserter))
            conn.execute_ddl(
                "GRANT UPDATE ON TABLE %s WHERE v3 TO ROLE %s_role" % \
                (tbl, updater))
            conn.execute_ddl(
                "GRANT DELETE ON TABLE %s WHERE v4 TO ROLE %s_role" % \
                (tbl, updater))

            def get(user, level):
                r = self.get_filter(conn, 'okera_system', 'audit_logs', user, level)
                return r.filter

            def fail(user, level):
                with self.assertRaises(TRecordServiceException) as ex_ctx:
                    get(user, level)
                    self.fail()
                self.assertTrue("does not have permissions" in str(ex_ctx.exception))

            #
            # SELECT
            #
            self.assertEqual(None, get(admin, TAccessPermissionLevel.SELECT))
            self.assertEqual(None, get(full_reader, TAccessPermissionLevel.SELECT))
            self.assertEqual("v1", get(partial_reader, TAccessPermissionLevel.SELECT))
            self.assertEqual("v1", get(insert_reader, TAccessPermissionLevel.SELECT))
            fail(inserter, TAccessPermissionLevel.SELECT)
            fail(updater, TAccessPermissionLevel.SELECT)

            #
            # INSERT
            #
            self.assertEqual(None, get(admin, TAccessPermissionLevel.INSERT))
            fail(full_reader, TAccessPermissionLevel.INSERT)
            fail(partial_reader, TAccessPermissionLevel.INSERT)
            self.assertEqual("v1", get(insert_reader, TAccessPermissionLevel.INSERT))
            self.assertEqual("v2", get(inserter, TAccessPermissionLevel.INSERT))
            fail(updater, TAccessPermissionLevel.INSERT)

            #
            # UPDATE
            #
            self.assertEqual(None, get(admin, TAccessPermissionLevel.UPDATE))
            fail(full_reader, TAccessPermissionLevel.UPDATE)
            fail(partial_reader, TAccessPermissionLevel.UPDATE)
            fail(insert_reader, TAccessPermissionLevel.UPDATE)
            fail(inserter, TAccessPermissionLevel.UPDATE)
            self.assertEqual("v3", get(updater, TAccessPermissionLevel.UPDATE))

            #
            # DELETE
            #
            self.assertEqual(None, get(admin, TAccessPermissionLevel.DELETE))
            fail(full_reader, TAccessPermissionLevel.DELETE)
            fail(partial_reader, TAccessPermissionLevel.DELETE)
            fail(insert_reader, TAccessPermissionLevel.DELETE)
            fail(inserter, TAccessPermissionLevel.DELETE)
            self.assertEqual("v4", get(updater, TAccessPermissionLevel.DELETE))

    @pytest.mark.perf
    def test_measure_get_filter_nea(self):
        """
        Measure time to return a filter.
        """
        partial_reader = "nea_test_reader"
        tbl = 'okera_system.audit_logs'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % partial_reader)
            conn.execute_ddl("CREATE ROLE %s_role" % partial_reader)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % \
                (partial_reader, partial_reader))
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s WHERE v1 TO ROLE %s_role" % \
                (tbl, partial_reader))

            def get():
                self.get_filter(conn, 'okera_system', 'audit_logs', 'nea_test_reader',
                                TAccessPermissionLevel.SELECT)
            PERF.measure(get, 'get_filter', 'nea_test_reader', 'authorize_query')

    @pytest.mark.perf
    def test_records_filter(self):
        all_user = "filter_test_user1"
        user1 = "filter_test_user2"

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Set up roles and groups
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % all_user)
            conn.execute_ddl("CREATE ROLE %s_role" % all_user)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % (all_user, all_user))
            conn.execute_ddl("DROP ROLE IF EXISTS %s_role" % user1)
            conn.execute_ddl("CREATE ROLE %s_role" % user1)
            conn.execute_ddl("GRANT ROLE %s_role TO GROUP %s" % (user1, user1))

            def grant(filter, user):
                conn.execute_ddl(
                    "GRANT INSERT ON TABLE okera_system.audit_logs %s TO ROLE %s_role" % \
                    (filter, user))
                conn.execute_ddl(
                    "GRANT SELECT ON TABLE okera_system.audit_logs %s TO ROLE %s_role" % \
                    (filter, user))

            def filter(user, records, return_records=False):
                serialized = []
                for record in records:
                    serialized.append(json.dumps(record))
                r = self.get_filter(conn, 'okera_system', 'audit_logs', user,
                                    TAccessPermissionLevel.INSERT, serialized,
                                    return_records)
                if return_records:
                    result = []
                    for r in r.result_records:
                      result.append(json.loads(r))
                    return result
                else:
                    return r.filtered_records

            # Set up grants
            grant("", all_user)
            grant("WHERE user='1'", user1)

            # Check records
            self.assertEqual([True], filter(all_user, [{'user':'1'}]))
            self.assertEqual([{'user':'1'}], filter(all_user, [{'user':'1'}], True))

            self.assertEqual([True, True], filter(all_user,
                                                  [{'user':'1'},
                                                   {'user':'2'}]))
            self.assertEqual([{'user':'1'}, {'user':'2'}],
                             filter(all_user, [{'user':'1'}, {'user':'2'}], True))

            self.assertEqual([True], filter(user1, [{'user':'1'}]))
            self.assertEqual([{'user':'1'}], filter(user1, [{'user':'1'}], True))

            self.assertEqual([False], filter(user1, [{'abc':'1'}]))
            self.assertEqual([], filter(user1, [{'abc':'1'}], True))

            self.assertEqual([True], filter(user1, [{'abc':'1', 'user':'1'}]))
            self.assertEqual([{'abc':'1', 'user':'1'}],
                             filter(user1, [{'abc':'1', 'user':'1'}], True))

            self.assertEqual([True, False], filter(user1,
                                                   [{'user':'1'},
                                                    {'user':'2'}]))
            self.assertEqual([{'user':'1'}], filter(user1,
                                                   [{'user':'1'},
                                                    {'user':'2'}], True))

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            def get():
                records = [{'user':'1'}, {'user':'2'}]
                serialized = []
                for record in records:
                    serialized.append(json.dumps(record))
                self.get_filter(conn, 'okera_system', 'audit_logs', 'filter_test_user2',
                                TAccessPermissionLevel.INSERT, serialized)
            PERF.measure(get, 'get_filter', 'filter_test_user2', 'authorize_query')

    def test_require_worker(self):
        # Test tables are atypical and always require the worker to evaluate
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for user in [None, TEST_USER]:
                self.assertEqual(
                    None, self.authorize_table(conn, "all_table_types", "local_fs", user))
                self.assertEqual(
                    '*',
                    self.authorize_table(
                        conn, "all_table_types", "external_view_only", user))
                self.assertEqual(
                    '*',
                    self.authorize_table(
                        conn, "all_table_types", "dbfs_invalid_table", user))
                if user is None:
                    self.assertEqual(
                        None,
                        self.authorize_table(
                            conn, "okera_system", "audit_logs", user))

                self.assertEqual(
                    None,
                    self.authorize_table(
                        conn, "all_table_types", "single_file_table", user))
                self.assertEqual(
                    None,
                    self.authorize_table(
                        conn, "all_table_types", "http_table", user))

    def test_authorize_table_filter(self):
        role = "filter_test_role"
        testuser = "filter_testuser"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ROLE IF EXISTS " + role)
            conn.execute_ddl("CREATE ROLE " + role)
            conn.execute_ddl("GRANT ROLE " + role + " TO GROUP " + testuser)
            conn.execute_ddl('GRANT SELECT ON TABLE %s WHERE %s TO ROLE %s' %\
                             ('abac_db.all_types', 'find_in_set(string_col, "1,2") > 0',
                              role))
            self.assertTrue(
                self.authorize_table(conn, "abac_db", "all_types", testuser) is not None)

    def test_impala_rewrite(self):
        ctx = common.get_test_context()
        cases = [
            ("SELECT 1",
             "SELECT 1",
             "SELECT 1"),
            ("select count(*), count(int_col) from rs.alltypes_s3",
             "SELECT `count`(*), `count`(`int_col`) FROM `rs`.`alltypes_s3`",
             "select count(*), count(int_col) from `rs`.`alltypes_s3`"),
            ("SELECT count(int_col) as `a.c1` FROM rs.alltypes_s3",
             "SELECT `count`(`int_col`) as `a.c1` FROM `rs`.`alltypes_s3`",
             "SELECT count(int_col) as `a.c1` FROM `rs`.`alltypes_s3`"),
            ("SELECT * FROM okera_sample.users_ccn_masked",
             "SELECT `uid`, `dob`, `gender`, okera_udfs.`mask_ccn`(`ccn`) " +
             "FROM `okera_sample`.`users`",
             "SELECT * FROM `okera_sample`.`users_ccn_masked`")
        ]

        with common.get_planner(ctx) as conn:
            for sql, rewritten, cte_rewritten in cases:
                self.assertEqual(
                    rewritten,
                    self.authorize_query(conn, sql, client=TAuthorizeQueryClient.IMPALA,
                                         cte=False))

                self.assertEqual(
                    cte_rewritten,
                    self.authorize_query(conn, sql, client=TAuthorizeQueryClient.IMPALA,
                                         cte=True))

    def test_cannot_cache(self):
        cases = [
            'SELECT 1',
            'SELECT user()',
            'SELECT rand()',
            'SELECT rand() + 1',
            'SELECT * FROM okera_sample.sample where rand() > 1',
        ]

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for sql in cases:
                self.assertEqual(None, self.cache_key(conn, sql))

    def test_can_cache(self):
        cases = [
            ("SELECT 1 from okera_sample.sample", "SELECT 1 FROM okera_sample.sample"),
            ("SELECT user() from okera_sample.sample",
             "SELECT 'okera' FROM okera_sample.sample"),
            ("SELECT upper(user()) from okera_sample.sample",
             "SELECT 'OKERA' FROM okera_sample.sample"),
            ('SELECT * FROM okera_sample.sample',
             'SELECT record FROM okera_sample.sample'),
            ('SELECT * FROM okera_sample.sample where record is not null',
             'SELECT record FROM okera_sample.sample WHERE record IS NOT NULL'),
        ]

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for sql, key in cases:
                self.assertEqual(key, self.cache_key(conn, sql))

    @unittest.skip("AuthorizeQuery by passing referenced tables will be deprecated.")
    def test_cte_rewrite(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            sql, _, _ = self.cte_rewrite(conn, "SELECT * FROM rs.alltypes_s3",
                                         ['rs.alltypes_s3'])
            print(sql)
            self.assertEqual('SELECT * FROM rs.alltypes_s3', sql)

            sql, _, _ = self.cte_rewrite(conn, "SELECT * FROM rs.alltypes_s3",
                                         ['rs.alltypes_s3'], "testuser")
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_rs__alltypes_s3 AS ' +
                '(SELECT int_col, float_col, string_col FROM rs.alltypes_s3) ' +
                'SELECT * FROM okera_rewrite_rs__alltypes_s3', sql)

            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self.cte_rewrite(conn, "SELECT * FROM rs.nonexistent", ['rs.nonexistent'])
            self.assertTrue('Referenced table does not exist' in str(ex_ctx.exception))

    @unittest.skip("BigQuery test data is not loaded.")
    def test_cte_big_query(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS bigquery_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE bigquery_test.attr")

            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql, user=user,
                                             client=TAuthorizeQueryClient.PRESTO)
                return sql

            sql = rewrite("SELECT * FROM jdbc_test_bigquery.customers")
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_bigquery__customers AS '\
                '(SELECT `dob`, `country_code`, `mac`, `customer_name`, `customer_id`, `ip`, '\
                '`customer_unique_id`, `customer_unique_name`, `email` FROM `demo`.`customers`) '\
                'SELECT * FROM okera_rewrite_jdbc_test_bigquery__customers `customers`',
                sql)

            # Column level permissions
            self._recreate_test_role(conn, 'bigquery_test_role', ['bq_testuser'])
            conn.execute_ddl(
                'GRANT SELECT(name, userid) ' +
                'ON TABLE jdbc_test_bigquery.user_account_data ' +
                'TO ROLE bigquery_test_role')
            sql = rewrite("SELECT * FROM jdbc_test_bigquery.user_account_data",
                          user='bq_testuser')
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_bigquery__user_account_data AS '\
                '(SELECT `name`, `userid` FROM `demo`.`user_account_data`) '\
                'SELECT * FROM '\
                'okera_rewrite_jdbc_test_bigquery__user_account_data `user_account_data`',
                sql)

            # Try count(*)
            result = conn.scan_as_json(
                "SELECT count(*) FROM jdbc_test_bigquery.user_account_data",
                requesting_user='bq_testuser')
            self.assertEqual([{'count(*)': 100}], result)

            # Row level permissions
            self._recreate_test_role(conn, 'bigquery_test_role', ['bq_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON TABLE jdbc_test_bigquery.customers ' +
                "WHERE country_code = 'AL'" +
                'TO ROLE bigquery_test_role')
            sql = rewrite("SELECT * FROM jdbc_test_bigquery.customers",
                          user='bq_testuser')
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_bigquery__customers AS '\
                '(SELECT `dob`, `country_code`, `mac`, `customer_name`, `customer_id`, `ip`, '\
                '`customer_unique_id`, `customer_unique_name`, `email` FROM `demo`.`customers` '\
                'WHERE `country_code` = \'AL\') '\
                'SELECT * FROM okera_rewrite_jdbc_test_bigquery__customers `customers`',
                sql)

            result = conn.scan_as_json("SELECT * FROM jdbc_test_bigquery.customers",
                                       requesting_user='bq_testuser')
            self.assertEqual(85, len(result))

            # Loop over all OOB deindentification functions
            conn.execute_ddl('ALTER TABLE jdbc_test_bigquery.customers ' +
                             'ADD COLUMN ATTRIBUTE email bigquery_test.attr')

            for udf, expected in [('mask', 'okera_udfs.mask(`email`)'),
                                  ('mask_ccn', "okera_udfs.mask_ccn(`email`)"),
                                  ('null', "CAST(NULL AS STRING)"),
                                  ('sha2', "CAST(to_base64(sha1(`email`)) AS STRING)"),
                                  ('tokenize', "okera_udfs.tokenize(`email`)"),
                                  ('zero', "''")]:
                self._recreate_test_role(conn, 'bigquery_test_role', ['bq_testuser'])
                conn.execute_ddl(
                    ('GRANT SELECT ON TABLE jdbc_test_bigquery.customers ' +
                     'TRANSFORM bigquery_test.attr WITH `%s`() ' +
                     'TO ROLE bigquery_test_role') % udf)
                sql = rewrite("SELECT * FROM jdbc_test_bigquery.customers",
                              user='bq_testuser')
                print(sql)
                self.assertEqual(
                    ('WITH okera_rewrite_jdbc_test_bigquery__customers AS '\
                     '(SELECT `dob`, `country_code`, `mac`, `customer_name`, `customer_id`, `ip`, '\
                     '`customer_unique_id`, `customer_unique_name`, '\
                     '%s as `email` FROM `demo`.`customers`) '\
                     'SELECT * FROM '\
                     'okera_rewrite_jdbc_test_bigquery__customers `customers`')
                    % expected, sql)

            # Ensure sets_intersect gets rewritten correctly
            self._recreate_test_role(conn, 'bigquery_test_role', ['bq_testuser'])
            conn.execute_ddl(
                ('GRANT SELECT ON TABLE jdbc_test_bigquery.customers ' +
                 'WHERE sets_intersect(`country_code`, \'US,AL\') ' +
                 'TO ROLE bigquery_test_role'))
            sql = rewrite("SELECT * FROM jdbc_test_bigquery.customers",
                            user='bq_testuser')
            print(sql)
            self.assertEqual(
                ('WITH okera_rewrite_jdbc_test_bigquery__customers AS '\
                 '(SELECT `dob`, `country_code`, `mac`, `customer_name`, `customer_id`, `ip`, '\
                 '`customer_unique_id`, `customer_unique_name`, '\
                 '`email` FROM `demo`.`customers` '\
                 'WHERE okera_udfs.arrays_overlap(split(`country_code`, \',\'), split(\'US,AL\', \',\'))) '\
                 'SELECT * FROM '\
                 'okera_rewrite_jdbc_test_bigquery__customers `customers`'), sql)

    @unittest.skip("Athena test data is not loaded.")
    def test_cte_athena(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS athena_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE athena_test.attr")

            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql, user=user,
                                             client=TAuthorizeQueryClient.PRESTO)
                return sql

            sql = rewrite("SELECT * FROM jdbc_test_athena.alltypes_s3")
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_athena__alltypes_s3 AS '
                '(SELECT "bool_col", "tinyint_col", "smallint_col", "int_col", '
                '"bigint_col", "float_col", "double_col", "string_col", "varchar_col", '
                '"char_col", "timestamp_col", "decimal_col" FROM '
                '"okera_test"."alltypes_s3") '
                'SELECT * FROM okera_rewrite_jdbc_test_athena__alltypes_s3 "alltypes_s3"',
                sql)

            # Column level permissions
            self._recreate_test_role(conn, 'athena_test_role', ['athena_testuser'])
            conn.execute_ddl(
                'GRANT SELECT(bool_col, tinyint_col) ' +
                'ON TABLE jdbc_test_athena.alltypes_s3 ' +
                'TO ROLE athena_test_role')
            sql = rewrite("select * from jdbc_test_athena.alltypes_s3",
                          user='athena_testuser')
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_athena__alltypes_s3 AS '
                '(SELECT "bool_col", "tinyint_col" FROM '
                '"okera_test"."alltypes_s3") '
                'SELECT * FROM okera_rewrite_jdbc_test_athena__alltypes_s3 '
                '"alltypes_s3"',
                sql)

            # Try count(*)
            result = conn.scan_as_json(
                "SELECT count(*) as cnt FROM jdbc_test_athena.alltypes_s3",
                requesting_user='athena_testuser')
            self.assertEqual([{'cnt': 2}], result)

            # Row level permissions
            self._recreate_test_role(conn, 'athena_test_role', ['athena_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON TABLE jdbc_test_athena.alltypes_s3 ' +
                "WHERE string_col = 'hello'" +
                'TO ROLE athena_test_role')
            sql = rewrite("SELECT * FROM jdbc_test_athena.alltypes_s3",
                          user='athena_testuser')
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_athena__alltypes_s3 AS '
                '(SELECT "bool_col", "tinyint_col", "smallint_col", "int_col", '
                '"bigint_col", "float_col", "double_col", "string_col", "varchar_col", '
                '"char_col", "timestamp_col", "decimal_col" FROM '
                '"okera_test"."alltypes_s3" '
                'WHERE "string_col" = \'hello\') '
                'SELECT * FROM okera_rewrite_jdbc_test_athena__alltypes_s3 "alltypes_s3"',
                sql)

            sql = rewrite("SELECT * FROM jdbc_test_athena.alltypes_s3",
                          user='athena_testuser')
            self.assertEqual(1, len(result))

            # Loop over all OOB deindentification functions
            conn.execute_ddl('ALTER TABLE jdbc_test_athena.alltypes_s3 ' +
                             'ADD COLUMN ATTRIBUTE string_col athena_test.attr')

            for udf, expected in [('mask', 'CAST(lpad(\'\', length(("string_col")), \'X\') AS VARCHAR(255))'),
                                  ('mask_ccn', 'CAST((\'XXXX-XXXX-XXXX\' || substr(("string_col"), length(("string_col"))-3) AS VARCHAR(255))'),
                                  ('null', "CAST(CAST(NULL AS STRING) AS VARCHAR(255))"),
                                  ('sha2', 'CAST(from_base(substr(to_hex(sha256(to_utf8(cast(("string_col") as varchar)))), 1, 15), 16) AS VARCHAR(255))'),
                                  ('tokenize', 'CAST(to_hex(sha1(to_utf8(cast(("string_col") as varchar)))) AS VARCHAR(255))'),
                                  ('zero', "CAST('' AS VARCHAR(255))")]:
                self._recreate_test_role(conn, 'athena_test_role', ['athena_testuser'])
                conn.execute_ddl(
                    ('GRANT SELECT ON TABLE jdbc_test_athena.alltypes_s3 ' +
                     'TRANSFORM athena_test.attr WITH `%s`() ' +
                     'TO ROLE athena_test_role') % udf)
                sql = rewrite("SELECT string_col FROM jdbc_test_athena.alltypes_s3",
                              user='athena_testuser')
                print(udf, sql)
                self.assertEqual(
                    ('WITH okera_rewrite_jdbc_test_athena__alltypes_s3 AS '
                    '(SELECT %s as "string_col" FROM '
                    '"okera_test"."alltypes_s3") '
                    'SELECT "string_col" FROM '
                    'okera_rewrite_jdbc_test_athena__alltypes_s3 "alltypes_s3"')
                    % expected, sql)

            # Ensure sets_intersect gets rewritten correctly
            self._recreate_test_role(conn, 'athena_test_role', ['athena_testuser', 'bqtestuser'])
            conn.execute_ddl(
                ('GRANT SELECT ON TABLE jdbc_test_athena.alltypes_s3 ' +
                    "WHERE sets_intersect(string_col, 'hello,abc') " +
                    'TO ROLE athena_test_role'))
            sql = rewrite("SELECT string_col FROM jdbc_test_athena.alltypes_s3",
                            user='athena_testuser')
            print(sql)
            self.assertEqual(
                ('WITH okera_rewrite_jdbc_test_athena__alltypes_s3 AS '
                '(SELECT "string_col" FROM '
                '"okera_test"."alltypes_s3" '
                'WHERE arrays_overlap(split("string_col", \',\'), split(\'hello,abc\', \',\'))) '
                'SELECT "string_col" FROM '
                'okera_rewrite_jdbc_test_athena__alltypes_s3 "alltypes_s3"'), sql)

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_cte_get_referenced_tables(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS snowflake_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE snowflake_test.attr")

            def rewrite(sql, user=None):
                sql, plan, referenced_tables = self.cte_rewrite(
                    conn, sql, client=TAuthorizeQueryClient.PRESTO, user=user)
                return sql, plan, referenced_tables

            test_sql = """select * from jdbc_test_snowflake.all_types a
                          join jdbc_test_snowflake.all_types b ON a.string = b.string"""
            sql, _, referenced_tables = rewrite(test_sql)
            self.assertTrue(sql is not None)
            self.assertEqual(len(referenced_tables), 1)
            self.assertTrue("jdbc_test_snowflake.all_types" in referenced_tables)

            test_sql = """select * from jdbc_test_snowflake.all_types a
                          join jdbc_test_snowflake.all_types2 b ON a.string = b.string"""
            sql, _, referenced_tables = rewrite(test_sql)
            self.assertTrue(sql is not None)
            self.assertEqual(len(referenced_tables), 2)
            self.assertTrue("jdbc_test_snowflake.all_types" in referenced_tables)
            self.assertTrue("jdbc_test_snowflake.all_types2" in referenced_tables)


    # Ensure sets_intersect gets rewritten correctly
    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_cte_snowflake_sets_intersect(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS snowflake_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE snowflake_test.attr")
            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            conn.execute_ddl(
                ("GRANT SELECT ON TABLE jdbc_test_snowflake.all_types " +
                 "WHERE sets_intersect(`string`, 'hello') OR sets_intersect(`string`, user_attribute('not_exist'))" +
                 "TO ROLE %s") % ('sf_test_role'))

            def rewrite(sql, user=None):
                sql, plan, referenced_tables = self.cte_rewrite(
                    conn, sql, client=TAuthorizeQueryClient.PRESTO, user=user)
                return sql, plan, referenced_tables

            sql, _, _ = rewrite("SELECT \"string\" FROM jdbc_test_snowflake.all_types",
                            user='sf_testuser')
            print(sql)
            self.assertEqual(
                ('WITH okera_rewrite_jdbc_test_snowflake__all_types AS '
                '(SELECT "STRING" as "string" FROM '
                '"DEMO_DB"."JDBC_TEST"."ALL_TYPES" '
                'WHERE arrays_overlap(split("STRING", \',\'), split(\'hello\', \',\')) '
                'OR arrays_overlap(split("STRING", \',\'), split(NULL, \',\'))) '
                'SELECT "string" FROM '
                'okera_rewrite_jdbc_test_snowflake__all_types "all_types"'), sql)

    # Ensure sql gets rewritten correctly when unqualified table name is specified
    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_cte_snowflake_unqualified_table_name(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            def rewrite(sql, default_db=None, user=None):
                sql, plan, referenced_tables = self.cte_rewrite(
                    conn, sql, client=TAuthorizeQueryClient.PRESTO, user=user,
                    default_db=default_db)
                return sql, plan, referenced_tables

            sql, _, _ = rewrite("SELECT * FROM all_types",
                    default_db='jdbc_test_snowflake')
            print(sql)
            self.assertEqual(
                ('WITH okera_rewrite_jdbc_test_snowflake__all_types AS '
                '(SELECT "VARCHAR" as "varchar", "STRING" as "string", '
                '"TEXT" as "text", "SMALLINT" as "smallint", '
                '"INT" as "int", "BIGINT" as "bigint", '
                '"INTEGER" as "integer", "DOUBLE" as "double", '
                '"NUMERIC" as "numeric", "NUMBER" as "number", '
                '"DECIMAL" as "decimal", "TIMESTAMP" as "timestamp", '
                '"CHAR" as "char", "BOOLEAN" as "boolean", '
                '"BINARY" as "binary", "VARBINARY" as "varbinary", "REAL" as "real" '
                'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES") '
                'SELECT * FROM '
                'okera_rewrite_jdbc_test_snowflake__all_types "all_types"'), sql)

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_cte_snowflake_pushdown(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS snowflake_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE snowflake_test.attr")

            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql,
                                             client=TAuthorizeQueryClient.PRESTO,
                                             user=user)
                return sql

            for test_sql in ['SELECT * FROM jdbc_test_snowflake.all_types',
                             'SELECT * FROM "jdbc_test_snowflake"."all_types"']:
                print("Original SQL:\n " + test_sql)
                sql = rewrite(test_sql)
                print("Rewritten SQL:\n " + sql)
                self.assertEqual(
                    'WITH okera_rewrite_jdbc_test_snowflake__all_types AS ' \
                    '(SELECT "VARCHAR" as "varchar", "STRING" as "string", ' \
                    '"TEXT" as "text", "SMALLINT" as "smallint", "INT" as "int", ' \
                    '"BIGINT" as "bigint", "INTEGER" as "integer", ' \
                    '"DOUBLE" as "double", "NUMERIC" as "numeric", ' \
                    '"NUMBER" as "number", "DECIMAL" as "decimal", ' \
                    '"TIMESTAMP" as "timestamp", "CHAR" as "char", ' \
                    '"BOOLEAN" as "boolean", "BINARY" as "binary", ' \
                    '"VARBINARY" as "varbinary", "REAL" as "real" ' \
                    'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES") ' \
                    'SELECT * FROM okera_rewrite_jdbc_test_snowflake__all_types ' \
                    '"all_types"', sql)
                result = conn.scan_as_json(test_sql, client=TAuthorizeQueryClient.PRESTO)
                print(result)
                self.assertEqual(2, len(result))

            # Column level permissions
            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            conn.execute_ddl(
                'GRANT SELECT(`real`, `text`) ' +
                'ON TABLE jdbc_test_snowflake.all_types ' +
                'TO ROLE sf_test_role')
            sql = rewrite("SELECT * FROM jdbc_test_snowflake.all_types",
                          user='sf_testuser')
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_snowflake__all_types AS (' +
                'SELECT "TEXT" as "text", "REAL" as "real" ' +
                'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES") ' +
                'SELECT * FROM okera_rewrite_jdbc_test_snowflake__all_types ' +
                '"all_types"', sql)
            result = conn.scan_as_json("SELECT * FROM jdbc_test_snowflake.all_types",
                                       requesting_user='sf_testuser')
            self.assertEqual(
                result,
                [{'text': None, 'real': None}, {'text': 'testtext', 'real': 10.0}])


            # Try count(*)
            test_sql = "SELECT count(*) FROM jdbc_test_snowflake.all_types"
            sql = rewrite(test_sql, user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_snowflake__all_types ' +
                'AS (SELECT "TEXT" as "text", "REAL" as "real" ' +
                'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES") ' +
                'SELECT "count"(*) FROM okera_rewrite_jdbc_test_snowflake__all_types ' +
                '"all_types"', sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser')
            self.assertEqual([{'count(*)': 2}], result)

            # Row level permissions
            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON TABLE jdbc_test_snowflake.all_types ' +
                "WHERE `text` = 'testtext'" +
                'TO ROLE sf_test_role')

            for test_sql in ['SELECT * FROM jdbc_test_snowflake.all_types']:
                print("Original SQL:\n " + test_sql)
                sql = rewrite(test_sql, user='sf_testuser')
                print("Rewritten SQL:\n " + sql)
                self.assertEqual(
                    'WITH okera_rewrite_jdbc_test_snowflake__all_types ' +
                    'AS (SELECT "VARCHAR" as "varchar", "STRING" as "string", ' +
                    '"TEXT" as "text", "SMALLINT" as "smallint", ' +
                    '"INT" as "int", "BIGINT" as "bigint", ' +
                    '"INTEGER" as "integer", "DOUBLE" as "double", ' +
                    '"NUMERIC" as "numeric", "NUMBER" as "number", ' +
                    '"DECIMAL" as "decimal", "TIMESTAMP" as "timestamp", ' +
                    '"CHAR" as "char", "BOOLEAN" as "boolean", ' +
                    '"BINARY" as "binary", "VARBINARY" as "varbinary", ' +
                    '"REAL" as "real" ' +
                    'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES" ' +
                    'WHERE "TEXT" = \'testtext\') ' +
                    "SELECT * FROM okera_rewrite_jdbc_test_snowflake__all_types " +
                    "\"all_types\"", sql)
                result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                           client=TAuthorizeQueryClient.PRESTO)
                self.assertEqual(1, len(result))

            # Loop over all OOB deindentification functions
            conn.execute_ddl('ALTER TABLE jdbc_test_snowflake.all_types ' +
                             'ADD COLUMN ATTRIBUTE `text` snowflake_test.attr')

            for test_sql in ['SELECT * FROM jdbc_test_snowflake.all_types']:
                for udf, expected in [('mask', 'okera_udfs.public.mask("TEXT")'),
                                      ('mask_ccn', 'okera_udfs.public.mask_ccn("TEXT")'),
                                      ('null', 'CAST(NULL AS STRING)'),
                                      ('sha2', 'CAST(sha2("TEXT") AS STRING)'),
                                      ('tokenize',
                                       'okera_udfs.public.tokenize' + \
                                       '("TEXT", last_query_id())'),
                                      ('zero', "''")]:
                    self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
                    conn.execute_ddl(
                        ('GRANT SELECT ON TABLE jdbc_test_snowflake.all_types ' +
                         'TRANSFORM snowflake_test.attr WITH `%s`() ' +
                         'TO ROLE sf_test_role') % udf)
                    print("Original SQL:\n " + test_sql)
                    sql = rewrite(test_sql, user='sf_testuser')
                    print("Rewritten SQL:\n " + sql)
                    self.assertEqual(
                        ('WITH okera_rewrite_jdbc_test_snowflake__all_types AS ' +
                         '(SELECT "VARCHAR" as "varchar", ' +
                         '"STRING" as "string", %s as "text", ' +
                         '"SMALLINT" as "smallint", ' +
                         '"INT" as "int", "BIGINT" as "bigint", ' +
                         '"INTEGER" as "integer", ' +
                         '"DOUBLE" as "double", "NUMERIC" as "numeric", ' +
                         '"NUMBER" as "number", "DECIMAL" as "decimal", ' +
                         '"TIMESTAMP" as "timestamp", "CHAR" as "char", ' +
                         '"BOOLEAN" as "boolean", "BINARY" as "binary", ' +
                         '"VARBINARY" as "varbinary", "REAL" as "real" ' +
                         'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES") ' +
                         'SELECT * FROM okera_rewrite_jdbc_test_snowflake__all_types ' +
                         '"all_types"') %
                        expected, sql)
                    result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                               client=TAuthorizeQueryClient.PRESTO)
                    self.assertEqual(2, len(result))

            for test_sql in [
                    'select * from "jdbc_test_snowflake"."all_types" a ' +
                    'join "jdbc_test_snowflake"."all_types" b ON a.string = b.string',
                    'select * from jdbc_test_snowflake.all_types a ' +
                    'join jdbc_test_snowflake.all_types b ON a.string = b.string']:
                print("Original SQL:\n " + test_sql)
                sql = rewrite(test_sql, user='sf_testuser')
                print("Rewritten SQL:\n " + sql)
                self.assertEqual(
                    'WITH okera_rewrite_jdbc_test_snowflake__all_types ' +
                    'AS (SELECT "VARCHAR" as "varchar", "STRING" as "string", ' +
                    '\'\' as "text", "SMALLINT" as "smallint", "INT" as "int", ' +
                    '"BIGINT" as "bigint", "INTEGER" as "integer", ' +
                    '"DOUBLE" as "double", "NUMERIC" as "numeric", ' +
                    '"NUMBER" as "number", "DECIMAL" as "decimal", ' +
                    '"TIMESTAMP" as "timestamp", "CHAR" as "char", ' +
                    '"BOOLEAN" as "boolean", "BINARY" as "binary", ' +
                    '"VARBINARY" as "varbinary", "REAL" as "real" ' +
                    'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES") ' +
                    'SELECT * FROM (okera_rewrite_jdbc_test_snowflake__all_types ' +
                    '"a" INNER JOIN okera_rewrite_jdbc_test_snowflake__all_types "b" ' +
                    'ON ("a"."string" = "b"."string"))', sql)

            test_sql = '''
  SELECT  SUM(1) sum_number_of_reco, DATE_ADD('DAY', CAST((-1 * ((1 + MOD((MOD((MOD((MOD(DATE_DIFF('DAY', CAST('1995-01-01' AS DATE),
        CAST(CAST(superstore.date AS DATE) AS DATE)), 7) + ABS(7)), 7) + 7), 7) + ABS(7)), 7)) - 1)) AS BIGINT),
        CAST(DATE_TRUNC('day', CAST(superstore.date AS DATE)) AS timestamp)) twk_order_date_ok, YEAR(CAST(superstore.date AS DATE)) yr_order_date_nk,
        DAY_OF_WEEK(CAST(superstore.date AS DATE)) day_of_week, DAY_OF_MONTH(CAST(superstore.date AS DATE)) day_of_month,
        DAY_OF_YEAR(CAST(superstore.date AS DATE)) day_of_year, WEEK_OF_YEAR(CAST(superstore.date AS DATE)) week_of_year,
        YEAR_OF_WEEK(CAST(superstore.date AS DATE)) year_of_week
  FROM jdbc_test_snowflake.all_types2 superstore
  GROUP BY 2, 3, 4, 5, 6, 7, 8'''
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql)
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(2, len(result))

            for test_sql in [
                    'select * from okera.jdbc_test_snowflake.all_types a',
                    'select * from "okera"."jdbc_test_snowflake"."all_types" a']:
                print("Original SQL:\n " + test_sql)
                sql = rewrite(test_sql)
                print("Rewritten SQL:\n " + sql)
                result = conn.scan_as_json(test_sql, client=TAuthorizeQueryClient.PRESTO)
                self.assertEqual(2, len(result))

            test_sql = '''
    SELECT DATE_FORMAT(date, '%Y-%m-%d') as date_val FROM jdbc_test_snowflake.all_types2
            '''
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql)
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(2, len(result))
            print(result)
            self.assertEqual(None, result[0]["date_val"])
            self.assertEqual('2017-02-28', result[1]["date_val"])

            test_sql = '''
    SELECT to_unixtime(date) as date_val FROM jdbc_test_snowflake.all_types2
            '''
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql)
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(2, len(result))
            print(result)
            self.assertEqual(None, result[0]["date_val"])
            self.assertEqual(1488240000000, result[1]["date_val"])

            test_sql = '''
    with date_test as (
      select decimal, from_unixtime(1582985586) as x from jdbc_test_snowflake.all_types2
    )
    select
      current_date as c1,
      current_time  as c2,
      current_timestamp as c3,
      DATE(x) as c4,
      localtime as c5,
      now() as c6,
      to_unixtime(x) as c7,
      date_trunc('year', x) as c8,
      date_add('month', 2, x) as c9,
      date_diff('day', x, from_unixtime(1583995586)) as c10,
      date_format(x, 'YYYY-MM-DD') as c11,
      date_parse('2020-02-29 12:05:30', 'YYYY-MM-DD HH:mi:ss') as c12,
      extract(year FROM x) as c13,
      format_datetime(x, 'YYYY-MM-DD') as c14,
      parse_datetime('2020-02-29', 'YYYY-MM-DD') as c15,
      day(x) as c16,
      day_of_month(x) as c17,
      day_of_week(x) as c18,
      day_of_year(x) as c19,
      dow(x) as c20,
      doy(x) as c21,
      hour(x) as c22,
      minute(x) as c23,
      month(x) as c24,
      quarter(x) as c25,
      second(x) as c26,
      week(x) as c27,
      week_of_year(x) as c28,
      year(x) as c29,
      year_of_week(x) as c30,
      yow(x) as c31
    from date_test
    limit 1'''
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql)
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(1, len(result))
            # TODO: Assert some values. Since these are some current context, it would be
            # hard to assert the correctness.
            print(result)

    def test_cte_snowflake_pushdown_recursive_with_clause(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql,
                                             client=TAuthorizeQueryClient.PRESTO,
                                             user=user)
                return sql
            test_sql = '''
                WITH RECURSIVE cte_sequence (n) AS (
                    SELECT 1 from (select 1 from jdbc_test_snowflake.all_types limit 1)
                UNION ALL
                    SELECT n+1 FROM cte_sequence WHERE n < 5
                )
                SELECT * FROM cte_sequence
            '''
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql)
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(5, len(result))
            print(result)
            self.assertEqual(1, result[0]["n"])
            self.assertEqual(2, result[1]["n"])
            self.assertEqual(3, result[2]["n"])
            self.assertEqual(4, result[3]["n"])
            self.assertEqual(5, result[4]["n"])

    def snowflake_verify_policy_on_column(self, conn, column):
        print('\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
        print('snowflake_verify_policy_on_column test for "%s" column\n' % column)

        def get_cast_type(col_upper):
            if col_upper in ['DOUBLE', 'REAL']:
                return 'DOUBLE'
            if col_upper in ['NUMERIC', 'DECIMAL']:
                return 'DECIMAL(10,2)'
            if col_upper in ['VARCHAR']:
                return 'VARCHAR(20)'
            if col_upper in ['CHAR']:
                return 'VARCHAR(10)'
            if col_upper in ['BIGINT', 'SMALLINT', 'INT', 'INTEGER', 'NUMBER']:
                return 'BIGINT'
            return 'STRING'

        def get_function_tuple_by_column(col_upper):
            if (col_upper in ['BIGINT', 'SMALLINT', 'INT', 'INTEGER', 'DOUBLE',
                              'NUMBER', 'REAL']):
                return [('null', 'CAST(NULL AS %s)' % get_cast_type(col_upper)),
                        ('mask', '0'),
                        ('sha2', 'to_number(substr(sha2(("%s")), 0, 10), \'xxxxxxxxxx\')' % col_upper),
                        ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' % col_upper),
                        ('zero', "0")]
            if (col_upper in ['NUMERIC', 'DECIMAL']):
                return [('null', 'CAST(NULL AS %s)' % get_cast_type(col_upper)),
                        ('mask', '0'),
                        ('sha2', 'to_number(substr(sha2(("%s")), 0, ' % col_upper),
                        ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' % col_upper),
                        ('zero', "0")]
            if (col_upper in ['BOOLEAN']):
                return [('null', 'CAST(NULL AS %s)' % col_upper),
                        ('mask', 'FALSE'),
                        ('sha2', 'CAST(to_number(substr(sha2(("%s")), 0, 10), \'xxxxxxxxxx\') AS BOOLEAN)' % col_upper),
                        ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' % col_upper),
                        ('zero', 'FALSE')]
            if (col_upper in ['TIMESTAMP']):
                return [('null', 'CAST(CAST(NULL AS TIMESTAMP) AS TIMESTAMP)'),
                        # FIXME: SF issue with tokenize for timestamp
                        # ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' % col_upper),
                        ('mask', '1970-01-01'),
                        ('sha2', '1970-01-01'),
                        ('zero', '1970-01-01')]
            if (col_upper in ['DATE']):
                return [('null', 'CAST(CAST(NULL AS TIMESTAMP) AS DATE)'),
                        ('sha2', '1970-01-01'),
                        # FIXME: SF issue with tokenize for DATE
                        # ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' % col_upper),
                        ('mask', '1970-01-01'),
                        ('zero', '1970-01-01')]
            if (col_upper in ['VARCHAR', 'CHAR']):
                return [('mask', 'okera_udfs.public.mask("%s")' % col_upper),
                        ('mask_ccn', 'okera_udfs.public.mask_ccn("%s")' % col_upper),
                        ('null', 'CAST(NULL AS STRING)'),
                        ('sha2', 'CAST(substr(sha2(("%s")), 0, ' % col_upper),
                        ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' % col_upper),
                        ('zero', "''")]
            if (col_upper in ['BINARY', 'VARBINARY']):
                return [('null', 'CAST(NULL AS STRING)'),
                        ('sha2', 'CAST(sha2("%s") AS STRING)' % col_upper),
                        # FIXME: SF issue fails for mask(BINARY)
                        # ('mask', 'okera_udfs.public.mask("%s")' % col_upper),
                        # FIXME: SF issue fails for mask(BINARY)
                        # ('mask_ccn', 'okera_udfs.public.mask_ccn("%s")' % col_upper),
                        # FIXME: SF issue fails for tokenize(BINARY)
                        # ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' % col_upper),
                        ('zero', "''")]
            return [('mask', 'okera_udfs.public.mask("%s")' % col_upper),
                    ('mask_ccn', 'okera_udfs.public.mask_ccn("%s")' % col_upper),
                    ('null', 'CAST(NULL AS STRING)'),
                    ('sha2', 'CAST(sha2("%s") AS STRING)' % col_upper),
                    ('tokenize', 'okera_udfs.public.tokenize("%s", last_query_id())' %
                     col_upper),
                    ('zero', "''")]

        # Loop over all OOB deindentification functions
        conn.execute_ddl('ALTER TABLE jdbc_test_snowflake.all_types2 ' +
                         'ADD COLUMN ATTRIBUTE `%s` snowflake_test.attr' % column)

        col_upper = column.upper()
        test_sql = 'SELECT * FROM jdbc_test_snowflake.all_types2'
        self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
        for udf, expected in get_function_tuple_by_column(col_upper):
            conn.execute_ddl(
                ('GRANT SELECT ON TABLE jdbc_test_snowflake.all_types2 ' +
                 'TRANSFORM snowflake_test.attr WITH `%s`() ' +
                 'TO ROLE sf_test_role') % udf)
            print("\nTest: UDF / expected:\n " + udf + " / " + expected)
            print("Column:", col_upper)
            print("Original SQL:\n " + test_sql)
            sql, _, _ = self.cte_rewrite(conn, test_sql,
                                         client=TAuthorizeQueryClient.PRESTO,
                                         user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            self.assertTrue('%s' % expected in sql)
            self.assertTrue('as "%s"' % column in sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            print("The output:")
            print(result)
            self.assertEqual(2, len(result))
            # cleanup for next test.
            conn.execute_ddl(
                'REVOKE SELECT ON TABLE jdbc_test_snowflake.all_types2 ' +
                'TRANSFORM snowflake_test.attr WITH `%s`() FROM ROLE sf_test_role' %
                udf)

        if column in ['date']:
            # FIXME: date is not present in all_types table, we need another table
            # with data and should complete the referential integrity testing.
            print('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
            return

        conn.execute_ddl('ALTER TABLE jdbc_test_snowflake.all_types ' +
                         'ADD COLUMN ATTRIBUTE `%s` snowflake_test.attr' % column)

        self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
        test_sql = 'SELECT a.* FROM jdbc_test_snowflake.all_types2 a JOIN ' + \
                   'jdbc_test_snowflake.all_types b ON (a.%s = b.%s)' % \
                   (column, column)
        for udf, expected in get_function_tuple_by_column(col_upper):
            conn.execute_ddl(
                ('GRANT SELECT ON TABLE jdbc_test_snowflake.all_types2 ' +
                 'TRANSFORM snowflake_test.attr WITH `%s`() ' +
                 'TO ROLE sf_test_role') % udf)
            conn.execute_ddl(
                ('GRANT SELECT ON TABLE jdbc_test_snowflake.all_types ' +
                 'TRANSFORM snowflake_test.attr WITH `%s`() ' +
                 'TO ROLE sf_test_role') % udf)

            print("\nTest: UDF / expected:\n " + udf + " / " + expected)
            print("Column:", col_upper)
            print("Original SQL:\n " + test_sql)
            sql, _, _ = self.cte_rewrite(conn, test_sql,
                                         client=TAuthorizeQueryClient.PRESTO,
                                         user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            self.assertTrue('%s' % expected in sql)
            self.assertTrue('as "%s"' % column in sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            print("The output:")
            print(result)
            # If everything is null, joins will evaluate to no rows.
            if udf == 'null':
                self.assertEqual(0, len(result))
            elif udf == 'zero':
                # There are 2 rows in each table and join on zeros for both would result
                # in 4 rows (cartesian product).
                self.assertEqual(4, len(result))
            elif udf in ['mask'] and \
                 col_upper not in ['VARCHAR', 'CHAR', 'STRING', 'TEXT',
                                   'BINARY', 'VARBINARY']:
                # There are 2 rows in each table and join on zeros for both would result
                # in 4 rows (cartesian product), but we only return 0 for non-string
                # types.
                self.assertEqual(4, len(result))
            elif udf in ['sha2'] and col_upper in ['DATE', 'TIMESTAMP']:
                # sha2() returns a constant
                self.assertEqual(4, len(result))
            else:
                # There are 2 rows in each table but one row is all nulls.
                self.assertEqual(1, len(result))
            # Cleanup for next test.
            conn.execute_ddl(
                'REVOKE SELECT ON TABLE jdbc_test_snowflake.all_types2 ' +
                'TRANSFORM snowflake_test.attr WITH `%s`() FROM ROLE sf_test_role' %
                udf)
            conn.execute_ddl(
                'REVOKE SELECT ON TABLE jdbc_test_snowflake.all_types ' +
                'TRANSFORM snowflake_test.attr WITH `%s`() FROM ROLE sf_test_role' %
                udf)
        print('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_cte_snowflake_privacy_functions(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            for column in ['varchar', 'string', 'text', 'smallint', 'bigint', 'int',
                           'integer', 'double', 'numeric', 'number', 'decimal', 'real',
                           'char', 'boolean', 'binary', 'varbinary',
                           'timestamp', 'date']:
                conn.execute_ddl("DROP ATTRIBUTE IF EXISTS snowflake_test.attr")
                conn.execute_ddl("CREATE ATTRIBUTE snowflake_test.attr")
                self.snowflake_verify_policy_on_column(conn, column)

    @unittest.skipIf(common.TEST_LEVEL not in "all", "Skipping at unit/all level")
    def test_cte_snowflake_aliases(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS snowflake_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE snowflake_test.attr")

            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON TABLE jdbc_test_snowflake.all_types ' +
                "WHERE `text` = 'testtext'" +
                'TO ROLE sf_test_role')

            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql,
                                             client=TAuthorizeQueryClient.PRESTO,
                                             user=user)
                return sql

            test_sql = 'SELECT 1 AS "number_of_records", ' \
                       '"all_types"."bigint" AS "BigInt", ' \
                       '"all_types"."binary" AS "Binary", ' \
                       '"all_types"."boolean" AS "Boolean", ' \
                       '"all_types"."char" AS "Char", ' \
                       '"all_types"."decimal" AS "Decimal", ' \
                       '"all_types"."double" AS "Double", ' \
                       '"all_types"."int" AS "Int", ' \
                       '"all_types"."integer" AS "Integer", ' \
                       '"all_types"."number" AS "Number", ' \
                       '"all_types"."numeric" AS "Numeric", ' \
                       '"all_types"."real" AS "Real", ' \
                       '"all_types"."smallint" AS "Smallint", ' \
                       '"all_types"."string" AS "String", ' \
                       '"all_types"."text" AS "Text", ' \
                       '"all_types"."timestamp" AS "Timestamp", ' \
                       '"all_types"."varbinary" AS "Varbinary", ' \
                       '"all_types"."varchar" AS "Varchar" ' \
                       'FROM "jdbc_test_snowflake"."all_types" "all_types" ' \
                       'LIMIT 1000'
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql, user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_snowflake__all_types AS ' \
                '(SELECT "VARCHAR" as "varchar", "STRING" as "string", ' \
                '"TEXT" as "text", "SMALLINT" as "smallint", "INT" as "int", ' \
                '"BIGINT" as "bigint", "INTEGER" as "integer", "DOUBLE" as "double", ' \
                '"NUMERIC" as "numeric", "NUMBER" as "number", ' \
                '"DECIMAL" as "decimal", "TIMESTAMP" as "timestamp", "CHAR" as "char", ' \
                '"BOOLEAN" as "boolean", "BINARY" as "binary", ' \
                '"VARBINARY" as "varbinary", ' \
                '"REAL" as "real" FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES" ' \
                'WHERE "TEXT" = \'testtext\') ' \
                'SELECT 1 "number_of_records", "all_types"."bigint" "BigInt", ' \
                '"all_types"."binary" "Binary", "all_types"."boolean" "Boolean", ' \
                '"all_types"."char" "Char", "all_types"."decimal" "Decimal", ' \
                '"all_types"."double" "Double", "all_types"."int" "Int", ' \
                '"all_types"."integer" "Integer", "all_types"."number" "Number", ' \
                '"all_types"."numeric" "Numeric", "all_types"."real" "Real", ' \
                '"all_types"."smallint" "Smallint", "all_types"."string" "String", ' \
                '"all_types"."text" "Text", "all_types"."timestamp" "Timestamp", ' \
                '"all_types"."varbinary" "Varbinary", "all_types"."varchar" "Varchar" ' \
                'FROM okera_rewrite_jdbc_test_snowflake__all_types "all_types" ' \
                'LIMIT 1000', sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(1, len(result))

            test_sql = 'SELECT "jdbc_test_snowflake"."all_types"."string" ' \
                           'AS "String", ' \
                           'count(distinct "jdbc_test_snowflake"."all_types"."bigint") ' \
                           'AS "count" ' \
                           'FROM "jdbc_test_snowflake"."all_types" ' \
                           'GROUP BY "jdbc_test_snowflake"."all_types"."string" ' \
                           'ORDER BY "jdbc_test_snowflake"."all_types"."string" ASC'
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql, user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_snowflake__all_types AS ' \
                '(SELECT "STRING" as "string", ' \
                '"BIGINT" as "bigint" ' \
                'FROM "DEMO_DB"."JDBC_TEST"."ALL_TYPES" ' \
                'WHERE "TEXT" = \'testtext\') ' \
                'SELECT "all_types"."string" "String", '\
                '"count"(DISTINCT "all_types"."bigint") ' \
                '"count" ' \
                'FROM okera_rewrite_jdbc_test_snowflake__all_types "all_types" ' \
                'GROUP BY "all_types"."string" ' \
                'ORDER BY "all_types"."string" ASC', sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(1, len(result))

            conn.execute_ddl(
                'GRANT SELECT ON DATABASE sf_tpcds_1gb '
                'TO ROLE sf_test_role')

            test_sql = 'SELECT "Date Dim"."d_year" AS "d_year", "Item"."i_brand" ' \
                'AS "i_brand", '\
                '"Item"."i_brand_id" AS "i_brand_id", ' \
                'sum("sf_tpcds_1gb"."store_sales"."ss_ext_sales_price") AS "sum" ' \
                'FROM "sf_tpcds_1gb"."store_sales" LEFT JOIN ' \
                '"sf_tpcds_1gb"."date_dim" "Date Dim" ON ' \
                '"sf_tpcds_1gb"."store_sales"."ss_sold_date_sk" = ' \
                '"Date Dim"."d_date_sk" LEFT JOIN ' \
                '"sf_tpcds_1gb"."item" "Item" ' \
                'ON "sf_tpcds_1gb"."store_sales"."ss_item_sk" = "Item"."i_item_sk" ' \
                'WHERE ("Item"."i_manufact_id" = 128 AND "Date Dim"."d_moy" = 11) ' \
                'GROUP BY "Date Dim"."d_year", "Item"."i_brand", "Item"."i_brand_id" ' \
                'ORDER BY "Date Dim"."d_year" ASC, "sum" ASC, "Item"."i_brand_id" ASC, ' \
                '"Item"."i_brand" ASC'
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql, user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(83, len(result))

            # Grant an abac transform
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS sf_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE sf_test.attr")
            conn.execute_ddl(
                "ALTER TABLE sf_tpcds_1gb.store_sales ADD COLUMN ATTRIBUTE " +
                "ss_item_sk sf_test.attr")
            conn.execute_ddl(
                "ALTER TABLE sf_tpcds_1gb.item ADD COLUMN ATTRIBUTE " +
                "i_item_sk sf_test.attr")
            conn.execute_ddl(
                'REVOKE SELECT ON DATABASE sf_tpcds_1gb '
                'FROM ROLE sf_test_role')
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE sf_tpcds_1gb '
                'TRANSFORM sf_test.attr WITH sha2()'
                'TO ROLE sf_test_role')
            sql = rewrite(test_sql, user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(83, len(result))

            # Query is valid in case insensitive with upper case Item as table
            # alias and lower case item used later.
            test_sql = '''
SELECT "Date Dim".d_year AS d_year,
       item.i_brand_id AS i_brand_id,
       item.i_brand AS i_brand,
       sum(ss_ext_sales_price) AS "SUM"
FROM   sf_tpcds_1gb.store_sales
       LEFT JOIN sf_tpcds_1gb.date_dim "Date Dim"
              ON sf_tpcds_1gb.store_sales.ss_sold_date_sk = "Date Dim".d_date_sk
       LEFT JOIN sf_tpcds_1gb.item Item
              ON sf_tpcds_1gb.store_sales.ss_item_sk = item.i_item_sk
WHERE  ( item.i_manufact_id = 128 AND "Date Dim".d_moy = 11 )
GROUP  BY "Date Dim".d_year, item.i_brand_id, item.i_brand
ORDER  BY "Date Dim".d_year ASC, "SUM" DESC, item.i_brand_id ASC, item.i_brand asc
limit 10'''
            print("Original SQL:\n " + test_sql)
            sql = rewrite(test_sql, user='sf_testuser')
            print("Rewritten SQL:\n " + sql)
            result = conn.scan_as_json(test_sql, requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(10, len(result))

    @unittest.skipIf(common.TEST_LEVEL not in "all", "Skipping at unit/all level")
    def test_snowflake_tpcds_pushdown(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS snowflake_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE snowflake_test.attr")

            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE sf_tpcds_1gb '
                'TO ROLE sf_test_role')

            blacklist_files = [
                # Cumulative window frame unsupported for function "max"
                'query51.sql',
                'query54.sql',
                'query57.sql',
            ]

            tpcds_query_files_path = os.environ["OKERA_HOME"] + \
                '/integration/tests/benchmark/resources/snowflake_tpcds/'

            # Set this to a value to test just that file and alphabetically after that.
            from_file = None

            success = 0
            for file in sorted(os.listdir(tpcds_query_files_path)):
                print("Total files processed so far: " + str(success))
                # Skip non-avro files.
                if not file.endswith(".sql"):
                    continue
                elif file in blacklist_files:
                    continue
                elif from_file is not None and file < from_file:
                    continue
                else:
                    test_file = '%s/%s' % (tpcds_query_files_path, file)
                    with open(test_file, 'r') as sql_f:
                        test_sql = sql_f.read().strip()
                        test_sql = test_sql.replace("{database}", "sf_tpcds_1gb")
                        test_sql = test_sql.replace(";", "")
                        if 'limit ' not in test_sql.lower():
                            test_sql = test_sql + " LIMIT 1 "
                        print("\n" + test_file)
                        print("\n" + test_sql + "\n")
                        success += 1
                        result = conn.scan_as_json(test_sql,
                                                   requesting_user='sf_testuser',
                                                   client=TAuthorizeQueryClient.PRESTO)
                        self.assertTrue(result is not None)
            print("Total files success: " + str(success))
            print("Total files blacklisted: " + str(len(blacklist_files)))

    def test_cte_snowflake_error(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS snowflake_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE snowflake_test.attr")

            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON TABLE jdbc_test_snowflake.all_types ' +
                "WHERE `text` = 'testtext'" +
                'TO ROLE sf_test_role')

            def rewrite(sql, user=None):
                return self.cte_rewrite(conn, sql, client=TAuthorizeQueryClient.PRESTO,
                                        generate_plan=True, user=user)
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                rewrite("select not_a_col from jdbc_test_snowflake.all_types")
            print(ex_ctx.exception.detail)
            self.assertTrue('invalid identifier' in ex_ctx.exception.detail,
                            msg=ex_ctx.exception.detail)

    @unittest.skipIf(common.TEST_LEVEL not in "all", "Skipping at unit/all level")
    def test_cte_snowflake_if_condition(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, 'sf_test_role', ['sf_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON TABLE jdbc_test_snowflake.all_types ' +
                'TO ROLE sf_test_role')

            def rewrite(sql, user=None):
                return self.cte_rewrite(conn, sql, client=TAuthorizeQueryClient.PRESTO,
                                        generate_plan=True, user=user)
            sql_statement = "select if(smallint=1, 10, 20) as x from jdbc_test_snowflake.all_types"
            rewritten_sql = rewrite(sql_statement, 'sf_testuser')
            assert 'iff(' in rewritten_sql[0].lower()

            result = conn.scan_as_json(sql_statement,
                                       requesting_user='sf_testuser',
                                       client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['x'], 20)
            self.assertEqual(result[1]['x'], 10)

    @unittest.skip("Insert test data is not set up.")
    def test_snowflake_insert_rewrite(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ROLE IF EXISTS test_sf_insert_role")
            conn.execute_ddl("CREATE ROLE test_sf_insert_role")
            conn.execute_ddl("GRANT ROLE test_sf_insert_role TO GROUP %s" % TEST_USER)
            def rewrite(sql, user=None):
                sql,_,_ = self.cte_rewrite(
                    conn, sql, client=TAuthorizeQueryClient.SNOWFLAKE, user=user)
                return sql

            sf_native_query = """
                insert into COX_DB.PUBLIC.HOSPITAL_DISCHARGE (facility_id, facility_name, gender)
                values ('x1', 'x2', 'x3')
                """
            test_sql = sf_native_query

            # Should fail, no insert permissions
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                result_sql = rewrite(test_sql, user=TEST_USER)
                print(result_sql)
            self.assertTrue(
                "User 'testuser' does not have INSERT privileges INTO cox_db.hospital_discharge" in str(ex_ctx.exception))

            # GRANT SELECT, still bad
            conn.execute_ddl("""
                GRANT SELECT ON TABLE cox_db.hospital_discharge
                TO ROLE test_sf_insert_role""")
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                result_sql = rewrite(test_sql, user=TEST_USER)
                print(result_sql)
            self.assertTrue(
                "User 'testuser' does not have INSERT privileges INTO cox_db.hospital_discharge" in str(ex_ctx.exception))

            # GRANT INSERT, all good
            conn.execute_ddl("""
                GRANT INSERT ON TABLE cox_db.hospital_discharge
                TO ROLE test_sf_insert_role""")
            result_sql = rewrite(test_sql, user=TEST_USER)
            self.assertEqual(self.normalize(test_sql), self.normalize(result_sql))

    def test_cte_non_jdbc(self):
        # Plan generation against non-pushdown-able queries should fail
        # TODO: add cross JDBC datasource join queries.

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            def rewrite(sql, client, user=None):
                return self.cte_rewrite(conn, sql, client=client,
                                        generate_plan=True, user=user)
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                rewrite("select * from okera_sample.sample",
                        client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(TErrorCode.UNSUPPORTED_REQUEST, ex_ctx.exception.code)

            # TODO: this should work, see impala-recordservice-server.cc:AuthorizeQuery
            # for details.
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                rewrite("select * from okera_sample.sample",
                        client=TAuthorizeQueryClient.OKERA)
            self.assertEqual(TErrorCode.INVALID_REQUEST, ex_ctx.exception.code)

    def test_cte_jdbc(self):
        # Note the SQL is in the dialect of the RDBMS engine, not OkeraQL
        ctx = common.get_test_context()
        role1 = 'jdbc_rewrite_test_role1'
        role2 = 'jdbc_rewrite_test_role2'
        testuser1 = 'jdbc_rewrite_test_user1'
        testuser2 = 'jdbc_rewrite_test_user2'
        db = 'jdbc_test_redshift'
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, role1, [testuser1])
            self._recreate_test_role(conn, role2, [testuser2])

            def rewrite(sql, user=None):
                return self.cte_rewrite(conn, sql, client=TAuthorizeQueryClient.PRESTO,
                                        generate_plan=True, user=user)

            sql, plan, ref_tables = rewrite(
                'SELECT * FROM "jdbc_test_redshift"."all_types_1" limit 10')
            print(sql)
            self.assertEqual('WITH okera_rewrite_jdbc_test_redshift__all_types_1 AS ' \
                '(SELECT "varchar", "text", "smallint", "int", "bigint", ' \
                '"double", "numeric", "decimal", "timestamp", "char", "bool", "real" ' \
                'FROM "dev"."public"."all_types_1") ' \
                'SELECT * FROM okera_rewrite_jdbc_test_redshift__all_types_1 ' \
                '"all_types_1" LIMIT 10',
                             sql)
            self.assertTrue(plan is not None)
            self.assertTrue('jdbc_test_redshift.all_types_1' in ref_tables)


            sql, plan, ref_tables = rewrite(
                "SELECT * FROM jdbc_test_redshift.all_types_1 limit 10")
            self.assertEqual('WITH okera_rewrite_jdbc_test_redshift__all_types_1 AS ' \
                '(SELECT "varchar", "text", "smallint", "int", "bigint", "double", ' \
                '"numeric", "decimal", "timestamp", "char", "bool", "real" ' \
                'FROM "dev"."public"."all_types_1") ' \
                'SELECT * FROM okera_rewrite_jdbc_test_redshift__all_types_1 ' \
                '"all_types_1" LIMIT 10',
                             sql)
            self.assertTrue(plan is not None)
            self.assertTrue('jdbc_test_redshift.all_types_1' in ref_tables)
            result = conn.scan_as_json(
                "SELECT * FROM jdbc_test_redshift.all_types_1 limit 10",
                client=TAuthorizeQueryClient.PRESTO)
            self.assertEqual(10, len(result))
            self.assertEqual(12, len(result[0]))
            self.assertEqual(1, result[0]['smallint'])
            self.assertEqual('hello', result[0]['text'])

            # Try with testuser1, which can only access one column
            conn.execute_ddl(
                "GRANT SELECT(`TEXT`) ON TABLE %s.all_types_1 TO ROLE %s" % \
                (db, role1))
            sql, plan, _ = rewrite(
                "SELECT * FROM jdbc_test_redshift.all_types_1 limit 10", user=testuser1)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_redshift__all_types_1 AS (' +
                'SELECT "text" FROM "dev"."public"."all_types_1") ' +
                'SELECT * FROM okera_rewrite_jdbc_test_redshift__all_types_1 ' +
                '"all_types_1" LIMIT 10',
                sql)
            self.assertTrue(plan is not None)
            result = conn.scan_as_json(
                "SELECT * FROM jdbc_test_redshift.all_types_1 limit 10",
                client=TAuthorizeQueryClient.PRESTO,
                requesting_user=testuser1)
            self.assertEqual(10, len(result))
            self.assertEqual(1, len(result[0]))
            self.assertEqual('hello', result[0]['text'])

            # Try with testuser2, which has a row filter that removes all rows
            conn.execute_ddl(
                "GRANT SELECT ON TABLE %s.all_types_1 WHERE `int` = 0 TO ROLE %s" % \
                (db, role2))
            sql, plan, _ = rewrite(
                "SELECT * FROM jdbc_test_redshift.all_types_1 limit 10", user=testuser2)
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_redshift__all_types_1 AS ' +
                '(SELECT "varchar", ' +
                '"text", "smallint", "int", ' +
                '"bigint", "double", ' +
                '"numeric", "decimal", ' +
                '"timestamp", "char", "bool", ' +
                '"real" FROM "dev"."public"."all_types_1" ' +
                'WHERE "int" = 0) ' +
                'SELECT * FROM okera_rewrite_jdbc_test_redshift__all_types_1 ' +
                '"all_types_1" LIMIT 10',
                sql)
            self.assertTrue(plan is not None)
            result = conn.scan_as_json(
                "SELECT * FROM jdbc_test_redshift.all_types_1 limit 10",
                client=TAuthorizeQueryClient.PRESTO,
                requesting_user=testuser2)
            self.assertEqual(len(result), 0)

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_cte_redshift(self):
        # Note the SQL is in the dialect of the RDBMS engine, not OkeraQL
        ctx = common.get_test_context()
        role = 'jdbc_rewrite_test_role'
        testuser = 'jdbc_rewrite_test_user'
        db = 'jdbc_test_redshift'

        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, role, [testuser])
            conn.execute_ddl(
                ("GRANT SELECT ON DATABASE %s TRANSFORM abac.test_col WITH zero() " +
                 "TO ROLE %s") % (db, role))

            def scan(sql, col):
                row_root = conn.scan_as_json(sql, client=TAuthorizeQueryClient.PRESTO)
                row_user = conn.scan_as_json(
                    sql, client=TAuthorizeQueryClient.PRESTO, requesting_user=testuser)
                v_root = None
                v_user = None
                if row_root:
                    v_root = row_root[0][col]
                if row_user:
                    v_user = row_user[0][col]
                return v_root, v_user

            sql = "SELECT * FROM jdbc_test_redshift.all_data_types limit 1"
            self.assertEqual((None, None), scan(sql, 'varchar'))

            sql = "SELECT * FROM jdbc_test_redshift.all_types limit 1"
            self.assertEqual((None, ''), scan(sql, 'varchar'))

            sql = "SELECT * FROM jdbc_test_redshift.all_types_1 limit 1"
            self.assertEqual(('test', ''), scan(sql, 'varchar'))

            sql = "SELECT * FROM jdbc_test_redshift.drug_detail limit 1"
            self.assertEqual(("Dr. Reddy's Laboratories Limited", ''),
                             scan(sql, 'manufacturer'))

            sql = "SELECT * FROM jdbc_test_redshift.fact_ae limit 1"
            self.assertEqual(("patient_id", ''), scan(sql, 'patient_id'))

            # TODO: Table is wide and ooms the worker scanning it
            #self.assertEqual(("patient_id", ''),
            #                 scan("SELECT * FROM fact_ae_wide limit 1", 'patient_id'))
            sql = "SELECT * FROM jdbc_test_redshift.healthcare_data limit 1"
            self.assertEqual(("918", ''), scan(sql, 'participants'))

            sql = "SELECT * FROM jdbc_test_redshift.patient limit 1"
            self.assertEqual(("pjaxon0@ifeng.com", ''), scan(sql, 'email'))

            sql = "SELECT * FROM jdbc_test_redshift.user_account_data where name='Warren Reyes' limit 1"
            self.assertEqual(("auctor.odio@amet.ca", ''), scan(sql, 'email'))

            sql = "SELECT * FROM jdbc_test_redshift.zd1278 limit 1"
            self.assertEqual((None, None), scan(sql, 'src_pcntr_ds'))

            # Ensure sets_intersect gets rewritten correctly
            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql, user=user,
                                             client=TAuthorizeQueryClient.PRESTO)
                return sql

            self._recreate_test_role(conn, role, [testuser])
            conn.execute_ddl(
                ("GRANT SELECT ON TABLE jdbc_test_redshift.transactions " +
                 "WHERE sets_intersect(country, 'AU,FR,CH') " +
                 "TO ROLE %s") % (role))

            sql = rewrite("SELECT country FROM jdbc_test_redshift.transactions",
                            user=testuser)
            print(sql)
            self.assertEqual(
                ('WITH okera_rewrite_jdbc_test_redshift__transactions AS '
                '(SELECT "country" FROM '
                '"dev"."public"."transactions" '
                'WHERE okera_udfs.public.sets_intersect("country", \'AU,FR,CH\')) '
                'SELECT "country" FROM '
                'okera_rewrite_jdbc_test_redshift__transactions "transactions"'), sql)

    def test_cte_dremio(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS dremio_test.attr")
            conn.execute_ddl("CREATE ATTRIBUTE dremio_test.attr")

            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql, user=user,
                                             client=TAuthorizeQueryClient.PRESTO)
                return sql

            sql = rewrite("SELECT * FROM jdbc_test_dremio.alltypes_parquet")
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_dremio__alltypes_parquet AS '
                '(SELECT "id", "bool_col", "tinyint_col", "smallint_col", "int_col", '
                '"bigint_col", "float_col", "double_col", "date_string_col", '
                '"string_col", "timestamp_col" FROM '
                '"okera.cerebrodata-test"."alltypes_parquet") '
                'SELECT * FROM okera_rewrite_jdbc_test_dremio__alltypes_parquet '
                '"alltypes_parquet"',
                sql)

            # Column level permissions
            self._recreate_test_role(conn, 'dremio_test_role', ['dremio_testuser'])
            conn.execute_ddl(
                'GRANT SELECT(bool_col, tinyint_col) ' +
                'ON TABLE jdbc_test_dremio.alltypes_parquet ' +
                'TO ROLE dremio_test_role')
            sql = rewrite("select * from jdbc_test_dremio.alltypes_parquet",
                          user='dremio_testuser')
            print(sql)
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_dremio__alltypes_parquet AS '
                '(SELECT "bool_col", "tinyint_col" FROM '
                '"okera.cerebrodata-test"."alltypes_parquet") '
                'SELECT * FROM okera_rewrite_jdbc_test_dremio__alltypes_parquet '
                '"alltypes_parquet"',
                sql)

            # Try count(*)
            result = conn.scan_as_json(
                "SELECT count(*) as cnt FROM jdbc_test_dremio.alltypes_parquet",
                requesting_user='dremio_testuser')
            self.assertEqual([{'cnt': 8}], result)

            # Row level permissions
            self._recreate_test_role(conn, 'dremio_test_role', ['dremio_testuser'])
            conn.execute_ddl(
                'GRANT SELECT ON TABLE jdbc_test_dremio.alltypes_parquet ' +
                "WHERE smallint_col = 1 " +
                'TO ROLE dremio_test_role')
            sql = rewrite("SELECT * FROM jdbc_test_dremio.alltypes_parquet",
                          user='dremio_testuser')
            self.assertEqual(
                'WITH okera_rewrite_jdbc_test_dremio__alltypes_parquet AS '
                '(SELECT "id", "bool_col", "tinyint_col", "smallint_col", "int_col", '
                '"bigint_col", "float_col", "double_col", "date_string_col", "string_col", '
                '"timestamp_col" FROM '
                '"okera.cerebrodata-test"."alltypes_parquet" '
                'WHERE "smallint_col" = 1) '
                'SELECT * FROM okera_rewrite_jdbc_test_dremio__alltypes_parquet "alltypes_parquet"',
                sql)

            result = conn.scan_as_json(
                "SELECT * FROM jdbc_test_dremio.alltypes_parquet",
                requesting_user='dremio_testuser')
            self.assertEqual(4, len(result))

            # Loop over all OOB deindentification functions
            conn.execute_ddl('ALTER TABLE jdbc_test_dremio.alltypes_parquet ' +
                             'ADD COLUMN ATTRIBUTE string_col dremio_test.attr')

            for udf, expected in [('mask', 'lpad(\'\', length(("string_col")), \'X\')'),
                                  ('mask_ccn', '(\'XXXX-XXXX-XXXX-\' || substr(("string_col"), length(("string_col"))-3))'),
                                  ('null', "CAST(NULL AS VARCHAR)"),
                                  ('sha2', 'CAST(SHA1(("string_col")) AS STRING)'),
                                  ('tokenize', 'SHA1(("string_col"))'),
                                  ('zero', "''")
                                  ]:
                self._recreate_test_role(conn, 'dremio_test_role', ['dremio_testuser'])
                conn.execute_ddl(
                    ('GRANT SELECT ON TABLE jdbc_test_dremio.alltypes_parquet ' +
                     'TRANSFORM dremio_test.attr WITH `%s`() ' +
                     'TO ROLE dremio_test_role') % udf)
                sql = rewrite("SELECT string_col FROM jdbc_test_dremio.alltypes_parquet",
                              user='dremio_testuser')
                print(udf, sql)
                self.assertEqual(
                    ('WITH okera_rewrite_jdbc_test_dremio__alltypes_parquet AS '
                    '(SELECT %s as "string_col" FROM '
                    '"okera.cerebrodata-test"."alltypes_parquet") '
                    'SELECT "string_col" FROM '
                    'okera_rewrite_jdbc_test_dremio__alltypes_parquet "alltypes_parquet"')
                    % expected, sql)

    def test_cte_dremio_with_clause(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            def rewrite(sql, user=None):
                sql, _, _ = self.cte_rewrite(conn, sql, user=user,
                                             client=TAuthorizeQueryClient.PRESTO)
                return sql

            # CTE Rewrite test for queries containing CTEs
            # case 1: Query starting with "WITH" clause
            sql = rewrite('WITH ct1 AS (SELECT * FROM dremio_tpcds.customer), '
                          'ct2 AS (SELECT * FROM ct1) '
                          'SELECT * FROM ct2')

            self.assertEqual(
                ('WITH okera_rewrite_dremio_tpcds__customer AS '
                '(SELECT "c_customer_sk", "c_customer_id", "c_current_cdemo_sk", '
                '"c_current_hdemo_sk", "c_current_addr_sk", "c_first_shipto_date_sk", '
                '"c_first_sales_date_sk", "c_salutation", "c_first_name", "c_last_name", '
                '"c_preferred_cust_flag", "c_birth_day", "c_birth_month", '
                '"c_birth_year", "c_birth_country", "c_login", "c_email_address", '
                '"c_last_review_date" '
                'FROM "okera.cerebrodata-test.perf.tpcds.unpartitioned.parquet.tpcds_001GB"."customer") , '
                'ct1 AS ( SELECT * FROM okera_rewrite_dremio_tpcds__customer "customer" ) , '
                'ct2 AS ( SELECT * FROM ct1 "ct1" ) SELECT * FROM ct2 "ct2"'),
                sql)

            # CTE Rewrite test for queries containing CTEs
            # case 2: Query having "WITH" clause but not at the very start
            sql = rewrite('SELECT * FROM ( '
                          'WITH ct1 AS (SELECT * FROM dremio_tpcds.customer), '
                          'ct2 AS (SELECT * FROM ct1) '
                          'SELECT * FROM ct2 )')

            self.assertEqual(
                ('WITH okera_rewrite_dremio_tpcds__customer AS '
                '(SELECT "c_customer_sk", "c_customer_id", "c_current_cdemo_sk", '
                '"c_current_hdemo_sk", "c_current_addr_sk", "c_first_shipto_date_sk", '
                '"c_first_sales_date_sk", "c_salutation", "c_first_name", "c_last_name", '
                '"c_preferred_cust_flag", "c_birth_day", "c_birth_month", '
                '"c_birth_year", "c_birth_country", "c_login", "c_email_address", '
                '"c_last_review_date" '
                'FROM "okera.cerebrodata-test.perf.tpcds.unpartitioned.parquet.tpcds_001GB"."customer") '
                'SELECT * FROM ( '
                    'WITH ct1 AS ( SELECT * FROM okera_rewrite_dremio_tpcds__customer "customer" ) , '
                    'ct2 AS ( SELECT * FROM ct1 "ct1" ) '
                    'SELECT * FROM ct2 "ct2" )'), sql)

            # CTE Rewrite test for queries containing CTEs
            # case 3: Complex query having "WITH" clause
            dremio_tpcds_test_file = os.environ["OKERA_HOME"] + \
                '/integration/tests/benchmark/resources/dremio_tpcds/query01.sql'
            with open(dremio_tpcds_test_file, 'r') as sql_f:
                test_sql = sql_f.read().strip()
                test_sql = test_sql.format(database="dremio_tpcds")
                print("\n" + dremio_tpcds_test_file)
                print("\n Original SQL:\n " + test_sql + "\n")
                result = conn.scan_as_json(test_sql,
                                            requesting_user='root',
                                            client=TAuthorizeQueryClient.PRESTO)
                self.assertTrue(result is not None)

            # CTE Rewrite test for queries containing CTEs
            # case 4: RECURSIVE CTEs
            # Note - RECURSIVE CTEs are not supported in Dremio as of Jul-2021.
            #   So we have a added a function to test RECURSIVE CTE as part of snowflake
            #   pushdown tests. [Please refer: test_cte_snowflake_pushdown_recursive_with_clause()]

    def test_rewrite_in_set(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("DROP ROLE IF EXISTS test_in_set_role")
            conn.execute_ddl("CREATE ROLE test_in_set_role")
            conn.execute_ddl("GRANT ROLE test_in_set_role TO GROUP %s" % TEST_USER)
            conn.execute_ddl("""
                GRANT SELECT ON TABLE rs.alltypes_s3
                WHERE (in_set('ALL', NULL)
                       OR in_set(string_col, user_attribute('does_not_exist'))
                       OR in_set(string_col, 'abc,def')
                       OR in_set(string_col, '"abc,def",xyz, "foo,bar"')
                       OR in_set(string_col, '"1,2",3, "4, 5", "6"",7"'))
                TO ROLE test_in_set_role""")

            def rewrite(sql, user=None):
                sql, plan, referenced_tables = self.cte_rewrite(
                    conn, sql, client=TAuthorizeQueryClient.PRESTO, user=user)
                return sql, plan, referenced_tables

            test_sql = """select * from rs.alltypes_s3"""
            result_sql, _, referenced_tables = rewrite(test_sql)
            assert 'WHERE' not in result_sql

            result_sql, _, referenced_tables = rewrite(test_sql, user=TEST_USER)
            print(result_sql)
            assert "WHERE (NULL OR string_col IN ('abc', 'def') " \
                   "OR string_col IN ('abc,def', 'xyz', 'foo,bar') " \
                   "OR string_col IN ('1,2', '3', '4, 5', '6\",7'))" in result_sql
            assert 'in_set' not in result_sql

            # Clean up by dropping the role
            conn.execute_ddl("DROP ROLE IF EXISTS test_in_set_role")

    def test_rewrite_hive_privacy(self):
        self.maxDiff = None
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            db = "hive_privacy_db"
            tbl = "sample_table"

            ddls = [
                "DROP ROLE IF EXISTS test_hive_privacy_role",
                "CREATE ROLE test_hive_privacy_role",
                "GRANT ROLE test_hive_privacy_role TO GROUP %s" % TEST_USER,
                "DROP DATABASE IF EXISTS %s CASCADE" % (db),

                "DROP ATTRIBUTE IF EXISTS hive_privacy.attr1",
                "CREATE ATTRIBUTE hive_privacy.attr1",

                "CREATE DATABASE %s" % (db),
                "CREATE TABLE %s.%s (c1 STRING ATTRIBUTE hive_privacy.attr1)" % (db, tbl),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # This list should be kept in sync with FunctionCallExpr.EXTERNAL_PRIVACY_UDFS
            for fn in ["mask_ccn", "mask", "sha2", "tokenize"]:
                print("Functions: " + fn)
                conn.execute_ddl(
                    """GRANT SELECT ON TABLE %s.%s
                       TRANSFORM hive_privacy.attr1 WITH `%s`()
                       TO ROLE test_hive_privacy_role""" % (db, tbl, fn))

                def rewrite(sql, user=None):
                    sql, plan, referenced_tables = self.cte_rewrite(
                        conn, sql, client=TAuthorizeQueryClient.HIVE, user=user)
                    return sql, plan, referenced_tables

                test_sql = """select * from %s.%s""" % (db, tbl)
                result_sql, _, _ = rewrite(test_sql, user=TEST_USER)
                assert ('okera_udfs.%s(`c1`)' % (fn)) in result_sql

                conn.execute_ddl(
                    """REVOKE SELECT ON TABLE %s.%s
                       TRANSFORM hive_privacy.attr1 WITH `%s`()
                       FROM ROLE test_hive_privacy_role""" % (db, tbl, fn))

            # Clean up by dropping the role
            conn.execute_ddl("DROP ROLE IF EXISTS test_hive_privacy_role")

    @pytest.mark.perf
    @unittest.skipIf(not PERF.run_perf(), "Skipping perf tests")
    def test_measure_has_full_access(self):
        """ Measures perf of fullAccess on a wide table. """
        DB = "full_access_perf_db"
        ctx = common.get_test_context()
        cols = 1000
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, DB)
            ddl = 'CREATE EXTERNAL TABLE %s.wide(' % DB
            ddl += 'i INT'
            for i in range(0, cols):
              ddl += ', i' + str(i) + ' INT'
            ddl += ") STORED AS TEXTFILE LOCATION 's3://cerebrodata-test/not-there'"
            conn.execute_ddl(ddl)

            conn.execute_ddl("DROP ROLE IF EXISTS full_access_test_role")
            conn.execute_ddl("CREATE ROLE full_access_test_role")
            conn.execute_ddl("GRANT ROLE full_access_test_role TO GROUP %s" % TEST_USER)
            conn.execute_ddl("CREATE ATTRIBUTE IF NOT EXISTS test.string_col")
            conn.execute_ddl("""
                GRANT SELECT ON DATABASE %s
                TRANSFORM test.string_col WITH tokenize()
                TO ROLE full_access_test_role""" % DB)

            def get_admin():
                self.authorize_table(conn, DB, 'wide')

            def get_test_user():
                self.authorize_table(conn, DB, 'wide', user=TEST_USER)

            PERF.measure(get_admin, 'wide-table', 'admin', 'authorize_query')
            PERF.measure(get_test_user, 'wide-table', TEST_USER, 'authorize_query')

    @pytest.mark.perf
    def test_scan_dummy_spark_metadata(self):
        DB = "spark_dummy_scan_db"
        TEST_ROLE = 'yotpo_test_role'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, DB)
            conn.execute_ddl('''
CREATE EXTERNAL TABLE %s.fact_segment_events_last (
  col ARRAY<STRING> COMMENT 'from deserializer'
)
PARTITIONED BY (
  year INT,
  month INT,
  day INT)
WITH SERDEPROPERTIES ('path'='s3://yotpo-data-lake/warehouse/segment/full/last', 'serialization.format'='1')
STORED AS PARQUET
LOCATION 's3://yotpo-data-lake/warehouse/segment/full/last'
TBLPROPERTIES (
    'spark.sql.sources.schema.partCol.0'='year',
    'spark.sql.sources.schema.part.9'='rated_text_removed_albums\",\"type\":{\"type\":\"array\",\"elementType\":\"string\",\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_neutral_reviews_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_invited_user_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_facebook_ad_account_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_autoplay_speed_checkbox\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_conversation_duration\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_public\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_message_body\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_questions_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_qn_a\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_page_number\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_has_referrer_first_name_variable\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_review_notifications_star2\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_review_notifications_subscribed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_count_orders\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_cta_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_rich_snippets\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_email_rendering_succeeded\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is5_stars_checked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_rad_prefill_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_email_subject\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_hashtag\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_deleted_user\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_package\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_shoppable_instagram\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_promoted_products_widget\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties__rrs_sent_in_billing_cycle\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_package_monthly_price\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_reminder_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_website_publish_link\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_agent_username\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_phrase\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_yotpo_product_score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"anonymous_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"event_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_page_category\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_app_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_top_negative_sentences\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"product_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"review_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"sentence\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_default_image_used\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_domain\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_pla\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_result_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"proper',
    'spark.sql.sources.schema.partCol.2'='day',
    'spark.sql.sources.schema.partCol.1'='month',
    'spark.sql.sources.schema.part.6'='true,\"metadata\":{}},{\"name\":\"properties_signup_country\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_email_template_version_order\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_admin_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_agent_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_total_products_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_subscribed_to_blog_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_rich_snippets\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sort_by\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_path\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_uploader_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_results_per_page\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_facebook_token\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tag_domain_key\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_map_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_sent_tsr\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_revenue\",\"type\":\"double\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_product\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_tab_position_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_ip\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_signup_utmmedium\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_topic_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_cta_location\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldform_sfdccampaign\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_mapcustom_fields_enabled\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_conversation_link\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_pinterest_token_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_primary_color\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_utm_content_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_explicit_review\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_old_package\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_external_order_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_facebook_spend\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_interaction_response\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"fieldId\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"fieldRequired\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"fieldType\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"label\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"value\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_new_main_widget_layout\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_sentiment_filter\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"user_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_device_brand\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_invited_user_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldsubscribedto_email_course\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_show_total_count_checkbox\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_video_title\",\"type\":\"string\",\"nullab',
    'spark.sql.sources.schema.part.5'='to_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_removed_from_albums\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_email_template_content_changed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"event_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_intercom_user_hash\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"page_path\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_online\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_amount_of_words\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_order_amount\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_traits_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_conversion_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_status\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_review_notifications\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"page_title\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_page_path\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_system_notifications\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_error\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_closed_question_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_questions_and_answers_subscribed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_free_text_profanity\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_section\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_signup_employee_count\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_products_shown\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_step\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_configuration_action\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_meeting_time\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_dma_code\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_exception_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sidebar_open\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_insights_api_end_point\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_package_categories\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_pla\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_last_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_state_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_number_reviews\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_product_star_rating\",\"type\":\"double\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_from_product\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_post_words\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_email_template_subject_changed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"app_key\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_duration\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_timezone\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_developer_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_start_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_lpg_action_value\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_send_after\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_platform\",\"type\":\"string\",\"nullable\":',
    'spark.sql.create.version'='2.4.5',
    'spark.sql.sources.schema.part.8'='pdated_testimonial_link_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_imported_reviews\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldform_category\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_os_patch\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_using_packages_service\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"_metadata_bundled\",\"type\":{\"type\":\"array\",\"elementType\":\"string\",\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_title\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_social_publish_link\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_store_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_post_title_text_length\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_top_negative_period\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"product_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"review_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"sentence\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"message_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_ctabutton_text_check_box\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_action\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tsr_upload_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_total_errors\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_bottom_overall_conversion_of_searching_users\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"overall_conversion_of_searching_users\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_card_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_invited_user_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_domain_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_admin_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_album_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_category\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_email_template_key\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tag_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_image_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_activation_url\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_send_to_email_address\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_comment_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_lpg_action_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_negative_topics\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"mentions_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"rank\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"sentiment_score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"topic\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_image_ids\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"external_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_has_pos\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_mode',
    'spark.sql.sources.schema.part.7'='le\":true,\"metadata\":{}},{\"name\":\"properties_reviewer_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_app_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_widget_font\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"review_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_moderated_text_selected_albums\",\"type\":{\"type\":\"array\",\"elementType\":\"string\",\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_old_package_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_birthday_selected_points\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_package\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_sent_mas\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_badge\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_location\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_email_campaign_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_tsr\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_charge_price\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_comments\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_team_member_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_newsletter_subscribed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_include_product_photo\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_css_editor\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_promoted_products_title_check_box\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_existing_baseline_version\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_profanity_filter_selection\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_auto_publish_enabled\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_state\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_album_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_message_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_device_model\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_gross_margin\",\"type\":\"double\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_map_state\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_expiration_period_in_hours\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_promoted_products_widget\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_pct_reached\",\"type\":\"double\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_dedicated_page\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_picture_url\",\"type\":{\"type\":\"array\",\"elementType\":\"string\",\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_user_days_to_renewal\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_pixel_version\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_comments_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_visitors\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_downgrade_reason\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_filter_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_review_submission\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_primary_color_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_reviewer_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_meeting_duration\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_u',
    'spark.sql.sources.schema.part.14'='\"name\":\"properties_cta_is_open\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_subject\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_question_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_source_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_skip_email\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_error_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldutm_campaign_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_company_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"page_url\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_phone\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_sent_tpr\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_signature\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_month\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_summary\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_secondary_color_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_synced_gallery_enabled\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tag_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_orders_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_last_locked_feature\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_medium_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_status_filter_selection\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_phase_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_merchant_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_conversation_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_profanity_notification\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_admin_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_first_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_quick_filter_selection\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_auto_publish_enabled\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_qn_a\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_feed_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_post_frequency_check_box\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_num_of_points\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_admin_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_send_after_amount\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_purchase_selected_points\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_minimum_opinions\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_app_developer_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_top_positive_period\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"product_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"review_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"sentence\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_days_invalid_pinterest_token\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_metro_code\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_browser_family\",\"type\":\"string\",\"nullable',
    'spark.sql.sources.schema.part.15'='\":true,\"metadata\":{}},{\"name\":\"properties_is_has_promoted_products_email\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_products_count\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_order_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_page_title_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_credit_card_last4_digits\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_selecting_reviews\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_object_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_item_sentiment_score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_moderated_text_allow_remove_from_shoppable_instagram\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_user_agent\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_renewal_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_title\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"session_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"year\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"month\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"day\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"year\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"month\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"day\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}}]}',
    'spark.sql.sources.schema.part.12'='lean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_meeting_time_zone\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_automatic_frequency_drop_down\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_emails_attempted\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_orders\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_medium\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_baseline_version\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_first_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_csv_path\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_moderation_link\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_error_message\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_product_tag_missing\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_signature_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_layout\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_background_color_checkbox\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_device_family\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"received_at\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_view\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_feature\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"page_search\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_pending_rrs\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_charge_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_star_rating_color_check_box\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_gclid_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_pull_past_orders_enabled\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_old_instance_version\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_stars_color_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_contepowerreviewsnt\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_checked\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_results_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_positive_opinions_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_post_title_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_attributes_feedback\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_utm_campaign\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_link_expiration_period_in_hours\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_url_for_skipped\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_coupon_notification_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_ctabutton_color\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_end_anonymous_user_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_source_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_title\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_pays_via\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_google_spend\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_star_rating_color\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_classic_editor\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_campaign_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_u',
    'spark.sql.sources.schema.part.13'='pdated_header_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invited_user_store_restricted\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sentences\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_sent_site_reminder\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_created_at\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_content_type_filter_selection\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sub_status_filter_selection\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_min_star_rating\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_positive_reviews_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_watched_pct\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_library_version\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_amount_of_products_in_file\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_only_my_instagram_photos_check_box\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_blog_category\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_upload_button\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_multiple_products_max_emails_amount\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_product_url\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_reviewer_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldutm_medium_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_avg_distinct_queries_in_domain_key_products\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"avg_distinct_queries_in_domain_key\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_spam_filter_checkbox_checked\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_opinions\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_order_currency\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_view_by\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_alignment\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_product_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_library_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_star_rating\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_marketo_form_loaded\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_old_pacakge_monthly_price\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldsubscribedto_shopify_plus_email_course\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_to_product\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_page_title_check_box\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_integration_version\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_personal_info\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_country_code\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_gsr\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_instance_version\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_last_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_max_orders\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_os_minor\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_user_renewal_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{',
    'spark.sql.sources.schema.part.10'='ties_signup_monthly_orders_count\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_total_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_override_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_thirty_day_revenue_cents\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_account_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_email_templates_reset_confirmed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_cross_sell\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_customer_tab_clicked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_term\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_card_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_multi_product\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_os_major\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_positive_topics\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"mentions_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"rank\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"sentiment_score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"topic\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_topics_in_favorites_section_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_social_network\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_order_amount\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties__rrmonthly_limit\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_page_url\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_popup_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_traits_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_autoplay_speed\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_favorite_action\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_widget_visible\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_end_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_utm_term_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_negative_opinions_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_all_reviews\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_page_referrer\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_album_picture_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldform_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_cokuchcake20silicon20molden20silicon20form20tent\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_gallery_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_days_to_renewal\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_product_didnt_arrive_notification\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_users_count_limit_reached\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_gsr\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_agency\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_original_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_post_comments\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_current_app\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sentiment_value\",\"type\":\"double\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_link_to_testimonial_page_checkbox\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_package_i',
    'spark.sql.partitionProvider'='catalog',
    'spark.sql.sources.schema.part.11'='d\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_org_key\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_friend_discount\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_review_notifications_star3\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_instance_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_open_text_question_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_os_family\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_group_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_traits_plan\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_pictures_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_publish_everywhere_link\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_referrals_selected\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties__package_extensions\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_number_of_reviews\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_subscription_state\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_website\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldutm_source_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_dest_app\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_invalid_reason\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_multiple_products_review_request_logic\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_credit_card_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_number_of_reviews\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_country_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_longitude\",\"type\":\"float\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_creation_location\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_referral_code\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_emails_sent\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_insights_api_error\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_friend_tab_clicked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldhashtag\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_topics_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_org_admin_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_amount_of_products\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_page_search\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_coupons\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_yotpo_ip\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_negative_reviews_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_errors_file\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_receive_newsletters\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_marketo_form_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_system_notifications_subscribed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_gallery_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_review_notifications_star1\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_chargify_balance\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_email_template_content_save_succeeded\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_industry_average\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_sentiment_notification\",\"type\":\"boo',
    'spark.sql.sources.schema.part.2'='iewer_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_collection_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_media_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_breakdown_by\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_convert_to_site_review\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_title\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_days_in_dunning\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_cta_title\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_org_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sentiment_filter_selection\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_from_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_signup_utmterm\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_twitter_token_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties__locked_feature_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_body\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_order_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties__deleted_users\",\"type\":{\"type\":\"array\",\"elementType\":\"string\",\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_mkto_person_notes\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_content\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_thirty_day_order_volume\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_to_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_browser_major\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_post_author\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_cta_url\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_item_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_media_sub_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_reviews_widget_installed\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_next_charge_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_ctabutton_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_order_id\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_filter_location\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_tpr\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_star_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_last_conversion_order_time\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"event\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tpr_upload_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_failed_reviews\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_fieldreferrer_token\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_term\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_filter_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tag_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_region_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_multiple_products_interval\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_region\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_opinion_sentiment\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_mandatory_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_number_orders\",\"ty',
    'spark.sql.sources.schema.part.1'='perties_admin\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_locked_menu_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_sent_mai\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_account_selected_points\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_map_state\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_coupons\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_import_status\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_integration_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_end_user_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_postal_code\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_comment_body\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_picture_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_verified_file\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_store_domain\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"channel\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"event_sent_to_segment_at\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_media_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_first_invite\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_header_customization_checkbox\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_facebook_token_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_link_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_reviewer_first_letter\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_days_invalid_facebook_token\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is2_stars_checked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_days_invalid_twitter_token\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_clicked_update_npsscore\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_neutral_opinions_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_yotpo_product_score_v2\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_cokuchen20silicon20form20tent\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_url_for_verified\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_chargify_revenue\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_interaction_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_email_template_subject_save_succeeded\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sentiment_change\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_widget_font_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_subject\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_invited_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"is_out_of_date_range\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_stars_color\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_role\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_integration_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_first_album\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_campaign_sq\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_product_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_added_to_albums\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_name_on_credit_card\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_rev',
    'spark.sql.sources.schema.part.4'='e\":\"properties_tab_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_latitude\",\"type\":\"float\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_phone\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_total_search_generated_purchases_products\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"total_search_generated_purchases\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_keyword\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_phase\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_ad_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_ad_network\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_submission\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_body_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_reviews_carousel\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_custom_reviews\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_product_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_platform\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_text_size\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_maps\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_recurring_payment_interval\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_top_overall_conversion_of_searching_users\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"overall_conversion_of_searching_users\",\"type\":\"double\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_hashtag_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_moderation_action\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_video_host\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_products_app_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_billing_provider\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"original_timestamp\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_download_link\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_total_searches_in_domain_key_products\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"total_searches_in_domain_key\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_referrer\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_url_for_errors\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_cta_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_segment_id_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_moderation_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_twitter_token\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_date_range\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_syndicated_inherit\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_shopify_plan\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_review_product_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_show_navigation_arrows_checkbox\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_social_push\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_cta_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_send_',
    'spark.sql.sources.schema.part.3'='pe\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tag_location\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_item_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_customer_points\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_batch_action\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_platform_plan\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_promoted_products_email\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_email_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_map\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_uninstall_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_report_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_review_notifications_star4\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_reviews_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_campaign_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"page_referrer\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_campaign_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is1_star_checked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_signup_utmsource\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_button_clicked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_send_after_amount\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_user_plan_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_sent_map\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_product_enablement\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sorting_content\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_failure_reason\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"context_page_title\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_enabled_custom_reviews\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_body\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_browser_patch\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_receive_review_notifications_star5\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_email_template_version_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_new_package_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_user_agent_browser_minor\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_ui_version\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_star_rating_filter_selection\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_subject_updated\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_signup_utmcampaign\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_product_with_reviews_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is4_stars_checked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_email_templates_reset_succeeded\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_signup_utmcontent\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_failure_message\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_agent_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_testimonial_link_url\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"nam',
    'spark.sql.sources.schema.numPartCols'='3',
    'spark.sql.sources.schema.part.0'='{\"type\":\"struct\",\"fields\":[{\"name\":\"valid_event_for_session\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"segment_user_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_area_code\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_end_user_email\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_tag_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_old_state\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_topics_in_all_others_section_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_sentiment_score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_media_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_city\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_filter_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_team_member_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"parsed_ip_country_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_install_order_volume\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"event_created_at\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_card_header\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_invalid_pinterest_token\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_phase\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_search_medium\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_reviews_tab\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_error_text\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is_has_star_rating\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_is3_stars_checked\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_old_plarform\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_lead_type_c\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_feature_update_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_signature\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_background_color\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_anonymized_email_count\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"_metadata_unbundled\",\"type\":{\"type\":\"array\",\"elementType\":\"string\",\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"days_from_purchase_changed\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_topics_shown\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_url\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_post_published\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_form_field_lead_source\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_attributes_score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_top_positive_sentences\",\"type\":{\"type\":\"array\",\"elementType\":{\"type\":\"struct\",\"fields\":[{\"name\":\"product_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"review_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"score\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"sentence\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]},\"containsNull\":true},\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_end_user_id\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_year\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_moderated_text_is_product_album\",\"type\":\"boolean\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_plan_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_header_text_color\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"properties_updated_reviews_type\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"pro',
    'spark.sql.sources.schema.numParts'='16',
    'spark.sql.sources.provider'='parquet')''' %  DB)

            # Without flag and schema inference, we get the dummy cols and partition cols
            ds = conn.list_datasets(DB, name='fact_segment_events_last')
            self.assertEqual(5, len(ds[0].schema.cols))

            # Alter to enable schema inference
            conn.execute_ddl('''
                alter table %s.fact_segment_events_last
                set tblproperties('okera.spark-table.infer-schema'='true')''' % DB)
            ds = conn.list_datasets(DB, name='fact_segment_events_last')
            self.assertEqual(733, len(ds[0].schema.cols))

            # Add some attributes
            conn.delete_attribute('yotpo_perf_test', 'email')
            conn.create_attribute('yotpo_perf_test', 'email')
            conn.delete_attribute('yotpo_perf_test', 'dummy_tag')
            conn.create_attribute('yotpo_perf_test', 'dummy_tag')
            conn.assign_attribute('yotpo_perf_test', 'email', DB,
                                  'fact_segment_events_last',
                                  'properties_send_to_email_address')
            conn.assign_attribute('yotpo_perf_test', 'email', DB,
                                  'fact_segment_events_last', 'properties_traits_email')
            conn.assign_attribute('yotpo_perf_test', 'email', DB,
                                  'fact_segment_events_last', 'properties_email')
            conn.assign_attribute('yotpo_perf_test', 'email', DB,
                                  'fact_segment_events_last', 'properties_reviewer_email')
            conn.execute_ddl('DROP ROLE IF EXISTS %s' % TEST_ROLE)
            conn.execute_ddl('CREATE ROLE %s' % TEST_ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE, TEST_USER))
            conn.execute_ddl(('GRANT SELECT ON DATABASE %s ' +
                              'TRANSFORM yotpo_perf_test.email WITH sha2() ' +
                              'TO ROLE %s') % (DB, TEST_ROLE))

            def admin_auth():
              return self.authorize_table(
                  conn, DB, 'fact_segment_events_last',
                  use_tmp_tables=True)
            def user_auth():
              return self.authorize_table(
                  conn, DB, 'fact_segment_events_last', user=TEST_USER,
                  use_tmp_tables=True)

            self.assertEqual('*', admin_auth())
            self.assertTrue('sha2' in user_auth())

            PERF.measure(admin_auth, 'yotpo-sparse-tags', 'admin', 'authorize_query')
            PERF.measure(user_auth, 'yotpo-sparse-tags', 'TEST_USER', 'authorize_query')

            # Add an unused tag to all columns
            ds = conn.list_datasets(DB, name='fact_segment_events_last')[0]
            for col in ds.schema.cols:
                if col.name:
                    conn.assign_attribute('yotpo_perf_test', 'dummy_tag', DB,
                                          'fact_segment_events_last', col.name)
            PERF.measure(admin_auth, 'yotpo-medium-tags', 'admin', 'authorize_query')
            PERF.measure(user_auth, 'yotpo-medium-tags', 'TEST_USER', 'authorize_query')


    @unittest.skipIf(not PERF.run_perf(), "Skipping perf tests")
    @pytest.mark.perf
    def test_yotpo_perf(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.delete_attribute('yotpo_perf_test', 'dummy_tag')
            conn.create_attribute('yotpo_perf_test', 'dummy_tag')

            def admin_auth():
              return self.authorize_table(conn, 'dbx_part_db', 'fact_segment_events_last')
            def user_auth():
              return self.authorize_table(
                  conn, 'dbx_part_db', 'fact_segment_events_last', user=TEST_USER)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % ('dbx_part_role', TEST_USER))
            self.assertEqual('*', admin_auth())
            self.assertTrue('sha2' in user_auth())

            PERF.measure(admin_auth, 'yotpo-sparse-tags2', 'admin', 'authorize_query')
            PERF.measure(user_auth, 'yotpo-sparse-tags2', 'TEST_USER', 'authorize_query')

            # Add an unused tag to all columns
            ds = conn.list_datasets('dbx_part_db', name='fact_segment_events_last')[0]
            for col in ds.schema.cols:
                if col.name:
                    conn.assign_attribute('yotpo_perf_test', 'dummy_tag', 'dbx_part_db',
                                          'fact_segment_events_last', col.name)
            PERF.measure(admin_auth, 'yotpo-medium-tags2', 'admin', 'authorize_query')
            PERF.measure(user_auth, 'yotpo-medium-tags2', 'TEST_USER', 'authorize_query')

    def test_authorize_query_struct(self):
        db = "authorize_query_struct_db"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_db(conn, db)
            self._recreate_test_role(conn, 'authorize_query_struct_role', ['authorize_query_struct_user'])
            conn.execute_ddl("CREATE ATTRIBUTE IF NOT EXISTS test.string_col")
            conn.execute_ddl("""CREATE TABLE %s.t(
                id STRING ATTRIBUTE test.string_col,
                s1 STRUCT <f1: STRING, f2: BIGINT>)""" % db)
            conn.execute_ddl(
                """GRANT SELECT ON DATABASE %s TRANSFORM test.string_col
                WITH mask() TO ROLE %s""" % (db, 'authorize_query_struct_role'))
            self.assertEqual(
                "SELECT mask(id) as id, s1 FROM authorize_query_struct_db.t",
                self.authorize_query(conn, "SELECT * FROM %s.t" % db,
                                     'authorize_query_struct_user', False,
                                     return_full_result=True))

if __name__ == "__main__":
    unittest.main()
