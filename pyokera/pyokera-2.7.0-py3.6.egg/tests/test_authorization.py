# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Integration authorization tests
#
# pylint: disable=consider-using-enumerate
# pylint: disable=too-many-locals
# pylint: disable=too-many-nested-blocks

import random
import time
import unittest

from okera.concurrency import OkeraWorkerException
from okera._thrift_api import TAuthorizeQueryParams
from okera._thrift_api import TRecordServiceException
from okera._thrift_api import TTypeId
from okera.tests import pycerebro_test_common as common

SKIP_LEVELS = ["smoke", "dev", "all"]

EPOCH0_DATE = '1970-01-01'
EPOCH0_TS = '1970-01-01 00:00:00.000'

TEST_DB = 'auth_test_db'
TEST_ROLE = 'auth_test_role'
TEST_USER = 'auth_test_user'
ABAC_TEST_ROLE = 'abac_test_role'
ABAC_TEST_USER = 'abac_test_user'
ABAC_TRANSFORM_ROLE = 'abac_transform_role'
ABAC_TRANSFORM_USER = 'abac_transform_user'
ABAC_TRANSFORM_ROLE2 = 'abac_transform_role2'
ABAC_TRANSFORM_USER2 = 'abac_transform_user2'

# Environment configs to control test running
MINIMAL_NUM_COLS = common.get_env_var('AUTH_TEST_MINIMAL_NUM_COLS', int, 1)
if common.get_env_var('AUTH_TEST_RANDOM_SEED', bool, False):
    print("Initializing to random seed (based on current time).")
    random.seed(None)
else:
    random.seed(1)
SKIP_SCANS = common.get_bool_env_var('AUTH_TEST_SKIP_SCANS', False)
AUTH_QUERY = SKIP_SCANS = common.get_bool_env_var('AUTH_TEST_AUTH_QUERY', False)

class AuthorizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(AuthorizationTest, cls).setUpClass()
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.delete_attribute('abac_auth_test', 'v1')
            conn.create_attribute('abac_auth_test', 'v1')

    # Runs a SQL statement and log it
    @staticmethod
    def __ddl(conn, sql):
        print(sql)
        conn.execute_ddl(sql)

    def __cleanup(self, conn):
        """ Cleanups all the test state used in this test to "reset" the catalog.
            dbs can be specified to do the initialize over multiple databases.
            This can be used for tests that use multiple dbs (but makes the test
            take longer). By default, only load TEST_DB.
        """
        self.__ddl(conn, "DROP ROLE IF EXISTS %s" % TEST_ROLE)
        self.__ddl(conn, "CREATE ROLE %s" % TEST_ROLE)
        self.__ddl(conn, "GRANT ROLE %s to GROUP %s" % (TEST_ROLE, TEST_USER))
        self.__ddl(conn, "DROP ROLE IF EXISTS %s" % ABAC_TEST_ROLE)
        self.__ddl(conn, "CREATE ROLE %s" % ABAC_TEST_ROLE)
        self.__ddl(conn, "GRANT ROLE %s to GROUP %s" % (ABAC_TEST_ROLE, ABAC_TEST_USER))
        self.__ddl(conn, "DROP ROLE IF EXISTS %s" % ABAC_TRANSFORM_ROLE)
        self.__ddl(conn, "CREATE ROLE %s" % ABAC_TRANSFORM_ROLE)
        self.__ddl(conn, "GRANT ROLE %s to GROUP %s" % \
            (ABAC_TRANSFORM_ROLE, ABAC_TRANSFORM_USER))
        self.__ddl(conn, "DROP ROLE IF EXISTS %s" % ABAC_TRANSFORM_ROLE2)
        self.__ddl(conn, "CREATE ROLE %s" % ABAC_TRANSFORM_ROLE2)
        self.__ddl(conn, "GRANT ROLE %s to GROUP %s" % \
            (ABAC_TRANSFORM_ROLE2, ABAC_TRANSFORM_USER2))

    def __convert_col(self, cols, idx):
        name = '`' + cols[idx].name + '`'
        type = cols[idx].type
        children = []
        if cols[idx].type.num_children:
            idx += 1
            for _ in range(0, cols[idx - 1].type.num_children):
                idx, child_name, child = self.__convert_col(cols, idx)
                children.append((child_name, child))
        else:
            idx += 1
        return idx, name, (type, children)

    def __top_level_columns(self, schema):
        cols = schema.nested_cols
        if not cols:
            cols = schema.cols
        names = []
        types = {}
        idx = 0
        while idx < len(cols):
            idx, name, col = self.__convert_col(cols, idx)
            names.append(name)
            types[name] = col
        return names, types

    @staticmethod
    def __collect_grant_objects(conn):
        grants = conn.execute_ddl('SHOW GRANT ROLE %s' % (TEST_ROLE))
        result = []
        for grant in grants:
            path = ''
            if grant[1]:
                path = grant[1]
                if grant[2]:
                    path += '.' + grant[2]
                    if grant[3]:
                        path += '.' + grant[3]
                else:
                    path += '.*'
            else:
                path = '*'
            result.append(path)
        return result

    # Tests that revokes to a db does not cascade to the table or columns
    def test_revoke_db_no_cascade(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)

            # Grant on db, table and column
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE okera_sample TO ROLE %s' % (TEST_ROLE))
            conn.execute_ddl(
                'GRANT SELECT ON TABLE okera_sample.sample TO ROLE %s' % (TEST_ROLE))
            conn.execute_ddl(
                'GRANT SELECT(record) ON TABLE okera_sample.sample TO ROLE %s' %\
                (TEST_ROLE))

            objs = self.__collect_grant_objects(conn)
            print(objs)
            self.assertTrue('okera_sample.*' in objs)
            self.assertTrue('okera_sample.sample' in objs)
            self.assertTrue('okera_sample.sample.record' in objs)
            self.assertEqual(len(objs), 3)

            # Revoke on db, should not cascade, this cascade can take a while so sleep
            # first. In the test setup, the refresh is 5 seconds.
            conn.execute_ddl(
                'REVOKE SELECT ON DATABASE okera_sample FROM ROLE %s' % (TEST_ROLE))
            time.sleep(7)
            objs = self.__collect_grant_objects(conn)
            print(objs)
            self.assertTrue('okera_sample.sample' in objs)
            self.assertTrue('okera_sample.sample.record' in objs)
            self.assertEqual(len(objs), 2)

            # Revoke on table, should not cascade.
            conn.execute_ddl(
                'REVOKE SELECT ON TABLE okera_sample.sample FROM ROLE %s' % (TEST_ROLE))
            time.sleep(7)
            objs = self.__collect_grant_objects(conn)
            print(objs)
            self.assertTrue('okera_sample.sample.record' in objs)
            self.assertEqual(len(objs), 1)

            # Revoke on column.
            conn.execute_ddl(
                'REVOKE SELECT(record) ON TABLE okera_sample.sample FROM ROLE %s' %\
                (TEST_ROLE))
            objs = self.__collect_grant_objects(conn)
            self.assertEqual(len(objs), 0)

    @staticmethod
    def __is_complex_type(t):
        return t.type_id == TTypeId.RECORD \
            or t.type_id == TTypeId.ARRAY \
            or t.type_id == TTypeId.MAP

    # Returns true if this value maps to 0
    def __is_zero(self, v):
        if isinstance(v, dict):
            for _, val in v.items():
                if not self.__is_zero(val):
                    return False
            return True
        if v is not None and isinstance(v, (bytes, str)):
            v = v.strip()
        return v in [0, '', b''] or str(v) in (EPOCH0_DATE, EPOCH0_TS) or float(v) == 0

    # Returns the first primitive type for the schema at col/t. Returns None if
    # all leaf types are complex (e.g. array)
    # FIXME: disable_recursion returns None if it is a record type. This is used
    # to disable some tests due to existing bugs.
    def __first_primitive_type(self, col, t, disable_recursion=False):
        if t[0].type_id == TTypeId.ARRAY or t[0].type_id == TTypeId.MAP:
            return None
        if t[0].type_id != TTypeId.RECORD:
            return col
        if disable_recursion:
            return None

        for child in t[1]:
            child_name = self.__first_primitive_type(
                child[0], child[1], disable_recursion)
            if not child_name:
                continue
            return col + '.' + child_name
        return None

    # Returns the number of fully expanded columns for this type. i.e. flattened
    # structs
    def __expanded_result_cols(self, t):
        result = 0
        if t[0].type_id == TTypeId.RECORD:
            for child in t[1]:
                result += self.__expanded_result_cols(child[1])
            return result
        if t[0].type_id == TTypeId.ARRAY:
            return 1 + self.__expanded_result_cols(t[1][0][1])
        if t[0].type_id == TTypeId.MAP:
            return 1 + self.__expanded_result_cols(t[1][0][1]) +\
                self.__expanded_result_cols(t[1][1][1])
        return 1

    # Verify that this query is authorized. If analysis_error is true, it means this
    # query is known to be semantically invalid but is authorized. This happens when
    # we, for example, run transformations on complex types.
    def __test_valid_query(self, conn, user, query, num_result_cols, test_scan,
                           analysis_error=False, pandas_num_result_cols=None,
                           expect_no_results=False, expect_complex_types_error=False,
                           transformed_cols=None):
        print('Running valid query: ' + query)
        if analysis_error:
            # We expect an analysis error (not auth) as this uses functions on complex
            # types
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                conn.plan(query)
            self.assertTrue('does not support complex types' in str(ex_ctx.exception) or\
                'No matching function' in str(ex_ctx.exception) or\
                'this column is a complex type' in str(ex_ctx.exception))
        else:
            try:
                schema = conn.plan(query).schema
            except TRecordServiceException as ex:
                # Transformations on complex types will fail.
                if expect_complex_types_error and \
                      user in [ABAC_TRANSFORM_USER, ABAC_TRANSFORM_USER2]:
                    self.assertTrue('this column is a complex type' in str(ex.detail))
                    return
                raise

            result_cols, _ = self.__top_level_columns(schema)
            self.assertEqual(num_result_cols, len(result_cols))

            # Verify authorize query succeeds
            if AUTH_QUERY:
                authorize_query = TAuthorizeQueryParams()
                authorize_query.sql = query
                authorize_query_result = conn.service.client.AuthorizeQuery(
                    authorize_query)
                self.assertTrue(authorize_query_result is not None)

            if not test_scan or SKIP_SCANS:
                return

            # Read the data from json and pandas
            try:
                result = conn.scan_as_json(query, max_records=1, max_task_count=1,
                                           strings_as_utf8=False)
                if expect_no_results:
                    self.assertEqual(0, len(result), msg="Result should have been empty.")
                if result:
                    self.assertEqual(num_result_cols, len(result[0]))
                    if transformed_cols and 'count(' not in query:
                        for row in result:
                            for key, v in row.items():
                                key = key.split('.')[0]
                                if key in transformed_cols:
                                    self.assertTrue(self.__is_zero(v))
            except OkeraWorkerException as ex:
                self.assertTrue('Only arrays of string, int32' in str(ex.error))
            try:
                df = conn.scan_as_pandas(query, max_records=1, max_task_count=1)
                if expect_no_results:
                    self.assertEqual(0, len(df), msg="Result should have been empty.")
                self.assertTrue(
                    len(df.columns) in [num_result_cols, pandas_num_result_cols],
                    msg=df)
            except OkeraWorkerException as ex:
                self.assertTrue('Only arrays of string, int32' in str(ex.error))

    # Verifies this query fails with an auth error
    def __test_invalid_query(self, conn, query):
        print("Running invalid query: " + query)
        with self.assertRaises(TRecordServiceException) as ex_ctx:
            conn.plan(query)
        self.assertTrue(
            'not have privilege' in str(ex_ctx.exception) or\
            'column is a complex type' in str(ex_ctx.exception),
            msg=str(ex_ctx.exception))

    def __test_visible_cols(self, conn, db, ds, user, types, visible_cols,
                            transformed_cols, test_scan):
        all_cols = ', '.join(visible_cols)
        tbl = db + '.' + ds

        # Queries that return all columns
        all_queries = [
            'SELECT * FROM %s.%s' % (db, ds),
            'SELECT %s from %s.%s' % (all_cols, db, ds),
            'SELECT * FROM (SELECT %s from %s.%s)v' % (all_cols, db, ds),
            'SELECT %s FROM (SELECT %s from %s.%s)v' % (all_cols, all_cols, db, ds),
            'SELECT %s FROM ( WITH cte_tbl as ' \
            '(SELECT %s from %s.%s) SELECT * FROM cte_tbl) v' %
            (all_cols, all_cols, db, ds),
        ]

        contains_complex = False
        for col in visible_cols:
            contains_complex |= self.__is_complex_type(types[col][0])

        for query in all_queries:
            print('Running valid query: ' + query)
            try:
                schema = conn.plan(query).schema
                result_cols, _ = self.__top_level_columns(schema)
                self.assertEqual(len(visible_cols), len(result_cols))
            except TRecordServiceException as ex:
                # Transformations on complx types will fail.
                if contains_complex and \
                      user in [ABAC_TRANSFORM_USER, ABAC_TRANSFORM_USER2]:
                    self.assertTrue('this column is a complex type' in str(ex.detail))
                else:
                    raise

        first_col = visible_cols[0]
        first_col_expanded = self.__expanded_result_cols(types[first_col])
        last_col = visible_cols[-1]
        last_col_complex = self.__is_complex_type(types[last_col][0])
        last_col_expanded = self.__expanded_result_cols(types[last_col])

        # Run some specific queries
        self.__test_valid_query(
            conn, user, 'SELECT %s FROM %s.%s' % (last_col, db, ds), 1,
            test_scan, False, last_col_expanded,
            expect_complex_types_error=self.__is_complex_type(types[last_col][0]),
            transformed_cols=transformed_cols)
        self.__test_valid_query(
            conn, user, 'SELECT count(*) FROM %s.%s' % (db, ds), 1, test_scan,
            transformed_cols=transformed_cols)

        # Go into the struct type to find a primitive type to query
        last_col_primitive = self.__first_primitive_type(last_col, types[last_col])
        first_col_primitive = self.__first_primitive_type(first_col, types[first_col])
        if last_col_primitive:
            self.__test_valid_query(
                conn, user, 'SELECT count(%s) FROM %s.%s' % (last_col_primitive, db, ds),
                1, test_scan, transformed_cols=transformed_cols)
            self.__test_valid_query(
                conn, user, 'SELECT count(%s) FROM %s.%s WHERE %s IS NOT NULL' % \
                    (last_col_primitive, db, ds, last_col_primitive), 1,
                test_scan, transformed_cols=transformed_cols)
            self.__test_valid_query(
                conn, user, 'SELECT count(%s) as c1, count(%s) as c2 FROM %s.%s' % \
                    (last_col_primitive, last_col_primitive, db, ds), 2,
                test_scan, False, transformed_cols=transformed_cols)

            if first_col_primitive and len(visible_cols) > 1:
                self.__test_valid_query(
                    conn, user, 'SELECT count(%s) as c1, count(%s) as c2 FROM %s.%s' % \
                        (first_col_primitive, last_col_primitive, db, ds), 2,
                    test_scan, transformed_cols=transformed_cols)

        # FIXME: for fields in structs, fails with:
        # Illegal reference to non-materialized slot
        last_col_primitive = self.__first_primitive_type(last_col, types[last_col], True)
        first_col_complex = self.__is_complex_type(types[first_col][0])
        if last_col_primitive:
            # Join on accessible column
            self.__test_valid_query(
                conn, user,
                'select a.%s from %s a join %s b on a.%s = b.%s' %\
                    (last_col, tbl, tbl, last_col_primitive, last_col_primitive),
                1, test_scan, False, first_col_expanded,
                transformed_cols=transformed_cols)
            self.__test_valid_query(
                conn, user,
                'select a.%s from %s a join %s b on a.%s = b.%s' %\
                    (first_col, tbl, tbl, last_col_primitive, last_col_primitive),
                1, test_scan, False, first_col_expanded,
                expect_complex_types_error=first_col_complex,
                transformed_cols=transformed_cols)

        # Get a primitive column.
        # This should be collapsed into the last block once above bugs are fixed
        last_col_primitive = self.__first_primitive_type(last_col, types[last_col])
        if last_col_primitive:
            # Test some queries that should return no results due to the where clause
            empty_where = 'CAST(%s AS STRING) = "NOT A VALUE TEST"' % last_col_primitive
            empty_queries = [
                'SELECT %s FROM %s.%s WHERE %s' % (first_col, db, ds, empty_where),
                'SELECT %s FROM (SELECT %s FROM %s.%s WHERE %s)v' %\
                    (first_col, first_col, db, ds, empty_where),
                'SELECT * FROM (SELECT %s FROM %s.%s WHERE %s)v' %\
                    (first_col, db, ds, empty_where),
            ]
            for query in empty_queries:
                self.__test_valid_query(
                    conn, user, query, 1, test_scan, False, first_col_expanded, True,
                    expect_complex_types_error=first_col_complex,
                    transformed_cols=transformed_cols)

            empty_queries = [
                'SELECT %s FROM (SELECT * FROM %s.%s WHERE %s)v' %\
                    (first_col, db, ds, empty_where),
            ]
            for query in empty_queries:
                self.__test_valid_query(
                    conn, user, query, 1, test_scan, False, first_col_expanded, True,
                    expect_complex_types_error=contains_complex,
                    transformed_cols=transformed_cols)

        # Run some queries that return one column
        queries_one_col_result = [
            'SELECT count(%s) FROM %s.%s' % (last_col, db, ds),
            'SELECT %s FROM %s.%s WHERE %s IS NOT NULL' % (first_col, db, ds, last_col),
            'SELECT count(%s) FROM %s.%s WHERE %s IS NOT NULL' % \
                (last_col, db, ds, last_col),
        ]
        for query in queries_one_col_result:
            is_complex = self.__is_complex_type(types[first_col][0])
            is_complex |= self.__is_complex_type(types[last_col][0])
            self.__test_valid_query(
                conn, user, query, 1, test_scan, last_col_complex, first_col_expanded,
                expect_complex_types_error=is_complex,
                transformed_cols=transformed_cols)

    def __test_no_access(self, conn, db, ds):
        # Tests when the user has access to nothing in the dataset
        # when no columns eligible for select, a privilege exception is thrown.
        queries = [
            'SELECT * FROM %s.%s' % (db, ds),
            'SELECT count(*) FROM %s.%s' % (db, ds),
            'SELECT count(*) FROM %s.%s WHERE false' % (db, ds),
            'SELECT * FROM (SELECT * FROM %s.%s)v' % (db, ds),
            'SELECT count(*) FROM (SELECT * FROM %s.%s)v' % (db, ds),
            'SELECT count(*) FROM (SELECT * FROM %s.%s)v' % (db, ds),
            'SELECT * FROM ( WITH cte_cnt_tbl as ' \
            '(SELECT * from %s.%s) SELECT count(*) FROM cte_cnt_tbl) v' % (db, ds)
        ]
        for query in queries:
            self.__test_invalid_query(conn, query)

    # Authorization tests where the user has access to visible_cols but not
    # non_visible_col.
    def __test_partial_access(self, conn, db, ds, user, types, visible_cols,
                              non_visible_col):
        tbl = db + '.' + ds
        visible = 1
        visible_col = 1
        visible_col_primitive = None
        if visible_cols:
            visible = ', '.join(visible_cols)
            visible_col = visible_cols[0]
            visible_col_primitive = self.__first_primitive_type(
                visible_col, types[visible_col])
        non_visible_col_primitive = self.__first_primitive_type(
            non_visible_col, types[non_visible_col])

        contains_complex = False
        for col in visible_cols:
            contains_complex |= self.__is_complex_type(types[col][0])

        # Collect all the queries that should fail
        queries = [
            'select %s from %s' % (non_visible_col, tbl)
        ]

        # Queries with both visible and not, should fail
        queries += [
            'select %s from %s WHERE %s IS NULL' % (visible_col, tbl, non_visible_col),
            'select %s from %s WHERE %s IS NULL' % (non_visible_col, tbl, visible_col),
            'select count(%s), count(%s) from %s' % (non_visible_col, visible_col, tbl),
            # CTEs
            'SELECT * FROM ( WITH cte_non_visible_tbl as ' \
            '(SELECT %s,%s from %s) SELECT %s, %s FROM cte_non_visible_tbl) v' %
            (non_visible_col, visible_col, tbl, non_visible_col, visible_col),
            'SELECT * FROM ( WITH cte_non_visible_tbl as ' \
            '(SELECT %s,%s from %s) SELECT count(%s) FROM cte_non_visible_tbl ' \
            'group by %s) v' %
            (non_visible_col, visible_col, tbl, non_visible_col, visible_col),

            'select %s from %s group by %s' % (non_visible_col, tbl, visible_col),
            'select %s from %s group by %s' % (visible_col, tbl, non_visible_col),

            'select %s from %s a join %s b on a.%s = b.%s' %\
                 (visible_col, tbl, tbl, non_visible_col, non_visible_col),

            'select %s from %s order by %s' % (non_visible_col, tbl, visible_col),
            'select %s from %s order by %s' % (visible_col, tbl, non_visible_col),
        ]

        # Try a field in the struct if this is a struct type. These should all fail
        if non_visible_col_primitive and \
              self.__is_complex_type(types[non_visible_col][0]):
            queries += [
                'select %s from %s' % (non_visible_col_primitive, tbl),
                'select %s from %s WHERE %s IS NULL' % \
                    (visible_col, tbl, non_visible_col_primitive),
                'select %s from %s WHERE %s IS NULL' % \
                    (non_visible_col_primitive, tbl, visible_col),
                'select count(%s), count(%s) from %s' % \
                    (non_visible_col_primitive, visible_col, tbl),

                'select %s from %s group by %s' % \
                    (non_visible_col_primitive, tbl, visible_col),
                'select %s from %s group by %s' % \
                    (visible_col, tbl, non_visible_col_primitive),

                'select %s from %s order by %s' % \
                    (non_visible_col_primitive, tbl, visible_col),

                'select %s from %s order by %s' % \
                    (visible_col, tbl, non_visible_col_primitive),

                'select %s from %s a join %s b on a.%s = b.%s' %\
                    (visible_col, tbl, tbl, non_visible_col_primitive,
                     non_visible_col_primitive),
            ]

        if visible_cols:
            queries += [
                'select %s from %s a join %s b on a.%s = b.%s' %\
                    (visible_col, tbl, tbl, non_visible_col, visible_col),
                'select %s from %s a join %s b on a.%s = b.%s' %\
                    (visible_col, tbl, tbl, visible_col, non_visible_col),
            ]
            if visible_col_primitive:
                queries += [
                    'select a.%s from %s a join %s b on a.%s = b.%s' %\
                        (non_visible_col, tbl, tbl, visible_col_primitive,
                         visible_col_primitive),
                ]

        # Now run all the queries
        for query in queries:
            self.__test_invalid_query(conn, query)

        # Add this inaccessible column to the accessible ones, should fail.
        # Try a few permutations.
        select_list = visible_cols.copy()
        select_list.append(non_visible_col)
        for _ in range(0, min(len(select_list), 3)):
            random.shuffle(select_list)
            self.__test_invalid_query(
                conn, 'select %s from %s' % (','.join(select_list), tbl))

        primitive = self.__first_primitive_type(non_visible_col, types[non_visible_col])
        is_complex = self.__is_complex_type(types[non_visible_col][0])
        if primitive and is_complex and \
              user not in [ABAC_TRANSFORM_USER, ABAC_TRANSFORM_USER2]:
            # Test with a where clause on inaccessible column.
            self.__test_invalid_query(
                conn,
                'select %s from %s WHERE %s IS NOT NULL' % (visible, tbl, primitive))

    # Authorization has been configured on db.ds for visible and non-visible columns
    # on this dataset, for this user.
    # This function permutes over queries on this dataset.
    def __test_dataset_auth(self, ctx, conn, db, ds, all_cols, types,
                            visible_cols, non_visible_cols, transformed_cols,
                            user, minimal, test_scan):
        print("\nTest on %s.%s with visible cols (%s), non-visible cols(%s) for: %s" %\
              (db, ds, ', '.join(visible_cols), ', '.join(non_visible_cols), user))

        # Admin user should always see all columns
        ctx.disable_auth()
        schema = conn.plan('select * from %s.%s' % (db, ds)).schema
        result_cols, _ = self.__top_level_columns(schema)
        self.assertEqual(len(all_cols), len(result_cols))

        # Switch to test user
        ctx.enable_token_auth(token_str=user)
        if visible_cols:
            self.__test_visible_cols(conn, db, ds, user, types, visible_cols,
                                     transformed_cols, test_scan)
        else:
            self.__test_no_access(conn, db, ds)

        if minimal:
            if non_visible_cols:
                non_visible_cols_copy = non_visible_cols.copy()
                random.shuffle(non_visible_cols_copy)
                n = len(non_visible_cols_copy)
                if minimal:
                    n = min(n, MINIMAL_NUM_COLS)
                for idx in range(0, n):
                    self.__test_partial_access(
                        conn, db, ds, user, types, visible_cols,
                        non_visible_cols_copy[idx])
        else:
            for non_visible_col in non_visible_cols:
                self.__test_partial_access(
                    conn, db, ds, user, types, visible_cols, non_visible_col)

    # Runs ACL tests against db.ds
    # This test will permute through multiple dimensions to generate test cases.
    #
    # 1) ABAC/RBAC for column/table visibility
    #    X
    # 2) Queries to run
    #    X
    # 3) Clients to run it against
    #
    # This function is handles 1).
    # If minimal is true, don't exhaustive test all columns to reduce test times.
    def __test_dataset(self, ctx, conn, db, ds, minimal=False, test_scan=True):
        print("\n\nTesting dataset: %s.%s..." % (db, ds))

        ctx.disable_auth()
        print('Running valid query: select * from %s.%s' % (db, ds))
        schema = conn.plan('select * from %s.%s' % (db, ds)).schema
        all_cols, types = self.__top_level_columns(schema)
        self.__cleanup(conn)

        # Generate the columns the RBAC and ABAC user is allowed to access. The RBAC
        # user starts with no access and gets it column by column. The ABAC user does
        # the opposite.
        # TODO: add another user that uses both
        rbac_visible_cols = []
        rbac_non_visible_cols = all_cols.copy()
        abac_non_visible_cols = []
        abac_visible_cols = all_cols.copy()
        transformed_cols = []

        # Test ABAC: GRANT SELECT on table based on attribute (not in)
        self.__ddl(
            conn,
            ('GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +\
            'not in (abac_auth_test.v1) TO ROLE %s') % (db, ds, ABAC_TEST_ROLE))

        # Test transform: GRANT but only with transform. Every column is set to zero.
        self.__ddl(
            conn,
            ('GRANT SELECT ON TABLE %s.%s ' +\
            'HAVING ATTRIBUTE abac_auth_test.v1 ' + \
            'TRANSFORM abac_auth_test.v1 with zero() ' + \
            'TO ROLE %s') % (db, ds, ABAC_TRANSFORM_ROLE))

        # Test another transform GRANT. In this case the user can always see all
        # columns, and an increasing number of them are masked
        self.__ddl(
            conn,
            ('GRANT SELECT ON TABLE %s.%s ' +\
            'TRANSFORM abac_auth_test.v1 with zero() ' + \
            'TO ROLE %s') % (db, ds, ABAC_TRANSFORM_ROLE2))

        # Only admin and ABAC user can see all
        self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types, rbac_visible_cols,
                                 rbac_non_visible_cols, [], TEST_USER, minimal, test_scan)
        self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types, abac_visible_cols,
                                 abac_non_visible_cols, [], ABAC_TEST_USER, minimal,
                                 test_scan)
        self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types, rbac_visible_cols,
                                 rbac_non_visible_cols, transformed_cols,
                                 ABAC_TRANSFORM_ROLE, minimal, test_scan)
        self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types, all_cols, [],
                                 transformed_cols, ABAC_TRANSFORM_USER2, minimal,
                                 test_scan)

        # Loop over columns in this dataset. Randomize order of columns. We tend to put
        # the types in the same order across tables
        random.shuffle(all_cols)
        n = len(all_cols)
        if minimal:
            n = min(n, MINIMAL_NUM_COLS)

        for idx in range(0, n):
            c = all_cols[idx]

            # RBAC grant granting to additional columns
            ctx.disable_auth()
            self.__ddl(conn, 'GRANT SELECT(%s) ON TABLE %s.%s TO ROLE %s' %\
                  (c, db, ds, TEST_ROLE))
            rbac_visible_cols.append(c)
            rbac_non_visible_cols.remove(c)

            # Keep assigning attributes one by one that would result in exclusion of
            # the column due to ABAC evaluation. Don't cascade so each test case can
            # do its own thing.
            print("\nAssigning tag to %s.%s.%s" % (db, ds, c))
            conn.assign_attribute('abac_auth_test', 'v1', db, ds, c.strip('`'),
                                  cascade=False)
            abac_non_visible_cols.append(c)
            transformed_cols.append(c.strip('`'))
            abac_visible_cols.remove(c)

            # Grants are set up, now verify this dataset
            self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types,
                                     rbac_visible_cols, rbac_non_visible_cols, [],
                                     TEST_USER, minimal, test_scan)
            self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types,
                                     abac_visible_cols, abac_non_visible_cols, [],
                                     ABAC_TEST_USER, minimal, test_scan)
            self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types,
                                     rbac_visible_cols, rbac_non_visible_cols,
                                     transformed_cols,
                                     ABAC_TRANSFORM_USER, minimal, test_scan)
            self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types, all_cols, [],
                                     transformed_cols, ABAC_TRANSFORM_USER2, minimal,
                                     test_scan)

        # Grant to entire table and verify
        ctx.disable_auth()
        self.__ddl(conn, 'GRANT SELECT ON TABLE %s.%s TO ROLE %s' %\
              (db, ds, TEST_ROLE))
        self.__test_dataset_auth(ctx, conn, db, ds, all_cols, types,
                                 all_cols, [], [], TEST_USER, minimal, test_scan)

    # Tests that verify grants to complex types works. This programmatically gets
    # columns to the table/view and increasingly grants more access to it.
    @unittest.skipIf(common.TEST_LEVEL in ["all"], "Skipping at all level")
    def test_complex_types_core(self):
        # This contains a subset that capture most cases
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in ['struct_t', 'strarray_t_view']:
                self.__test_dataset(ctx, conn, 'rs_complex', ds)

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_complex_types_extended(self):
        # This adds some additional tables and run at a higher test level to control
        # test times.
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in ['struct_t2', 'struct_t3', 'struct_array_struct', 'struct_view',
                       'struct_t_restricted_view', 'struct_nested', 'struct_t_view2',
                       'struct_nested_view', 'array_struct_array', 'array_struct_t',
                       'array_t', 'avrotbl', 'map_t', 'multiple_structs_nested', 'users',
                       'user_phone_numbers', 'user_phone_numbers_map']:
                self.__test_dataset(ctx, conn, 'rs_complex', ds)

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_market_data(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__test_dataset(ctx, conn, 'rs_complex', 'market_v20_single')

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_complex_types_slow(self):
        # These tests are N^2 with the number of columns so don't run these by default
        slow = ['test_bucketing_tbl', 'zd1216', 'zd1216_with_subscriptionlimit']

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in slow:
                self.__test_dataset(ctx, conn, 'rs_complex', ds, True)
            for ds in ['ledger_balance', 'subscription', 'subscription_currency',
                       'subscription_view']:
                self.__test_dataset(ctx, conn, 'chase', ds, True)

    @staticmethod
    def check_dataset_metadata(database, dataset, prop, value):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ds_info = conn.list_datasets(db=database, name=dataset)
            assert(len(ds_info) == 1)
            ds_md = ds_info[0].metadata
            return (ds_md is not None) and (prop in ds_md) and (ds_md[prop] == value)

    def __test_db(self, ctx, conn, db, minimal):
        print("Testing database: " + db)
        ctx.disable_auth()
        datasets = conn.list_dataset_names(db)
        for ds in datasets:
            # If set to false, don't run the scanning (just the planning). We do
            # for big datasets that can take a long time to to skip tables that
            # we can't scan due to bugs (but still get some test coverage).
            run_scan = True

            # These datasets/dbs take a long time to run as the dataset is big
            if ds in ['buckets_test.nytaxi_sample_bucketed',
                      'nytaxi.orc_data',
                      'nytaxi.parquet_data',
                      'nytaxi.parquet_mega',
                      'nytaxi.parquet_data_symlink',
                      'nytaxi.unionallview',
                      'partition_test.part_flat_200_data_100',
                      'rs.alltypes_large_s3',
                      'rs.alltypes_large_s3_gz',
                      'rs.alltypes_large_s3_gz_no_ext',
                      'rs.alltypes_large_s3_lzo']:
                run_scan = False

            if db in ['tpcds1000_partitioned', 'tpcds1000_unpartitioned',
                      'tpcds100_partitioned', 'tpcds100_unpartitioned',
                      'tpcds10_partitioned', 'tpcds10_unpartitioned',
                      'tpcds1_partitioned', 'tpcds1_unpartitioned',
                      'tpcds_csv_10', 'tpcds_csv_100', 'tpch_sf1', 'tpch_sf5',
                      'zd1179large']:
                run_scan = False

            # Complex types on text format, not supported.
            # This fails to plan.
            if ds in ['customer.japan_pos_trade_item_stg',
                      'customer.japan_pos_trade_item_stg_part',
                      'rs_complex.array_text',
                      'rs_complex.map_text']:
                continue

            # Data is inaccessible in s3. This table is not suppose to work.
            # This fails to plan.
            if ds in ['rs.s3_no_perm']:
                continue

            # Data stored in DBFS which we can't plan.
            # This fails to plan.
            if ds in ['customer.zd1010_dbfs_table_external_provider',
                      'customer.zd1065_dbfs_table_no_provider']:
                continue

            # BUG[DAS-4871]
            # Test fail to assign tags due to special characters in the column name.
            # This fails to plan.
            if ds in ['special_chars.space_table',
                      'special_chars.test_table']:
                continue

            # BUG: Self join bug
            # This fails to plan.
            if ds in ['customer.zd608_fiducia_risk_score_ato_tb',
                      'demo.reporting_audit_logs',
                      'partition_test.special_chars_partition',
                      'partition_test.special_chars_partition_nested',
                      'partition_test.timestamp_part_encoded',
                      'partition_test.timestamp_part_test',
                      'partition_test.timestamp_part_test2']:
                continue

            # BUG[DAS-4799]: This crashes the worker
            # This fails to scan.
            if ds in ['parquet_testing.dict_page_offset_zero']:
                run_scan = False

            # BUG[DAS-5908]: This crashes the worker
            # This fails to scan.
            if ds in ['rs_complex.unnest1', 'rs_complex.unnest2']:
                run_scan = False

            # BUG[DAS-4801]: Worker fails this query with nested array items
            # This fails to scan.
            if ds in ['parquet_testing.nested_lists_snappy',
                      'parquet_testing.nonnullable_impala',
                      'parquet_testing.nullable_impala',
                      'rs_complex_parquet.rs_parquet_array_map_t',
                      'rs_complex.rs_complex_array_map_t',]:
                run_scan = False

            # BUG[DAS-4802]: pyokera fails to deserialize with index out of bounds
            # This fails to scan.
            if ds in ['parquet_testing.nested_maps_snappy']:
                run_scan = False

            # BUG[DAS-4905]: This where clause is not supported right and dropped
            # This fails to scan.
            if ds in ['chase.subscription_party_view']:
                continue

            # BUG[DAS-5500]: Fail to convert
            if ds in ['customer.t2_authzn', 'partition_test.keyword_part_table',
                      'datedb.dates_with_invalid_data', 'partition_test.weird_partition6',
                      'rs.partitioned_tbl_s3']:
                continue

            # Bad avro format cant be scanned
            if ds in ['customer.zd623_east', 'rs.avro_comments']:
                run_scan = False

            # Unsupported
            if ds in ['parquet_testing.datapage_v2_snappy', 'rs_complex.pn_view',
                      'parquet_testing.nested_maps_snappy',
                      'parquet_testing.repeated_no_annotation']:
                continue


            # JDBC datasets
            if ds in ['jdbc_psql_test.nytaxi_demo',
                      'jdbc_test_athena._abac_privileges',
                      'jdbc_test_athena._sentry_privileges',
                      'jdbc_test_athena.privileges']:
                continue

            # Skip if ds is external view
            if self.check_dataset_metadata(ds.split('.')[0], ds.split('.')[1],
                                           'cerebro.external.view', 'true'):
                continue

            self.__test_dataset(ctx, conn, db, ds.split('.')[1], minimal, run_scan)

    @unittest.skip("Example for use during development to test a specific dataset.")
    def test_single_dataset(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__test_dataset(
                ctx, conn, 'rs_complex', 'struct_view', minimal=False, test_scan=True)

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_rs_db(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in ['alltypes', 'alltypes_null', 'ccn',
                       'large_decimals', 'nation_projection',
                       's3_nation', 'users']:
                self.__test_dataset(ctx, conn, 'rs', ds)

    @unittest.skipIf(common.TEST_LEVEL in SKIP_LEVELS, "Skipping at unit/all level")
    def test_auth_db(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__test_db(ctx, conn, 'authdb', True)

    @unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
    def test_all(self):
        # Runs test again all tables in all dbs, except the black listed ones
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            dbs = conn.list_databases()
            for db in dbs:
                # Dbs that either have public access or non queryable tables
                # BUG DAS-5544 filter pushdown on jdbc tables
                # Delta tables are getting errors from the manifest file when scanning
                if db in ['bad_metadata_db', 'cerebro_sample', 'default', 'demo',
                          'okera_sample', 'okera_system', 'all_table_types',
                          'jdbc_test_mysql', 'jdbc_test_psql', 'jdbc_test_redshift',
                          'jdbc_test_snowflake', 'jdbc_test_sqlserver',
                          'jdbc_test_oracle', 'delta_db']:
                    continue
                if db.startswith('_'):
                    continue

                self.__test_db(ctx, conn, db, True)

if __name__ == "__main__":
    unittest.main()
