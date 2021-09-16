# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for Presto in PyOkera
#
# pylint: disable=broad-except
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals
# pylint: disable=bad-continuation
# pylint: disable=broad-except

import os
from datetime import datetime

import pytest

import pytz
import requests
import urllib3
import prestodb

from okera import context
from okera.tests import pycerebro_test_common as common

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_PRESTO_HOST = os.environ['ODAS_TEST_HOST']
DEFAULT_PRESTO_PORT = int(os.environ['ODAS_TEST_PORT_PRESTO_COORD_HTTPS'])
DEFAULT_PLANNER_PORT = int(os.environ['ODAS_TEST_PORT_PLANNER_THRIFT'])
BAD_PRESTO_PORT = 1234

@pytest.mark.filterwarnings('ignore::urllib3.exceptions.InsecureRequestWarning')
@pytest.mark.filterwarnings('ignore:numpy.dtype size changed')
class PrestoTest(common.TestBase):

    def _connect_presto_with_session_props(self, props):
        user = 'root'
        return prestodb.dbapi.connect(
            host=DEFAULT_PRESTO_HOST,
            port=DEFAULT_PRESTO_PORT,
            user=user,
            catalog='okera',
            http_scheme="https",
            auth=prestodb.auth.BasicAuthentication(user, user),
            isolation_level=prestodb.transaction.IsolationLevel.READ_UNCOMMITTED,
            session_properties=props
        )

    def _close_presto_connection(self, conn, cursor):
        if cursor:
            cursor.cancel()
        if conn:
            conn.close()

    def test_basic(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('select * from okera_sample.whoami',
                                        dialect='presto')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_auto_choose_dialect(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('select * from okera_sample.whoami')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_presto_disabled_auto_choose_dialect(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            results = conn.scan_as_json('select * from okera_sample.whoami')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_presto_disabled_presto_dialect(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            with pytest.raises(ValueError):
                conn.scan_as_json('select * from okera_sample.whoami',
                                  dialect='presto')

    def test_presto_enabled_okera_dialect(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('select * from okera_sample.whoami',
                                        dialect='okera')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_bad_presto_connection(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with ctx.connect(host=DEFAULT_PRESTO_HOST, port=DEFAULT_PLANNER_PORT,
                         presto_host=DEFAULT_PRESTO_HOST,
                         presto_port=BAD_PRESTO_PORT) as conn:
            with pytest.raises(requests.exceptions.ConnectionError):
                conn.scan_as_json('select * from okera_sample.whoami',
                                  dialect='presto')

    def test_presto_ctx_namespace(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('select * from okera_sample.whoami',
                                        dialect='presto')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_presto_ctx_bad_namespace(self):
        ctx = common.get_test_context(namespace='okera2')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            with pytest.raises(prestodb.exceptions.PrestoUserError):
                conn.scan_as_json('select * from okera_sample.whoami',
                                  dialect='presto')

    def test_presto_conn_namespace(self):
        ctx = common.get_test_context(namespace='okera_bad')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT,
                                namespace='okera') as conn:
            results = conn.scan_as_json('select * from okera_sample.whoami',
                                        dialect='presto')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_presto_conn_bad_namespace(self):
        ctx = common.get_test_context(namespace='okera_bad')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT,
                                namespace='okera2') as conn:
            with pytest.raises(prestodb.exceptions.PrestoUserError):
                conn.scan_as_json('select * from okera_sample.whoami',
                                  dialect='presto')

    def test_max_records(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json(
                'select * from okera_sample.users', dialect='presto', max_records=100)
            self.assertEqual(len(results), 100)
            results = conn.scan_as_pandas(
                'select * from okera_sample.users', dialect='presto', max_records=100)
            self.assertEqual(len(results), 100)

    def test_max_records_with_less_records(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('select * from okera_sample.users limit 50',
                                        dialect='presto', max_records=100)
            self.assertEqual(len(results), 50)
            results = conn.scan_as_pandas('select * from okera_sample.users limit 50',
                                          dialect='presto', max_records=100)
            self.assertEqual(len(results), 50)

    def test_json_pandas_equality(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            json_results = conn.scan_as_json('select * from okera_sample.users limit 50',
                                             dialect='presto', max_records=100)
            pandas_results = conn.scan_as_pandas(
                'select * from okera_sample.users limit 50',
                dialect='presto', max_records=100)
            self.assertEqual(json_results, pandas_results.to_dict('records'))

    def test_no_auth(self):
        ctx = context() # use default to ensure no auth
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            with pytest.raises(RuntimeError):
                conn.scan_as_json('select * from okera_sample.whoami',
                                  dialect='presto')

    def test_ctx_dialect(self):
        ctx = common.get_test_context(dialect='okera')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('okera_sample.whoami')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_ctx_dialect_override(self):
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('okera_sample.whoami', dialect='okera')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'root')

    def test_complex_types(self):
        datasets = [
            'rs_complex.struct_t',
            'rs_complex.multiple_structs_nested',
            'rs_complex.map_t',
            'rs_complex.struct_nested',
            'rs_complex_parquet.map_struct_t',
            'rs_complex_parquet.map_struct_array_t',
        ]
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            for dataset in datasets:
                presto_results = conn.scan_as_json(
                    'select * from %s' % dataset, dialect='presto')
                okera_results = conn.scan_as_json(
                    'select * from %s' % dataset, dialect='okera', strings_as_utf8=True)
                self.assertEqual(okera_results, presto_results)

    def test_external_view(self):
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            conn.execute_ddl("create view if not exists default.external_view as select" +
                             " `role_name` from okera_system.role_names;")
            conn.execute_ddl("ALTER TABLE default.external_view SET TBLPROPERTIES" +
                             " ('cerebro.external.view'='true');")
            conn.execute_ddl("grant select on database default to okera_public_role;")

        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json("select * from default.external_view")
            self.assertTrue("role_name" in str(results), results)

        ctx.enable_token_auth(token_str='some_test_user')
        caught = None
        expected = "Unknown dataset: okera_system.role_names"
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            try:
                results = conn.scan_as_json("select * from default.external_view")
            except Exception as e:
                if expected not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True
            if (not caught):
                self.fail("No exception raised, expected TRecordServiceException")

    def verify_allowed_view_auth_sql(self, user, sql):
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str=user)
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            try:
                results = conn.scan_as_json(sql)
                self.assertTrue(results is not None)
            except Exception as e:
                self.fail("Fail to verify auth for user: " + user + " for sql: " + sql
                            + " due to Exception: " + str(e))

    def verify_restricted_view_auth_sql(self, user, expected, sql):
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str=user)
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            caught = None
            try:
                results = conn.scan_as_json(sql)
                assert(results)
            except Exception as e:
                if expected not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True
            if (not caught):
                self.fail(
                    "No exception raised, expected TRecordServiceException for user: " +
                    user + ", for sql: " + sql)

    def test_complex_type_view_auth(self):
        ## verify complex_type where clause auth
        where_qry = """select currency from chase.subscription_view
            where subscriptionkey = 'e23c82e3-10fd-40f3-ba59-5959a82ad3c8'"""
        ## verify complex_type Join clause auth
        join_query = """select a.currency from chase.subscription_view a
             join chase.subscription_view b
             ON (a.subscriptionkey = b.subscriptionkey)"""
        ## verify complex_type GROUP BY clause auth
        group_by_query = """select MAX(accountnumber), productkey
            from chase.subscription_view GROUP BY productkey"""
        ## verify complex_type UNION ALL clause auth
        union_all_query = """select count(*) from chase.subscription_view
            WHERE subscriptionkey='e23c82e3-10fd-40f3-ba59-5959a82ad3c8'
            UNION ALL select count(*) from chase.subscription_view
            WHERE subscriptionkey='e23c82e3-10fd-40f3-ba59-5959a82ad3c8'"""

        ## Run tests as 'root' user
        user = 'root'
        self.verify_allowed_view_auth_sql(user, where_qry)
        self.verify_allowed_view_auth_sql(user, join_query)
        self.verify_allowed_view_auth_sql(user, group_by_query)
        self.verify_allowed_view_auth_sql(user, union_all_query)

        ## Run some tests as 'testuser' user
        user = 'testuser'
        self.verify_allowed_view_auth_sql(user,
            "select * from chase.subscription_currency")
        self.verify_allowed_view_auth_sql(user,
            "select currency from chase.subscription_currency")
        self.verify_allowed_view_auth_sql(user,
            "select count(*) from chase.subscription_view " +
            "WHERE currency.currencycode='GBP'")
        allowed_union_all_query = """select count(*) from chase.subscription_view
            WHERE currency.currencycode='GBP'
            UNION ALL select count(*) from chase.subscription_view
            WHERE currency.currencycode='GBP'"""
        self.verify_allowed_view_auth_sql(user, allowed_union_all_query)

        self.verify_restricted_view_auth_sql(
            'testuser', "Column 'subscriptionkey' cannot be resolved", where_qry)
        self.verify_restricted_view_auth_sql(
            'testuser', "Column 'a.subscriptionkey' cannot be resolved", join_query)
        self.verify_restricted_view_auth_sql(
            'testuser', "Column 'accountnumber' cannot be resolved", group_by_query)
        self.verify_restricted_view_auth_sql(
            'testuser', "Column 'subscriptionkey' cannot be resolved", union_all_query)

    def test_auth_primitive_type_dataset(self):
        ## Regular SELECT queries on primitive datasets
        ## A "select_col" here means selective columns from the table/view
        select_queries = [
            """select * from authdb.alltypes_s3""",
            """select * from authdb.alltypes_s3_view""",
            """select * from authdb.alltypes_s3_sel_view""",
            """select * from authdb.alltypes_s3_view_on_view""",
            """select * from authdb.alltypes_s3_sel_view_on_sel_view""",
            """select * from authdb.alltypes_s3_full_view_on_sel_view""",
            """select * from authdb.alltypes_s3_where_clause_view""",
            """select * from authdb.alltypes_s3_join_clause_view""",
            """select int_col, string_col from authdb.alltypes_s3""",
            """select int_col from authdb.alltypes_s3_view""",
            """select int_col from authdb.alltypes_s3_sel_view""",
            """select int_col from authdb.alltypes_s3_view_on_view""",
            """select int_col from authdb.alltypes_s3_sel_view_on_sel_view""",
            """select int_col from authdb.alltypes_s3_full_view_on_sel_view""",
            """select int_col from authdb.alltypes_s3_where_clause_view""",
            """select int_col from authdb.alltypes_s3_join_clause_view""",
        ]

        ## Queries used to check column level restrictions
        ## These will only error out for 'testuser'/'noadmin' users,
        ## so DO NOT run for other users
        select_col_level_restrict_queries = [
            """select decimal_col from authdb.alltypes_s3""",
            """select decimal_col, double_col from authdb.alltypes_s3_view""",
            """select decimal_col from authdb.alltypes_s3_sel_view""",
            """select decimal_col from authdb.alltypes_s3_view_on_view""",
            """select decimal_col from authdb.alltypes_s3_sel_view_on_sel_view""",
            """select decimal_col from authdb.alltypes_s3_full_view_on_sel_view""",
            """select decimal_col from authdb.alltypes_s3_where_clause_view""",
            """select decimal_col from authdb.alltypes_s3_join_clause_view""",
        ]

        ## Run tests as 'root' user
        user = 'root'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Run tests as 'noadmin' user
        user = 'noadmin'
        expected = "User 'noadmin' does not have privileges to access: authdb.*"
        for query in select_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

        ## Run tests as 'selectall' user (allowed has SELECT ON CATALOG ACCESS)
        user = 'selectall'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Test for column level permissions
        ## Step 1: Run tests as 'testuser' user for allowed columns
        user = 'testuser'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Step 2: Run tests as 'testuser' user for restricted columns
        user = 'testuser'
        expected = "Column 'decimal_col' cannot be resolved"
        for query in select_col_level_restrict_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

    def test_auth_struct_type_dataset(self):
        ## Regular SELECT queries on struct_type datasets
        ## A "select_col" here means selective columns from the table/view
        select_queries = [
            """select * from authdb.struct_t""",
            """select * from authdb.struct_t_view""",
            """select * from authdb.struct_t_sel_view""",
            """select * from authdb.struct_t_view_on_view""",
            """select * from authdb.struct_t_sel_view_on_sel_view""",
            """select * from authdb.struct_t_full_view_on_sel_view""",
            """select * from authdb.struct_t_where_clause_view""",
            """select * from authdb.struct_t_join_clause_view""",
            """select id from authdb.struct_t""",
            """select id from authdb.struct_t_view""",
            """select id from authdb.struct_t_sel_view""",
            """select id from authdb.struct_t_view_on_view""",
            """select id from authdb.struct_t_sel_view_on_sel_view""",
            """select id from authdb.struct_t_full_view_on_sel_view""",
            """select id from authdb.struct_t_where_clause_view""",
            """select id from authdb.struct_t_join_clause_view""",
        ]

        ## Queries used to check column level restrictions
        ## These will only error out for 'testuser'/'noadmin' users
        select_col_level_restrict_queries = [
            """select s1 from authdb.struct_t""",
            """select s1 from authdb.struct_t_view""",
            """select s1 from authdb.struct_t_sel_view""",
            """select s1 from authdb.struct_t_view_on_view""",
            """select s1 from authdb.struct_t_sel_view_on_sel_view""",
            """select s1 from authdb.struct_t_full_view_on_sel_view""",
            """select s1 from authdb.struct_t_where_clause_view""",
            """select s1 from authdb.struct_t_join_clause_view""",
        ]

        ## Run tests as 'root' user
        user = 'root'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Run tests as 'noadmin' user
        user = 'noadmin'
        expected = "User 'noadmin' does not have privileges to access: authdb.*"
        for query in select_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

        ## Run tests as 'selectall' user (allowed has SELECT ON CATALOG ACCESS)
        user = 'selectall'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Test for column level permissions
        ## Step 1: Run tests as 'testuser' user for allowed columns
        user = 'testuser'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Step 2: Run tests as 'testuser' user for restricted columns
        user = 'testuser'
        expected = "Column 's1' cannot be resolved"
        for query in select_col_level_restrict_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

    def test_auth_struct_type_complex_type_access_dataset(self):
        ## Regular SELECT queries on struct_type datasets
        ## A "select_col" here means selective columns from the table/view
        select_queries = [
            """select * from authdb.struct_t""",
            """select * from authdb.struct_t_view""",
            """select * from authdb.struct_t_sel_complex_view""",
            """select * from authdb.struct_t_view_on_view""",
            """select * from authdb.struct_t_sel_view_on_sel_complex_view""",
            """select * from authdb.struct_t_full_view_on_sel_complex_view""",
            """select * from authdb.struct_t_where_clause_view""",
            """select * from authdb.struct_t_join_clause_view""",
            """select s1 from authdb.struct_t""",
            """select s1 from authdb.struct_t_view""",
            """select s1 from authdb.struct_t_sel_complex_view""",
            """select s1 from authdb.struct_t_view_on_view""",
            """select s1 from authdb.struct_t_sel_view_on_sel_complex_view""",
            """select s1 from authdb.struct_t_full_view_on_sel_complex_view""",
            """select s1 from authdb.struct_t_where_clause_view""",
            """select s1 from authdb.struct_t_join_clause_view""",
        ]

        ## Queries used to check column level restrictions
        ## These will only error out for 'complex' users
        select_col_level_restrict_queries = [
            """select id from authdb.struct_t""",
            """select id from authdb.struct_t_view""",
            """select id from authdb.struct_t_sel_complex_view""",
            """select id from authdb.struct_t_view_on_view""",
            """select id from authdb.struct_t_sel_view_on_sel_complex_view""",
            """select id from authdb.struct_t_full_view_on_sel_complex_view""",
            """select id from authdb.struct_t_where_clause_view""",
            """select id from authdb.struct_t_join_clause_view""",
        ]

        ## Test for column level permissions
        ## Step 1: Run tests as 'complex' user for allowed columns
        user = 'complex'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Step 2: Run tests as 'complex' user for restricted columns
        user = 'complex'
        expected = "Column 'id' cannot be resolved"
        for query in select_col_level_restrict_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)


    def test_auth_map_type_dataset(self):
        ## Regular SELECT queries on map type datasets
        ## A "select_col" here means selective columns from the table/view
        select_queries = [
            """select * from authdb.map_t""",
            """select * from authdb.map_t_view""",
            """select * from authdb.map_t_sel_view""",
            """select * from authdb.map_t_view_on_view""",
            """select * from authdb.map_t_sel_view_on_sel_view""",
            """select * from authdb.map_t_full_view_on_sel_view""",
            """select * from authdb.map_t_where_clause_view""",
            """select * from authdb.map_t_join_clause_view""",
            """select str_map from authdb.map_t""",
            """select str_map from authdb.map_t_view""",
            """select str_map from authdb.map_t_sel_view""",
            """select str_map from authdb.map_t_view_on_view""",
            """select str_map from authdb.map_t_sel_view_on_sel_view""",
            """select str_map from authdb.map_t_full_view_on_sel_view""",
            """select str_map from authdb.map_t_where_clause_view""",
            """select str_map from authdb.map_t_join_clause_view""",
        ]

        ## Queries used to check column level restrictions
        ## These will only error out for 'testuser'/'noadmin' users,
        ## so DO NOT run for other users
        select_col_level_restrict_queries = [
            """select id from authdb.map_t""",
            """select id from authdb.map_t_view""",
            """select id from authdb.map_t_sel_view""",
            """select id from authdb.map_t_view_on_view""",
            """select id from authdb.map_t_sel_view_on_sel_view""",
            """select id from authdb.map_t_full_view_on_sel_view""",
            """select id from authdb.map_t_where_clause_view""",
            """select id from authdb.map_t_join_clause_view""",
        ]

        ## Run tests as 'root' user
        user = 'root'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Run tests as 'noadmin' user
        user = 'noadmin'
        expected = "User 'noadmin' does not have privileges to access: authdb.*"
        for query in select_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

        ## Run tests as 'selectall' user (allowed has SELECT ON CATALOG ACCESS)
        user = 'selectall'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Test for column level permissions
        ## Step 1: Run tests as 'testuser' user for allowed columns
        user = 'testuser'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Step 2: Run tests as 'testuser' user for restricted columns
        user = 'testuser'
        expected = "Column 'id' cannot be resolved"
        for query in select_col_level_restrict_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

    def test_auth_array_type_dataset(self):
        ## Regular SELECT queries on map type datasets
        ## A "select_col" here means selective columns from the table/view
        select_queries = [
            """select * from authdb.strarray_t""",
            """select * from authdb.strarray_t_view""",
            """select * from authdb.strarray_t_sel_view""",
            """select * from authdb.strarray_t_view_on_view""",
            """select * from authdb.strarray_t_sel_view_on_sel_view""",
            """select * from authdb.strarray_t_full_view_on_sel_view""",
            """select * from authdb.strarray_t_where_clause_view""",
            """select * from authdb.strarray_t_join_clause_view""",
            """select str_arr from authdb.strarray_t""",
            """select str_arr from authdb.strarray_t_view""",
            """select str_arr from authdb.strarray_t_sel_view""",
            """select str_arr from authdb.strarray_t_view_on_view""",
            """select str_arr from authdb.strarray_t_sel_view_on_sel_view""",
            """select str_arr from authdb.strarray_t_full_view_on_sel_view""",
            """select str_arr from authdb.strarray_t_where_clause_view""",
            """select str_arr from authdb.strarray_t_join_clause_view""",
        ]

        ## Queries used to check column level restrictions
        ## These will only error out for 'testuser'/'noadmin' users,
        ## so DO NOT run for other users
        select_col_level_restrict_queries = [
            """select id from authdb.strarray_t""",
            """select id from authdb.strarray_t_view""",
            """select id from authdb.strarray_t_sel_view""",
            """select id from authdb.strarray_t_view_on_view""",
            """select id from authdb.strarray_t_sel_view_on_sel_view""",
            """select id from authdb.strarray_t_full_view_on_sel_view""",
            """select id from authdb.strarray_t_where_clause_view""",
            """select id from authdb.strarray_t_join_clause_view""",
        ]

        ## Run tests as 'root' user
        user = 'root'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Run tests as 'noadmin' user
        user = 'noadmin'
        expected = "User 'noadmin' does not have privileges to access: authdb.*"
        for query in select_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

        ## Run tests as 'selectall' user (allowed has SELECT ON CATALOG ACCESS)
        user = 'selectall'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Test for column level permissions
        ## Step 1: Run tests as 'testuser' user for allowed columns
        user = 'testuser'
        for query in select_queries:
            self.verify_allowed_view_auth_sql(user, query)

        ## Step 2: Run tests as 'testuser' user for restricted columns
        user = 'testuser'
        expected = "Column 'id' cannot be resolved"
        for query in select_col_level_restrict_queries:
            self.verify_restricted_view_auth_sql(user, expected, query)

    def test_default_timezone(self):
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('select current_timezone() as tz')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['tz'], 'UTC')

    def test_no_timezone(self):
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            results = conn.scan_as_json('select current_timezone() as tz')
            self.assertEqual(len(results), 1)
            # Presto defaults to America/Los_Angeles assuming no configuration
            # has changed that. If that changes, this test will need changing
            # asw ell.
            self.assertEqual(results[0]['tz'], 'UTC')

    # pylint: disable=protected-access
    # is_std() is short for 'is standard time timezone'
    def is_std(self, timezone="UTC"):
        dt = datetime.utcnow()
        timezone = pytz.timezone(timezone)
        timezone_aware_date = timezone.localize(dt, is_dst=None)
        return timezone_aware_date.tzinfo._dst.seconds != 0
    # pylint: enable=protected-access

    def test_specific_timezones(self):
        tzs = [
            ('Asia/Calcutta', '+05:30'),
            ('America/New_York', '-04:00' if self.is_std('America/New_York')
                                          else '-05:00'),
            ('America/Los_Angeles', '-07:00' if self.is_std('America/Los_Angeles')
                                             else '-08:00'),
            ('Asia/Jerusalem', '+03:00' if self.is_std('Asia/Jerusalem')
                                        else '+02:00'),
        ]
        for tz in tzs:
            tz_name = tz[0]
            tz_offset = tz[1]
            ctx = common.get_test_context(dialect='presto', tz=pytz.timezone(tz_name))
            ctx.enable_token_auth(token_str='root')
            with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
                results = conn.scan_as_json('select current_timezone() as tz')
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['tz'], tz_offset)

    # pylint: disable=protected-access
    def test_sample_and_limit_setting_via_session_props(self):
        # Verify that session properties allow to limit the out put of the presto queries.
        query_1_all_rows_length = 38455
        query_2_all_rows_length = 12
        sampling_value = 100
        expected_sampled_output_length = 3
        limit = 100
        test_query1 = 'select * from okera_sample.users'
        test_query2 = 'select * from partdb.ymdata2'
        test_query3 = 'select * from nytaxi.parquet_data'
        session_properties = {
            'okera.limit': limit,
            'okera.sampling_value': sampling_value
        }
        # first we set a connection without session properties
        # and check that we get all rows
        conn = self._connect_presto_with_session_props({})
        conn._http_session.verify = False
        cursor = conn.cursor()
        cursor.execute(test_query1)
        rows = cursor.fetchall()
        self.assertEqual(len(rows), query_1_all_rows_length)

        cursor.execute(test_query2)
        rows = cursor.fetchall()
        self.assertEqual(len(rows), query_2_all_rows_length)

        self._close_presto_connection(conn, cursor)

        # then we query the dataset that is essentially one file, so sampling_value
        # won't work but limit will
        # and check that output results were truncated according to limit
        conn = self._connect_presto_with_session_props(session_properties)
        conn._http_session.verify = False
        cursor = conn.cursor()
        cursor.execute(test_query1)
        rows = cursor.fetchall()
        self.assertEqual(len(rows), limit)

        # then we query the partitioned dataset so now the sampling_value will be
        # used rather than the limit.
        # It should restrict the output per file read to number of bytes specified
        cursor.execute(test_query2)
        rows = cursor.fetchall()
        self.assertEqual(len(rows), expected_sampled_output_length)
        self._close_presto_connection(conn, cursor)

        # then we query the big dataset to test both props
        # the query would hang normally without limit
        # the query should return sampled result
        with_limit_and_sampling_row_length = 700

        conn = self._connect_presto_with_session_props(session_properties)
        conn._http_session.verify = False
        cursor = conn.cursor()

        cursor.execute(test_query3)
        rows = cursor.fetchall()
        self.assertTrue(len(rows) <= with_limit_and_sampling_row_length)

        self._close_presto_connection(conn, cursor)

    # Only the first row in the result is verified.
    def verify_query(self, user, sql, expected_row):
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str=user)
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            try:
                results = conn.scan_as_json(sql)
                self.assertTrue(results is not None)
                self.assertEqual(results, expected_row)
            except Exception as e:
                self.fail("Fail to verify results for user: " + user + " for sql: " + sql
                            + " due to Exception: " + str(e))

    def test_show_schemas(self):
        # verify database exists as root
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            results = conn.execute_ddl("show databases like 'rs_complex'")
        expected = [["rs_complex"]]
        self.assertEqual(results, expected)

        # verify database is NOT found as 'analyst'
        ctx.enable_token_auth(token_str='analyst')
        with common.get_planner(ctx) as conn:
            results = conn.execute_ddl("show databases like 'rs_complex'")
        expected = [["rs_complex"]]
        self.assertNotEqual(results, expected)

    def test_transform(self):
        # verify query as analyst
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            # grant privilege
            conn.execute_ddl("DROP ROLE IF EXISTS presto_view_role")
            conn.execute_ddl("CREATE ROLE presto_view_role")
            conn.execute_ddl("GRANT ROLE presto_view_role TO GROUP analyst")
            conn.execute_ddl("GRANT SELECT ON DATABASE abac_db " +
                             "HAVING attribute in " +
                             "(pii.ip_address, pii.email_address, pii.credit_card) " +
                             "TRANSFORM pii.email_address WITH tokenize() " +
                             "TRANSFORM pii.credit_card WITH mask_ccn() " +
                             "TO ROLE presto_view_role")
        user = 'analyst'
        sql = "SELECT * FROM okera.abac_db.user_account_data " +\
              "WHERE ipv4_address = '82.229.123.72'"

        expected_row = [{'ipv6_address': '7553:abe3:ca2f:9ac3:42b5:4f3b:7a46:9d52',
                     'email': 'Vafcw@yrpq.ryi',
                     'ipv4_address': '82.229.123.72',
                     'creditcardnumber': 'XXXXXXXXXXXXXXX3020'}]
        self.verify_query(user, sql, expected_row)

        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            # revoke privilege
            conn.execute_ddl("REVOKE SELECT ON DATABASE abac_db " +
                             "HAVING attribute in " +
                             "(pii.ip_address, pii.email_address, pii.credit_card) " +
                             "TRANSFORM pii.email_address WITH tokenize() " +
                             "TRANSFORM pii.credit_card WITH mask_ccn() " +
                             "FROM ROLE presto_view_role")

    def test_decimal(self):
        sql = "SELECT sum(cs_sales_price) FROM okera.tpcds1_unpartitioned.catalog_sales"
        expected_row = [{'_col0': '72371322.53'}]
        self.verify_query('root', sql, expected_row)

    def test_cte_view(self):
        # verify external view with non-ODAS sql
        # executed by analyst user in presto
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            # grant privilege
            conn.execute_ddl("DROP ROLE IF EXISTS presto_view_role")
            conn.execute_ddl("CREATE ROLE presto_view_role")
            conn.execute_ddl("GRANT ROLE presto_view_role TO GROUP analyst")
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS chase_pii.money")
            conn.execute_ddl("CREATE ATTRIBUTE chase_pii.money")
            conn.execute_ddl("ALTER TABLE chase.ledger_balance " +\
                             "ADD COLUMN ATTRIBUTE " +\
                             "posted_balance chase_pii.money")
            conn.execute_ddl("ALTER TABLE chase.ledger_balance " +\
                             "ADD COLUMN ATTRIBUTE " +\
                             "available_balance chase_pii.money")
            conn.execute_ddl("GRANT SELECT ON DATABASE chase " +\
                             "TRANSFORM chase_pii.money WITH tokenize() " +\
                             "TO ROLE presto_view_role")

        user = 'analyst'
        sql = "select * from okera.chase.cte_view " +\
              "where dt = cast('2020-01-02 14:29:27.145' as timestamp)"

        expected_row = [{'dt': '2020-01-02 14:29:27.145',
                         'sum_posted_balance': '3408793.163',
                         'metric': 'Value credit transaction',
                         'sum_avbl_balance': '3408793.163'}]
        self.verify_query(user, sql, expected_row)

        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            # revoke privilege
            conn.execute_ddl("REVOKE SELECT ON DATABASE chase " +\
                             "TRANSFORM chase_pii.money WITH tokenize() " +\
                             "FROM ROLE presto_view_role")
            conn.execute_ddl("ALTER TABLE chase.ledger_balance " +\
                             "DROP COLUMN ATTRIBUTE " +\
                             "available_balance chase_pii.money")
            conn.execute_ddl("ALTER TABLE chase.ledger_balance " +\
                             "DROP COLUMN ATTRIBUTE " +\
                             "posted_balance chase_pii.money")
            conn.execute_ddl("DROP ATTRIBUTE IF EXISTS chase_pii.money")

    def test_create_view(self):
        if common.TEST_LEVEL in ["dev", "smoke"]:
            # Run over fewer dbs in lower test modes
            dbs = [
                'rs_json_format',
            ]
        else:
            dbs = [
                'rs',
                'rs_complex',
                'rs_complex_parquet',
                'rs_json_format',
            ]
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            DB = 'test_presto_views'

            # Cleanup from previous runs
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % DB)
            conn.execute_ddl('CREATE DATABASE %s' % DB)

            skippable_datasets = [
                # Presto doesn't like views that contain keywords or
                # start with numbers
                'null',
                '12345_begins_with_number',
                '12345_begins_with_number2',
                # These files are too big to be useful, scan takes too long
                'alltypes_large_s3',
                'alltypes_large_s3_gz',
                'alltypes_large_s3_gz_no_ext',
                'alltypes_large_s3_lzo',
                'gharch_test_data',
                # Fails to parse the AVSC file
                'avro_comments',
                # Fails due to map in arrays
                'complextypestbl_parq',
                # TODO: there seems to be some utf-8 decoding issue
                'encoding',
                # presto and okera don't order this the same
                'increasing_file_sizes',
                'partitioned_alltypes',
                'partitioned_tbl_s3_from_readonly_bucket',
                'partitioned_tbl',
                'market_decide_single_avro',
                'spark_snappy_part',
                'partitioned_data',
                'zd1318_chase_1',
                'zd1318_chase_2',
                'zd1318_okera',
                'chase_ledger_balance_timestamp',
                'chase_ledger_transaction_timestamp',
                'chase_parquet_timestamp',
                # ODAS can't run this either
                'partitioned_tbl_s3',
                's3_no_perm',
                'array_text',
                'map_text',
                'rs_complex_array_map_t',
                'rs_parquet_array_map_t',
                # Table is too big for Presto to run
                'test_many_columns',
                # Is an external view that Presto can't parse/analyze
                'zd1075_view',
                # These hudi tables do not return data (due to subdirs)
                'hudi_as_parquet',
                'hudi_nonpartitioned',
            ]

            # we have some ordering issues when comparing results on some datasets.
            compare_records_returned_only = [
              'hudi_partitioned',
              'lineitem_orc',
            ]

            for db in dbs:
                datasets = conn.list_dataset_names(db)
                for dataset in datasets:
                    view_db, view_ds = dataset.split(".")
                    view_name = dataset.replace('.', '_')

                    # Skip datasets that don't work
                    if view_ds.lower() in skippable_datasets:
                        continue

                    print("Running test over %s.%s" % (view_db, view_ds))

                    # This is called 'scan' but is really just a way to execute a query
                    # against Presto, which does not distinguish DDL and DQL
                    create_view_stmt = 'CREATE VIEW %s.%s AS SELECT * FROM "%s"."%s"' % (
                        DB,
                        view_name,
                        view_db,
                        view_ds
                    )
                    res = conn.scan_as_json(create_view_stmt, dialect='presto')
                    assert len(res) == 1
                    assert 'result' in res[0] and res[0]['result']

                    presto_view_results = conn.scan_as_json(
                        'select * from %s.%s' % (DB, view_name), dialect='presto')
                    presto_ds_results = conn.scan_as_json(
                        'select * from %s' % dataset, dialect='presto')
                    okera_ds_results = conn.scan_as_json(
                        'select * from %s' % dataset, dialect='okera',
                        strings_as_utf8=True)

                    if view_ds.lower() in compare_records_returned_only:
                        self.assertEqual(len(presto_view_results),
                                         len(presto_ds_results))
                        self.assertEqual(len(presto_view_results),
                                         len(okera_ds_results))
                        continue

                    PrestoTest.compare_json(
                        self, presto_view_results, okera_ds_results, False,
                        empty_struct_equals_null=False,
                        batch_mode=False, required_type=None,
                        empty_array_equals_null=False)
                    PrestoTest.compare_json(
                        self, presto_view_results, presto_ds_results, False,
                        empty_struct_equals_null=False,
                        batch_mode=False, required_type=None,
                        empty_array_equals_null=False)

            views = conn.list_dataset_names(db=DB)
            for view in views:
                drop_view_stmt = 'DROP VIEW %s' % view
                res = conn.scan_as_json(drop_view_stmt, dialect='presto')
                assert len(res) == 1
                assert 'result' in res[0] and res[0]['result']

    def test_create_view_permission(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            DB = 'test_presto_views'

            # Cleanup from previous runs
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % DB)
            conn.execute_ddl('CREATE DATABASE %s' % DB)

            # This is called 'scan' but is really just a way to execute a query
            # against Presto, which does not distinguish DDL and DQL
            ctx.enable_token_auth(token_str='user_without_priv')
            with pytest.raises(prestodb.exceptions.PrestoQueryError) as excinfo:
                create_view_stmt = 'CREATE VIEW %s.test_view AS SELECT 1 as a' % DB
                conn.scan_as_json(create_view_stmt, dialect='presto')
            assert "not have privileges to execute 'CREATE'" in str(excinfo.value)

    def test_session_properties(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            with pytest.raises(prestodb.exceptions.PrestoQueryError) as excinfo:
                conn.scan_as_json(
                    'select count(*) from nytaxi.parquet_data',
                    dialect='presto',
                    presto_session={'query_max_execution_time': '1s'})
            assert "name=EXCEEDED_TIME_LIMIT" in str(excinfo.value)

            with pytest.raises(prestodb.exceptions.PrestoQueryError) as excinfo:
                conn.scan_as_pandas(
                    'select count(*) from nytaxi.parquet_data',
                    dialect='presto',
                    presto_session={'query_max_execution_time': '1s'})
            assert "name=EXCEEDED_TIME_LIMIT" in str(excinfo.value)

    def test_table_stats(self):
        DB = "stats_test_db"
        TBL = "stats_tbl"
        TBL_DDL = "CREATE TABLE %s.%s (c1 int)" % (DB, TBL)

        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % DB)
            conn.execute_ddl("CREATE DATABASE %s" % DB)
            conn.execute_ddl(TBL_DDL)

            res = conn.scan_as_json('show stats for %s.%s' % (DB, TBL))
            assert len(res) == 2
            assert res[1]['row_count'] is None

            alter_ddl = "ALTER TABLE %s.%s SET TBLPROPERTIES('numRows'='27')" % (DB, TBL)
            # TODO: Not sure why we need this twice, but essentially it's not reliably
            # set in the planner (even if manually checked) if we only execute this once.
            res = conn.execute_ddl(alter_ddl)
            res = conn.execute_ddl(alter_ddl)

            res = conn.scan_as_json('show stats for %s.%s' % (DB, TBL))
            assert len(res) == 2
            assert res[1]['row_count'] == 27

    def test_presto_udfs(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            res = conn.scan_as_json('select current_database()')
            assert res[0]['_col0'] == 'okera'

    def test_presto_password(self):
        query = 'select * from okera_sample.sample'
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='presto_test_user')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            res = conn.scan_as_json(query, dialect='presto')
            assert len(res) == 2

            ctx.enable_token_auth(token_str='presto_test_user', presto_password='abc')
            with pytest.raises(prestodb.exceptions.DatabaseError) as excinfo:
                conn.scan_as_json(query, dialect='presto')
            assert "401" in str(excinfo.value)

            ctx.enable_token_auth(token_str='presto_test_user',
                                  presto_password='presto_test_user')
            res = conn.scan_as_json(query, dialect='presto')
            assert len(res) == 2

    def test_plan_error(self):
        DB = "presto_error_db"

        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % DB)
            conn.execute_ddl("CREATE DATABASE %s" % DB)
            conn.execute_ddl("CREATE TABLE %s.tbl(c1 string)" % DB)
            conn.execute_ddl("CREATE VIEW %s.vw AS SELECT c1 FROM %s.tbl" % (DB, DB))
            conn.execute_ddl("ALTER TABLE %s.tbl REPLACE COLUMNS (c2 string)" % DB)

            with pytest.raises(prestodb.exceptions.PrestoQueryError) as excinfo:
                conn.scan_as_json('select * from %s.vw' % (DB), dialect='presto')
            assert "Could not resolve column/field reference: 'c1'" in str(excinfo.value)

    def test_keywords_in_column_names(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            DB = "presto_test_db"
            TBL = "test_table"

            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % DB,
                "CREATE DATABASE %s" % DB,
                "CREATE TABLE %s.%s(`database` int, `metadata` struct<`table`: int>)" % (DB, TBL)
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            ctx.enable_token_auth(token_str='root')
            conn.scan_as_json('SELECT * FROM %s.%s' % (DB, TBL), dialect='presto')

    def test_user_delegation(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:

            def session_header(username):
                return {
                    'X-Presto-User': username
                }

            ctx.enable_token_auth(token_str='root')
            res = conn.scan_as_json('SELECT * FROM okera_sample.whoami',
                              dialect='presto')
            assert len(res) == 1
            assert res[0]['user'] == 'root'

            ctx.enable_token_auth(token_str='testuser')
            res = conn.scan_as_json('SELECT * FROM okera_sample.whoami',
                              dialect='presto')
            assert len(res) == 1
            assert res[0]['user'] == 'testuser'

            ctx.enable_token_auth(token_str='root')
            conn.scan_as_json('SELECT * FROM okera_sample.whoami',
                              dialect='presto', presto_headers=session_header('testuser'))
            assert len(res) == 1
            assert res[0]['user'] == 'testuser'

            ctx.enable_token_auth(token_str='randomuser')
            with pytest.raises(prestodb.exceptions.PrestoQueryError) as excinfo:
                conn.scan_as_json('SELECT * FROM okera_sample.whoami',
                                  dialect='presto', presto_headers=session_header('testuser'))
            assert "'randomuser' is not allowed to delegate for user 'testuser'" in str(excinfo.value)

    # pylint: enable=protected-access
