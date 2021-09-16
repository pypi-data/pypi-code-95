# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for role granting
#
# pylint: disable=too-many-public-methods
# pylint: disable=line-too-long
# pylint: disable=len-as-condition
# pylint: disable=too-many-locals

import unittest

from okera._thrift_api import TAuthorizeQueryParams
from okera.tests import pycerebro_test_common as common

DB = 'test_privacy_db'
ROLE = 'test_privacy_role'
WORKSPACE_ROLE = 'okera_workspace_role'
VIEW = 'test_privacy_view'
USER1 = 'testprivacyuser1'
USER2 = 'testprivacyuser2'
USER3 = 'testprivacyuser3'

ATTR1 = "test_privacy_attr.attr1"
ATTR2 = "test_privacy_attr.attr2"

ALLTYPES_TABLE = 'alltypes'
ALLTYPES_TABLE2 = 'alltypes2'
ALLTYPES_ALL_ROWS_VIEW = 'alltypes_all_rows_view'
ALLTYPES_FIRST_ROW_DOUBLED_VIEW = 'alltypes_first_row_doubled_view'
ALLTYPES_SECOND_ROW_DOUBLED_VIEW = 'alltypes_second_row_doubled_view'
ALLTYPES_PRIVACY_VIEW = 'alltypes_privacy_view'
ALLTYPES_PRIVACY_UNIQUE_VIEW = 'alltypes_privacy_unique_view'
ALLTYPES_PRIVACY_SHARED_VIEW = 'alltypes_privacy_shared_view'
ALLTYPES_PRIVACY_UNIQUE_VIEW1 = 'alltypes_privacy_unique_no_ref_int_view1'
ALLTYPES_PRIVACY_UNIQUE_VIEW2 = 'alltypes_privacy_unique_no_ref_int_view2'
ALLTYPES_PRIVACY_SHARED_VIEW1 = 'alltypes_privacy_shared_no_ref_int_view1'
ALLTYPES_PRIVACY_SHARED_VIEW2 = 'alltypes_privacy_shared_no_ref_int_view2'

ALLTYPES_S3_DDL = """
CREATE EXTERNAL TABLE %s.%%s (
  bool_col BOOLEAN ATTRIBUTE test_privacy_attr.attr1 test_privacy_attr.attr2,
  tinyint_col TINYINT ATTRIBUTE test_privacy_attr.attr1 test_privacy_attr.attr2,
  smallint_col SMALLINT ATTRIBUTE test_privacy_attr.attr1 test_privacy_attr.attr2,
  int_col INT ATTRIBUTE test_privacy_attr.attr1 test_privacy_attr.attr2,
  bigint_col BIGINT ATTRIBUTE test_privacy_attr.attr1 test_privacy_attr.attr2,
  float_col FLOAT ATTRIBUTE test_privacy_attr.attr1,
  double_col DOUBLE ATTRIBUTE test_privacy_attr.attr1,
  string_col STRING ATTRIBUTE test_privacy_attr.attr1,
  varchar_col VARCHAR(10) ATTRIBUTE test_privacy_attr.attr1,
  char_col CHAR(5) ATTRIBUTE test_privacy_attr.attr1,
  timestamp_col TIMESTAMP ATTRIBUTE test_privacy_attr.attr1,
  decimal_col DECIMAL(24,10) ATTRIBUTE test_privacy_attr.attr1
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
WITH SERDEPROPERTIES ('field.delim'='|', 'serialization.format'='|')
STORED AS TEXTFILE
LOCATION 's3a://cerebrodata-test/alltypes'
""" % (DB)

ALLTYPES_ALL_ROWS_VIEW_DDL = """
CREATE VIEW %s.%s AS SELECT * FROM %s.%s
""" % (DB, ALLTYPES_ALL_ROWS_VIEW, DB, ALLTYPES_TABLE)

ALLTYPES_PRIVACY_QUERY = """
SELECT
    {privacy_fn}(bool_col) as bool_col,
    {privacy_fn}(tinyint_col) as tinyint_col,
    {privacy_fn}(smallint_col) as smallint_col,
    {privacy_fn}(int_col) as int_col,
    {privacy_fn}(bigint_col) as bigint_col,
    {privacy_fn}(float_col) as float_col,
    {privacy_fn}(double_col) as double_col,
    {privacy_fn}(string_col) as string_col,
    {privacy_fn}(varchar_col) as varchar_col,
    {privacy_fn}(char_col) as char_col,
    {privacy_fn}(timestamp_col) as timestamp_col,
    {privacy_fn}(decimal_col) as decimal_col
FROM {db}.{table}
"""

ALLTYPES_PRIVACY_VIEW_DDL = """
CREATE VIEW {db}.{view} AS SELECT
    {privacy_fn}(bool_col) as bool_col,
    {privacy_fn}(tinyint_col) as tinyint_col,
    {privacy_fn}(smallint_col) as smallint_col,
    {privacy_fn}(int_col) as int_col,
    {privacy_fn}(bigint_col) as bigint_col,
    {privacy_fn}(float_col) as float_col,
    {privacy_fn}(double_col) as double_col,
    {privacy_fn}(string_col) as string_col,
    {privacy_fn}(varchar_col) as varchar_col,
    {privacy_fn}(char_col) as char_col,
    {privacy_fn}(timestamp_col) as timestamp_col,
    {privacy_fn}(decimal_col) as decimal_col
FROM {db}.{table}
"""

ALLTYPES_FIRST_ROW_DOUBLED_VIEW_DDL = """
CREATE VIEW %s.%s AS %s
WHERE bool_col = true
UNION ALL %s
WHERE bool_col = true
""" % (DB, ALLTYPES_FIRST_ROW_DOUBLED_VIEW, ALLTYPES_PRIVACY_QUERY, ALLTYPES_PRIVACY_QUERY)

ALLTYPES_SECOND_ROW_DOUBLED_VIEW_DDL = """
CREATE VIEW %s.%s AS %s
WHERE bool_col = false
UNION ALL %s
WHERE bool_col = false
""" % (DB, ALLTYPES_SECOND_ROW_DOUBLED_VIEW, ALLTYPES_PRIVACY_QUERY, ALLTYPES_PRIVACY_QUERY)

ALLTYPES_PRIVACY_UNIQUE_VIEW_DDL = """
CREATE VIEW {db}.{view} AS SELECT
    {privacy_fn}(bool_col, signed_user(true)) as bool_col,
    {privacy_fn}(tinyint_col, signed_user(true)) as tinyint_col,
    {privacy_fn}(smallint_col, signed_user(true)) as smallint_col,
    {privacy_fn}(int_col, signed_user(true)) as int_col,
    {privacy_fn}(bigint_col, signed_user(true)) as bigint_col,
    {privacy_fn}(float_col, signed_user(true)) as float_col,
    {privacy_fn}(double_col, signed_user(true)) as double_col,
    {privacy_fn}(string_col, signed_user(true)) as string_col,
    {privacy_fn}(varchar_col, signed_user(true)) as varchar_col,
    {privacy_fn}(char_col, signed_user(true)) as char_col,
    {privacy_fn}(timestamp_col, signed_user(true)) as timestamp_col,
    {privacy_fn}(decimal_col, signed_user(true)) as decimal_col
FROM {db}.{table}
"""

ALLTYPES_PRIVACY_SHARED_VIEW_DDL = """
CREATE VIEW {db}.{view} AS SELECT
    {privacy_fn}(bool_col, signed_user(false)) as bool_col,
    {privacy_fn}(tinyint_col, signed_user(false)) as tinyint_col,
    {privacy_fn}(smallint_col, signed_user(false)) as smallint_col,
    {privacy_fn}(int_col, signed_user(false)) as int_col,
    {privacy_fn}(bigint_col, signed_user(false)) as bigint_col,
    {privacy_fn}(float_col, signed_user(false)) as float_col,
    {privacy_fn}(double_col, signed_user(false)) as double_col,
    {privacy_fn}(string_col, signed_user(false)) as string_col,
    {privacy_fn}(varchar_col, signed_user(false)) as varchar_col,
    {privacy_fn}(char_col, signed_user(false)) as char_col,
    {privacy_fn}(timestamp_col, signed_user(false)) as timestamp_col,
    {privacy_fn}(decimal_col, signed_user(false)) as decimal_col
FROM {db}.{table}
"""

GRANT_WITH_TRANSFORM_ATTR1_DDL = """
GRANT SELECT ON DATABASE %s
TRANSFORM %s WITH %%s
TO ROLE %s
""" % (DB, ATTR1, ROLE)

REVOKE_WITH_TRANSFORM_ATTR2_DDL = """
REVOKE SELECT ON TABLE %s.%s
TRANSFORM %s WITH %%s
FROM ROLE %s
""" % (DB, ALLTYPES_TABLE, ATTR1, ROLE)

GRANT_WITH_TRANSFORM_ATTR2_DDL = """
GRANT SELECT ON DATABASE %s
TRANSFORM %s WITH %%s
TO ROLE %s
""" % (DB, ATTR2, ROLE)

REVOKE_WITH_TRANSFORM_ATTR2_DDL = """
REVOKE SELECT ON TABLE %s.%s
TRANSFORM %s WITH %%s
FROM ROLE %s
""" % (DB, ALLTYPES_TABLE, ATTR2, ROLE)

ALLTYPES_STRING_COLS = ['varchar_col', 'string_col', 'char_col', 'timestamp_col']
ALLTYPES_TRANSFORMED_COLS = ['bool_col', 'tinyint_col', 'smallint_col', 'int_col', 'bigint_col']
ALLTYPES_RESULTS = [
    {'float_col': 4.0, 'varchar_col': 'vchar1', 'decimal_col': '3.1415920000',
     'smallint_col': 1, 'double_col': 5.0, 'bool_col': True, 'string_col': 'hello',
     'int_col': 2, 'timestamp_col': '2015-01-01 00:00:00.000', 'bigint_col': 3,
     'char_col': 'char1', 'tinyint_col': 0},
    {'float_col': 10.0, 'varchar_col': 'vchar2', 'decimal_col': '1234.5678900000',
     'smallint_col': 7, 'double_col': 11.0, 'bool_col': False, 'string_col': 'world',
     'int_col': 8, 'timestamp_col': '2016-01-01 00:00:00.000', 'bigint_col': 9,
     'char_col': 'char2', 'tinyint_col': 6}
]

ALLTYPES_CONSTANT_VALUES = {
    'bool_col': 'true',
    'tinyint_col': 'cast(5 AS TINYINT)',
    'smallint_col': 'cast(1024 AS TINYINT)',
    'int_col': 'cast(12345678 AS TINYINT)',
    'bigint_col': 'cast(123456789123456 AS BIGINT)',
    'float_col': 'cast(12.345 AS FLOAT)',
    'double_col': 'cast(12.345 AS DOUBLE)',
    'string_col': '\'abcdefghi\'',
    'varchar_col': 'cast(\'abcde\' AS VARCHAR(10))',
    'char_col': 'cast(\'abcde\' AS CHAR(5))',
    'timestamp_col': 'cast(10 AS TIMESTAMP)',
    'decimal_col': 'cast(12.345 AS DECIMAL(5,3))',
}

def scan_as_json(ctx, conn, query, dialect='okera', user=None):
    current_user = None
    if user:
        current_user = ctx.get_token()
        ctx.enable_token_auth(token_str=user)
    res = conn.scan_as_json(query, dialect=dialect)

    if current_user:
        ctx.enable_token_auth(token_str=current_user)
    else:
        ctx.disable_auth()
    return res

def authorize_query(conn, query, user):
    request = TAuthorizeQueryParams()
    request.sql = query
    request.requesting_user = user
    result = conn.service.client.AuthorizeQuery(request)
    return ' '.join(result.result_sql.split())

class PrivacyTest(unittest.TestCase):
    def _validate_query(self, ctx, conn, query,
                        equal_across_users=True, equal_across_queries=True,
                        has_results=True, equal_across_rows=False, null_col=None,
                        check_results=True):
        print(query)
        user1_res1 = scan_as_json(ctx, conn, query, user=USER1)
        user1_res2 = scan_as_json(ctx, conn, query, user=USER1)
        user2_res1 = scan_as_json(ctx, conn, query, user=USER2)

        if not check_results:
            return

        if has_results:
            self.assertTrue(len(user1_res1) > 0)
            self.assertTrue(len(user1_res2) > 0)
            self.assertTrue(len(user2_res1) > 0)
            if null_col:
                for result in [user1_res1, user1_res2, user2_res1]:
                    for record in result:
                        self.assertTrue(record[null_col] is None)
        else:
            self.assertTrue(len(user1_res1) == 0)
            self.assertTrue(len(user1_res2) == 0)
            self.assertTrue(len(user2_res1) == 0)

        if has_results:
            # These checks are only meaningful if we have results
            if equal_across_queries:
                self.assertTrue(user1_res1 == user1_res2)
            else:
                self.assertTrue(user1_res1 != user1_res2)

            if equal_across_users:
                self.assertTrue(user1_res1 == user2_res1)
            else:
                self.assertTrue(user1_res1 != user2_res1)

            if equal_across_rows:
                self.assertTrue(len(user1_res1) == 2)
                self.assertTrue(len(user1_res2) == 2)
                self.assertTrue(len(user2_res1) == 2)
                self.assertTrue(user1_res1[0] == user1_res1[1])
                self.assertTrue(user1_res2[0] == user1_res2[1])
                self.assertTrue(user2_res1[0] == user2_res1[1])


    def _test_fn(self, fn, maintains_ref_integrity, stable, maintains_type):
        PRIVACY_FN = fn
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP ATTRIBUTE IF EXISTS %s' % ATTR1)
            conn.execute_ddl('DROP ATTRIBUTE IF EXISTS %s' % ATTR2)
            conn.execute_ddl('DROP ROLE IF EXISTS %s' % ROLE)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % DB)
            conn.execute_ddl('CREATE DATABASE %s' % DB)
            conn.execute_ddl('CREATE ATTRIBUTE %s' % ATTR1)
            conn.execute_ddl('CREATE ATTRIBUTE %s' % ATTR2)

            conn.execute_ddl(ALLTYPES_S3_DDL % ALLTYPES_TABLE)
            conn.execute_ddl(ALLTYPES_S3_DDL % ALLTYPES_TABLE2)
            conn.execute_ddl(ALLTYPES_FIRST_ROW_DOUBLED_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE, privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_SECOND_ROW_DOUBLED_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE, privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_PRIVACY_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE, view=ALLTYPES_PRIVACY_VIEW,
                privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_PRIVACY_UNIQUE_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE, view=ALLTYPES_PRIVACY_UNIQUE_VIEW,
                privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_PRIVACY_SHARED_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE, view=ALLTYPES_PRIVACY_SHARED_VIEW,
                privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_PRIVACY_SHARED_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE, view=ALLTYPES_PRIVACY_SHARED_VIEW1,
                privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_PRIVACY_SHARED_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE2, view=ALLTYPES_PRIVACY_SHARED_VIEW2,
                privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_PRIVACY_UNIQUE_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE, view=ALLTYPES_PRIVACY_UNIQUE_VIEW1,
                privacy_fn=PRIVACY_FN))
            conn.execute_ddl(ALLTYPES_PRIVACY_UNIQUE_VIEW_DDL.format(
                db=DB, table=ALLTYPES_TABLE2, view=ALLTYPES_PRIVACY_UNIQUE_VIEW2,
                privacy_fn=PRIVACY_FN))

            conn.execute_ddl('CREATE ROLE %s' % ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (ROLE, USER1))
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (ROLE, USER2))
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (ROLE, USER3))
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (WORKSPACE_ROLE, USER1))
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (WORKSPACE_ROLE, USER2))
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (WORKSPACE_ROLE, USER3))

            conn.execute_ddl(GRANT_WITH_TRANSFORM_ATTR2_DDL % (PRIVACY_FN + '()'))

            res = scan_as_json(ctx, conn,
                               'SELECT * FROM %s.%s' % (DB, ALLTYPES_TABLE))
            self.assertTrue(res == ALLTYPES_RESULTS)

            # Verify that for authorize query, no seed is added to the privacy
            # function.
            authorized_sql = authorize_query(
                conn, 'SELECT * FROM %s.%s' % (DB, ALLTYPES_TABLE), USER1)
            expected = ("SELECT %s(bool_col) as bool_col, " +
                        "%s(tinyint_col) as tinyint_col, " +
                        "%s(smallint_col) as smallint_col, " +
                        "%s(int_col) as int_col, " +
                        "%s(bigint_col) as bigint_col, " +
                        "float_col, double_col, string_col, varchar_col, " +
                        "char_col, timestamp_col, decimal_col " +
                        "FROM test_privacy_db.alltypes") %\
                         (fn, fn, fn, fn, fn)
            self.assertEqual(authorized_sql, expected)

            # When executed against a table with a grant, should see the same thing
            # by default
            self._validate_query(ctx, conn,
                                 'SELECT * FROM %s.%s' % (DB, ALLTYPES_TABLE),
                                 equal_across_queries=stable, equal_across_users=stable,
                                 has_results=True)
            join_query = '''SELECT a.*, b.* FROM {db}.{table} a
                 JOIN {db}.{table} b ON a.bigint_col=b.bigint_col'''.format(
                     db=DB, table=ALLTYPES_TABLE)
            self._validate_query(ctx, conn, join_query, equal_across_queries=stable,
                                 equal_across_users=stable, has_results=stable)

            # Outer join should always return the outer table row even when there are
            # no matches but the other side should be null.
            join_query = '''SELECT a.*, b.bigint_col as be_null FROM {db}.{table} a
                 LEFT OUTER JOIN {db}.{table} b ON a.bigint_col=b.bigint_col'''.format(
                     db=DB, table=ALLTYPES_TABLE)
            null_col = 'be_null'
            if stable:
                null_col = None
            self._validate_query(ctx, conn, join_query, equal_across_queries=stable,
                                 equal_across_users=stable, has_results=True,
                                 null_col=null_col)

            # When executed against a view, should see the same thing by default
            self._validate_query(ctx, conn,
                                 'SELECT * FROM %s.%s' % (DB, ALLTYPES_PRIVACY_VIEW),
                                 equal_across_queries=stable, equal_across_users=stable,
                                 has_results=True)
            join_query = 'SELECT a.*, b.* FROM {db}.{table} a JOIN {db}.{table} b ON a.bigint_col=b.bigint_col'.format(
                db=DB, table=ALLTYPES_PRIVACY_VIEW)
            self._validate_query(ctx, conn, join_query,
                                 equal_across_queries=stable, equal_across_users=stable,
                                 has_results=stable)

            # When executed against a view with duplicate rows, each row should either
            # contain the same values if the function is stable, or not if it is not stable
            self._validate_query(ctx, conn,
                                 'SELECT * FROM %s.%s' % (DB, ALLTYPES_FIRST_ROW_DOUBLED_VIEW),
                                 equal_across_queries=stable, equal_across_users=stable, equal_across_rows=stable, has_results=True)

            # When executed against a view that is shared, should see the same thing by
            # default
            self._validate_query(ctx, conn,
                                 'SELECT * FROM %s.%s' % (DB, ALLTYPES_PRIVACY_SHARED_VIEW),
                                 equal_across_queries=stable, equal_across_users=stable,
                                 has_results=True)
            join_query = 'SELECT a.*, b.* FROM {db}.{table} a JOIN {db}.{table} b ON a.bigint_col=b.bigint_col'.format(
                db=DB, table=ALLTYPES_PRIVACY_SHARED_VIEW)
            self._validate_query(ctx, conn, join_query,
                                 equal_across_queries=stable, equal_across_users=stable,
                                 has_results=stable)

            # When executed against a view that is unique, should see the same thing
            # across runs but not across users
            self._validate_query(ctx, conn,
                                 'SELECT * FROM %s.%s' % (DB, ALLTYPES_PRIVACY_UNIQUE_VIEW),
                                 equal_across_queries=stable, equal_across_users=False, has_results=True)
            join_query = 'SELECT a.*, b.* FROM {db}.{table} a JOIN {db}.{table} b ON a.bigint_col=b.bigint_col'.format(
                db=DB, table=ALLTYPES_PRIVACY_UNIQUE_VIEW)
            self._validate_query(ctx, conn, join_query,
                                 equal_across_queries=stable, equal_across_users=False, has_results=stable)

            # Check referential integrity, which is dependent on which security function we use.
            # Note that the view is unique per user, so will never have the same results across users
            join_query = 'SELECT a.*, b.* FROM {db}.{table} a JOIN {db}.{table2} b ON a.bigint_col=b.bigint_col'.format(
                db=DB, table=ALLTYPES_PRIVACY_UNIQUE_VIEW1, table2=ALLTYPES_PRIVACY_UNIQUE_VIEW2)
            self._validate_query(ctx, conn, join_query,
                                 equal_across_queries=stable, equal_across_users=False, has_results=maintains_ref_integrity)

            # Check referential integrity, which is dependent on which security function we use.
            # Note that the view is shared for all users, so will have the same results across users
            join_query = 'SELECT a.*, b.* FROM {db}.{table} a JOIN {db}.{table2} b ON a.bigint_col=b.bigint_col'.format(
                db=DB, table=ALLTYPES_PRIVACY_SHARED_VIEW1, table2=ALLTYPES_PRIVACY_SHARED_VIEW2)
            self._validate_query(ctx, conn, join_query,
                                 equal_across_queries=stable, equal_across_users=maintains_ref_integrity, has_results=maintains_ref_integrity)

            # Check referential integrity, which is dependent on which security function we use.
            # This checks it across different parameters to the same privacy function, which means
            # there is no match.
            join_query = 'SELECT a.*, b.* FROM {db}.{table} a JOIN {db}.{table2} b ON a.bigint_col=b.bigint_col'.format(
                db=DB, table=ALLTYPES_PRIVACY_SHARED_VIEW1, table2=ALLTYPES_PRIVACY_UNIQUE_VIEW2)
            self._validate_query(ctx, conn, join_query,
                                 equal_across_queries=False, equal_across_users=False, has_results=False)

            # Test constant conversions - there's too much randomness here to check the actual
            # values consistently across all functions, but we can at least check to make sure
            # we don't error out.
            cols = []
            for col, expr in ALLTYPES_CONSTANT_VALUES.items():
                cols.append('%s(%s) as %s' % (fn, expr, col))
            query = 'SELECT %s' % (','.join(cols))
            self._validate_query(ctx, conn, query, check_results=False)

            for key, val in ALLTYPES_RESULTS[0].items():
                # These columns are too low cardinality to reliably pass
                if key in ['bool_col', 'tinyint_col']:
                    continue

                # We only transform some values in ALLTYPES_TABLE (via the transform policy),
                # and if we don't transform them, we do expect values to come back
                not_transformed = key not in ALLTYPES_TRANSFORMED_COLS
                if key in ALLTYPES_STRING_COLS:
                    val = '\'%s\'' % val
                # Check that the filter has tokenization applied on it properly
                join_query = 'SELECT * FROM {db}.{table} WHERE {key}={value}'.format(
                    db=DB, table=ALLTYPES_TABLE, key=key, value=val)
                self._validate_query(ctx, conn, join_query,
                                     equal_across_queries=stable, equal_across_users=stable, has_results=not_transformed)

                # Check that the aggregation has tokenization applied on it properly
                # Note that we explicitly reference one of the transform keys to ensure the result
                # set is appropriately stable/not stable
                join_query = 'SELECT {key}, {transformed_key}, max({key}) FROM {db}.{table} GROUP BY 1, 2 HAVING max({key})={value}'.format(
                    db=DB, table=ALLTYPES_TABLE, key=key, value=val, transformed_key='bigint_col')
                self._validate_query(ctx, conn, join_query,
                                     equal_across_queries=stable, equal_across_users=stable, has_results=not_transformed)

                # Check that the group by having has tokenization applied on it properly
                # Note that we explicitly reference one of the transform keys to ensure the result
                # set is appropriately stable/not stable
                join_query = 'SELECT {key}, {transformed_key}, count(*) FROM {db}.{table} GROUP BY 1, 2 HAVING {key}={value}'.format(
                    db=DB, table=ALLTYPES_TABLE, key=key, value=val, transformed_key='bigint_col')
                self._validate_query(ctx, conn, join_query,
                                     equal_across_queries=stable, equal_across_users=stable, has_results=not_transformed)

                # We can only do these checks if we have a format-preserving privacy function,
                # otherwise the comparison fails the type check in analysis, or we can do this
                # if the types are equivalent-ish, which we have encoded as whether we've transformed
                # this column in the transform grant.
                if maintains_type or key in ALLTYPES_TRANSFORMED_COLS:
                    # Check that you can't "detokenize" a value
                    join_query = 'SELECT * FROM {db}.{table} WHERE {key}={fn}({value})'.format(
                        db=DB, table=ALLTYPES_TABLE, fn=PRIVACY_FN, key=key, value=val)
                    self._validate_query(ctx, conn, join_query,
                                         equal_across_queries=False, equal_across_users=False, has_results=False)

                    join_query = 'SELECT * FROM {db}.{table} WHERE {key}={fn}({value}, signed_user(false))'.format(
                        db=DB, table=ALLTYPES_PRIVACY_SHARED_VIEW, fn=PRIVACY_FN, key=key, value=val)
                    self._validate_query(ctx, conn, join_query,
                                         equal_across_queries=False, equal_across_users=False, has_results=False)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_nfp_ref_tokenize(self):
        self._test_fn('nfp_ref_tokenize', maintains_ref_integrity=True, stable=True, maintains_type=False)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_nfp_noref_tokenize(self):
        self._test_fn('nfp_noref_tokenize', maintains_ref_integrity=False, stable=True, maintains_type=False)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_fp_ref_tokenize(self):
        self._test_fn('fp_ref_tokenize', maintains_ref_integrity=True, stable=True, maintains_type=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_fp_noref_tokenize(self):
        self._test_fn('fp_noref_tokenize', maintains_ref_integrity=False, stable=True, maintains_type=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_fpt(self):
        self._test_fn('fpt', maintains_ref_integrity=False, stable=True, maintains_type=True)

    def test_fpt_ref(self):
        self._test_fn('fpt_ref', maintains_ref_integrity=True, stable=True, maintains_type=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_tokenize_no_ref(self):
        self._test_fn('tokenize_no_ref', maintains_ref_integrity=False, stable=True, maintains_type=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_tokenize(self):
        self._test_fn('tokenize', maintains_ref_integrity=True, stable=True, maintains_type=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_fp_random(self):
        self._test_fn('fp_random', maintains_ref_integrity=False, stable=False, maintains_type=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_nfp_random(self):
        self._test_fn('fp_random', maintains_ref_integrity=False, stable=False, maintains_type=False)

if __name__ == "__main__":
    unittest.main()
