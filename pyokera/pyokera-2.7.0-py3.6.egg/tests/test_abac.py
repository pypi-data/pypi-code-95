# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for ABAC
#
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals

#+------+--------------------+----------------+--------+--------+---------+---------+---------+-------+
#| rpc  |        name        |      user      |  mean  |  50%   |   90%   |   99%   |   max   | iters |
#+------+--------------------+----------------+--------+--------+---------+---------+---------+-------+
#| many | access: db1.table1 | abac_test_user | 78.731 | 78.406 |  82.737 |  83.924 |  83.924 |   50  |
#| many | access: db1.table2 | abac_test_user | 79.571 | 78.101 |  87.006 |  89.063 |  89.063 |   50  |
#| many |  access: db1.view  | abac_test_user | 87.812 | 87.346 |  92.938 |  97.176 |  97.176 |   50  |
#| many |  access: db2.tbl1  | abac_test_user | 91.780 | 90.214 | 102.058 | 111.256 | 111.256 |   50  |
#| many |  access: db2.view  | abac_test_user | 89.705 | 88.350 |  96.189 | 100.211 | 100.211 |   50  |
#+------+--------------------+----------------+--------+--------+---------+---------+---------+-------+

import os
import time
import unittest

import pytest

from okera import _thrift_api
from okera.tests import pycerebro_test_common as common
from okera._thrift_api import TConfigType

upsert_config = common.upsert_config
list_configs = common.list_configs
delete_config = common.delete_config

TBLPROP_PARENTS = 'okera.view.parents'
TBLPROP_BASE = 'okera.view.base-tables'
TBLPROP_CHILDREN = 'okera.view.children'

TEST_DB = 'abac_test_db'
TEST_DB2 = 'abac_test_db2'
TEST_TBL = 'tbl'
TEST_TBL2 = 'tbl2'
TEST_DB_DROP = 'drop_db1'
TEST_TBL_DROP = 'drop_table1'
TEST_VIEW = 'v'
TEST_ROLE = 'abac_test_role'
TEST_USER = 'abac_test_user'
TEST_ROLE_DROP = 'abac_test_role_drop'
TEST_USER_DROP = 'abac_test_user_drop'
TEST_ADMIN_USER = 'abac_test_user_admin'

ENABLE_COMPLEX_TYPE_TAGS = False

PERF = common.PerfResults()

class AbacTest(common.TestBase):
    @classmethod
    def tearDownClass(cls):
        PERF.finalize_results()

    @staticmethod
    def __grant_abac_db(conn, db, namespace, key):
        conn.execute_ddl(
            'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
            (db, namespace, key, TEST_ROLE))

    @staticmethod
    def __grant_abac_tbl(conn, db, tbl, namespace, key):
        conn.execute_ddl(
            'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
            (db, tbl, namespace, key, TEST_ROLE))

    @staticmethod
    def __revoke_abac_db(conn, db, namespace, key):
        conn.execute_ddl(
            'REVOKE SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) FROM ROLE %s' %\
            (db, namespace, key, TEST_ROLE))

    @staticmethod
    def __revoke_abac_tbl(conn, db, tbl, namespace, key):
        conn.execute_ddl(
            'REVOKE SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) FROM ROLE %s' %\
            (db, tbl, namespace, key, TEST_ROLE))

    @staticmethod
    def __show_grant_abac_role(conn):
        return conn.execute_ddl('SHOW GRANT ROLE %s' % (TEST_ROLE))

    @staticmethod
    def __init_test_role(conn):
        conn.execute_ddl('DROP ROLE IF EXISTS %s'% 'abac_test_role')
        conn.execute_ddl('CREATE ROLE %s'% 'abac_test_role')
        conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % ('abac_test_role', TEST_USER))

    @staticmethod
    def __col_has_attribute(conn, db, tbl, col, attr_ns, attr_key):
        datasets = conn.list_datasets(db, name=tbl)

        assert len(datasets) == 1
        # TODO: handle nested columns
        columns = datasets[0].schema.cols

        for column in columns:
            if column.name == col:
                attrs = column.attribute_values
                if not attrs:
                    continue
                for attr in attrs:
                    if attr.attribute.attribute_namespace != attr_ns:
                        continue
                    if attr.attribute.key != attr_key:
                        continue

                    assert attr.attribute.attribute_namespace == attr_ns
                    assert attr.attribute.key == attr_key

                    return True

                return False

        return False

    def __verify_tbl_access(self, conn, db, tbl, num_cols, has_db_access=False,
                            skip_metadata_check=False, timeout=0):
        """ Verifies the current connect has access to num_cols on this table

            FIXME(BUG): skip_metadata_check should be removed (and always True). It is
            skipping due to existing bugs.
        """
        if num_cols == 0:
            for ddl in ['describe %s.%s', 'describe formatted %s.%s']:
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    print(conn.execute_ddl(ddl % (db, tbl)))
                self.assertTrue('does not have privilege' in str(ex_ctx.exception))

            if has_db_access:
                # User has access to DB, make sure table does not show up in list
                self.assertTrue('%s.%s' %(db, tbl) not in conn.list_dataset_names(db))
                names = conn.list_dataset_names(db)
                self.assertFalse('%s.%s' %(db, tbl) in names, msg=str(names))
            else:
                # Doesn't have database access, ensure listing tables in it fails
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    print("Listing datasets in: " + db)
                    print(conn.list_dataset_names(db))
                self.assertTrue('does not have privilege' in str(ex_ctx.exception))

                datasets = conn.list_datasets(db)
                self.assertEqual(len(datasets), 0, msg=str(datasets))

                for ddl in ['describe database %s', 'show tables in %s']:
                    with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                        print(conn.execute_ddl(ddl % db))
                    self.assertTrue('does not have privilege' in str(ex_ctx.exception))

                if not skip_metadata_check:
                    dbs = conn.list_databases()
                    self.assertFalse(TEST_DB in dbs, msg=str(dbs))
        else:
            dbs = conn.list_databases()
            self.assertTrue(db in dbs, msg=str(dbs))
            names = conn.list_dataset_names(db)
            self.assertTrue('%s.%s' %(db, tbl) in names, msg=str(names))
            datasets = conn.list_datasets(db, name=tbl)
            self.assertEqual(len(datasets), 1)
            cols = self._visible_cols(conn.list_datasets(db, name=tbl)[0].schema.cols)
            self.assertEqual(len(cols), num_cols)

            datasets = conn.list_datasets(db)
            self.assertTrue(len(datasets) >= 1, msg=str(datasets))

            # Now do a select star and verify the right number of columns are expanded
            start = time.perf_counter()
            schema = conn.plan('SELECT * FROM %s.%s' % (db, tbl)).schema
            end = time.perf_counter()
            if schema.nested_cols:
                cols = schema.nested_cols
            else:
                cols = schema.cols
            self.assertEqual(self._top_level_columns(cols), num_cols, msg=str(cols))
            if timeout > 0:
                self.assertLess(end - start, timeout)

    @staticmethod
    def __verify_column_has_tag(tbl, col_name, tag):
        cols = {}
        for col in tbl.schema.cols:
            if not col.attribute_values:
                continue
            for attr_value in col.attribute_values:
                col = attr_value.column
                attr = '%s.%s' % (attr_value.attribute.attribute_namespace, attr_value.attribute.key)

                col_attrs = cols.get(col, list())
                col_attrs.append(attr)
                cols[col] = col_attrs

        return col_name in cols and tag in cols[col_name]

    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(AbacTest, cls).setUpClass()
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.delete_attribute('abac_test', 'v1')
            conn.create_attribute('abac_test', 'v1')
            conn.delete_attribute('abac_test', 'v2')
            conn.create_attribute('abac_test', 'v2')
            conn.delete_attribute('abac_test', 'v3')
            conn.create_attribute('abac_test', 'v3')
            conn.delete_attribute('abac_test', 'pii')
            conn.create_attribute('abac_test', 'pii')
            conn.delete_attribute('abac_test', 'email')
            conn.create_attribute('abac_test', 'email')
            conn.delete_attribute('abac_test', 'sales')
            conn.create_attribute('abac_test', 'sales')
            conn.delete_attribute('abac_test', 'marketing')
            conn.create_attribute('abac_test', 'marketing')

    @staticmethod
    def __cleanup(conn, dbs=None):
        """ Cleanups all the test state used in this test to "reset" the catalog.
            dbs can be specified to do the initialize over multiple databases.
            This can be used for tests that use multiple dbs (but makes the test
            take longer). By default, only load TEST_DB.
        """
        conn.execute_ddl("DROP ROLE IF EXISTS %s" % TEST_ROLE)
        conn.execute_ddl("CREATE ROLE %s" % TEST_ROLE)
        conn.execute_ddl("GRANT ROLE %s to GROUP %s" % (TEST_ROLE, TEST_USER))

        # Always drop both to prevent state from leaking
        conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % TEST_DB)
        conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % TEST_DB2)

        if not dbs:
            dbs = [TEST_DB]

        for db in dbs:
            conn.execute_ddl("CREATE DATABASE %s" % db)
            conn.execute_ddl("CREATE TABLE %s.%s(col1 int, col2 int, col3 int)" % \
                (db, TEST_TBL))
            conn.execute_ddl("CREATE TABLE %s.%s(col1 int, col2 int, col3 int)" % \
                (db, TEST_TBL2))
            conn.execute_ddl("CREATE VIEW %s.%s AS SELECT * FROM %s.%s" % \
                (db, TEST_VIEW, TEST_DB, TEST_TBL))

    @staticmethod
    def __revoke(conn, sql):
        """ Revokes a grant, transforming a GRANT statement to its corresponding REVOKE"""
        sql = sql.lower()
        sql = sql.replace('grant', 'revoke')
        sql = sql.replace('to role', 'from role')
        conn.execute_ddl(sql)

    @staticmethod
    def __fixture1(conn):
        """ Creates a representative test fixture. This will:
              Tag TEST_DB with department sales
              Tag TEST_DB2 with department marketing.
              Tag TEST_DB2.TEST_TBL with department sales.
              Tag some columns with pii tags, and some with another tag and a third
              column with no tags.
        """
        conn.assign_attribute('abac_test', 'sales', TEST_DB)
        conn.assign_attribute('abac_test', 'marketing', TEST_DB2)
        conn.assign_attribute('abac_test', 'sales', TEST_DB2, TEST_TBL)

        for db in [TEST_DB, TEST_DB2]:
            conn.assign_attribute('abac_test', 'pii', db, TEST_TBL, 'col1')
            conn.assign_attribute('abac_test', 'pii', db, TEST_TBL2, 'col1')

            # If cascading is on, then the above grant will auto-cascade to the view, but
            # if it isn't on, we need to assign it manually.
            has_col_attr = AbacTest.__col_has_attribute(
                conn, db, TEST_VIEW, 'col1', 'abac_test', 'pii')
            if not has_col_attr:
                conn.assign_attribute('abac_test', 'pii', db, TEST_VIEW, 'col1')

            conn.assign_attribute('abac_test', 'v1', db, TEST_TBL, 'col2')
            conn.assign_attribute('abac_test', 'v1', db, TEST_TBL2, 'col2')

            # If cascading is on, then the above grant will auto-cascade to the view, but
            # if it isn't on, we need to assign it manually.
            has_col_attr = AbacTest.__col_has_attribute(
                conn, db, TEST_VIEW, 'col2', 'abac_test', 'v1')
            if not has_col_attr:
                conn.assign_attribute('abac_test', 'v1', db, TEST_VIEW, 'col2')

    # Tests that grants are case insensitive for catalog objects, attributes and exprs.
    def test_case_insensitive_exprs(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            # Grant with all lower case
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                (TEST_DB, 'abac_test', 'v1', TEST_ROLE))

            # Try some duplicates, they should all fail
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB, 'abac_test.v1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB, 'abac_TEST.v1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'not abac_test.v1', TEST_ROLE))
            self.assertTrue('Another grant with' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'Abac_test', 'v1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'NOT Abac_test.V1', TEST_ROLE))
            self.assertTrue('Another grant with' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'Abac_test', 'V1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))

    def test_in_print(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            # Grant with all lower case
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE IN(%s.%s) TO ROLE %s' %\
                (TEST_DB, 'abac_test', 'v1', TEST_ROLE))
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE NOT IN(%s.%s) TO ROLE %s' %\
                (TEST_DB, 'abac_test', 'v2', TEST_ROLE))

            result = conn.execute_ddl('SHOW GRANT ROLE %s' % TEST_ROLE)
            self.assertEqual(2, len(result))
            for r in result:
                expr = r[6]
                self.assertFalse('null' in expr)

    def test_db(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)

            # Admin should see it but test user should not
            self.assertTrue(TEST_DB in conn.list_databases())
            ctx.enable_token_auth(token_str=TEST_USER)
            self.assertTrue('okera_sample' in conn.list_databases())
            self.assertFalse(TEST_DB in conn.list_databases())

            # Switch back to admin and assign abac_test.v1 to this db
            ctx.disable_auth()
            self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')

            # Test user should not have access to this DB but currently does.
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)

            # Assign the attribute
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v1', TEST_DB)

            # List databases again, test user should have access now
            self.assertTrue(TEST_DB in conn.list_databases())
            ctx.enable_token_auth(token_str=TEST_USER)
            self.assertTrue('okera_sample' in conn.list_databases())
            self.assertTrue(TEST_DB in conn.list_databases())

            # Should have full access to both tables
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 3)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)
            self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 3)

    def test_tbl_view(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # Admin should see it but test user should not
                self.assertTrue(
                    '%s.%s' %(TEST_DB, ds) in conn.list_dataset_names(TEST_DB))
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                # Switch back to admin and assign abac_test.v1 to this dataset
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds)
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                # List tables again, test user should have access now
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)

                # Unassign the attribute, testuser should not see it anymore
                ctx.disable_auth()
                conn.unassign_attribute('abac_test', 'v1', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                # Assign the attribute again but revoke the grant, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds)
                self.__revoke_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    def test_col(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # Verify no access to start
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 0)

                # Switch back to admin and assign abac_test.v1 to just one column and
                # issue the grant.
                ctx.disable_auth()
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                self.assertTrue(
                    '%s.%s' %(TEST_DB, ds) in conn.list_dataset_names(TEST_DB))

                # Verify user can just see one column on this one table
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 1)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Assign attribute to other column
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')

                # Now should be able to see both.
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 2)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Unassign one attribute
                ctx.disable_auth()
                conn.unassign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 1)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Unassign other
                ctx.disable_auth()
                conn.unassign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

                # Revoke the grant
                ctx.disable_auth()
                self.__revoke_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

    def test_attr(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for expr in ['abac_test.v1', 'in(abac_test.v1)',
                         'in(abac_test.v2, abac_test.v1)']:
                for ds in [TEST_TBL, TEST_VIEW]:
                    ctx.disable_auth()
                    self.__cleanup(conn)

                    # No tags, user can none
                    conn.execute_ddl(
                        'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE %s TO ROLE %s' %\
                        (TEST_DB, ds, expr, TEST_ROLE))
                    ctx.disable_auth()
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                    # Assign attribute to one column, user can see 1
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 1)

                    # Assign attribute to second column, user can see 2
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 2)

                    # Assign attribute to last column, user can see all 3
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col3')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 3)

    def test_not(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for expr in ['not abac_test.v1', 'not in(abac_test.v1)',
                         'not in(abac_test.v2, abac_test.v1)',
                         'not not not abac_test.v1']:
                for ds in [TEST_TBL, TEST_VIEW]:
                    ctx.disable_auth()
                    self.__cleanup(conn)

                    # No tags, user can see all 3
                    conn.execute_ddl(
                        'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE %s TO ROLE %s' %\
                        (TEST_DB, ds, expr, TEST_ROLE))
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 3)

                    # Assign attribute to one column, user can see 2
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 2)

                    # Assign attribute to second column, user can see 1
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 1)

                    # Assign attribute to last column, user cannot see
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col3')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    # Verify abac privileges for role are removed when role is dropped
    def test_drop_role(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # grant attribute privileges to role
                conn.assign_attribute('abac_test', 'v1', TEST_DB)
                self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')

                # Ensure 2 privileges
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 2)

                conn.execute_ddl("DROP ROLE %s" % TEST_ROLE)
                conn.execute_ddl("CREATE ROLE %s" % TEST_ROLE)

                # Ensure 0 privileges
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 0)
                conn.execute_ddl("DROP ROLE %s" % TEST_ROLE)

    def test_show(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)
                admin_before_count = self._ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON CATALOG')
                self.assertEqual(0, self._ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON DATABASE %s' % TEST_DB))
                self.assertEqual(0, self._ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON TABLE %s.%s' % \
                        (TEST_DB, ds)))
                self.assertEqual(0, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON CATALOG' % TEST_ROLE))

                # Issue some grants, make sure they show correctly
                self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')

                self.assertEqual(admin_before_count + 2, self._ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON CATALOG'))
                self.assertEqual(2, self._ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON DATABASE %s' % TEST_DB))
                self.assertEqual(1, self._ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON TABLE %s.%s' % \
                    (TEST_DB, ds)))
                self.assertEqual(
                    self._ddl_count(conn, 'SHOW GRANT ROLE %s' % TEST_ROLE), 2)
                self.assertEqual(2, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON CATALOG' % TEST_ROLE))
                self.assertEqual(2, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON DATABASE %s' % (TEST_ROLE, TEST_DB)))
                self.assertEqual(1, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))
                self.assertEqual(0, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON DATABASE %s' % \
                    (TEST_ROLE, 'okera_sample')))
                self.assertEqual(0, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, 'okera_sample', 'users')))

    def test_show_multiple_grants(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL]:
                ctx.disable_auth()
                self.__cleanup(conn)

                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v2')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v3')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'sales')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'marketing')

                self.assertEqual(5, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_literal_expression(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # Attribute expression without '='
                conn.execute_ddl(
                    'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                    (TEST_DB, ds, 'abac_test', 'v1', TEST_ROLE))
                self.assertEqual(1, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds)

                # List tables as test user
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Not expression
                ctx.disable_auth()
                conn.execute_ddl(
                    'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(!%s.%s) TO ROLE %s' %\
                    (TEST_DB, TEST_TBL2, 'abac_test', 'v2', TEST_ROLE))
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Revoke one of them
                ctx.disable_auth()
                conn.execute_ddl(
                    'REVOKE SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) FROM ROLE %s' %\
                    (TEST_DB, ds, 'abac_test', 'v1', TEST_ROLE))
                self.assertEqual(0, self._ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, has_db_access=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Revoke other one
                ctx.disable_auth()
                conn.execute_ddl(
                    ('REVOKE SELECT ON TABLE %s.%s HAVING ATTRIBUTE(!%s.%s) ' +\
                    'FROM ROLE %s') %\
                    (TEST_DB, TEST_TBL2, 'abac_test', 'v2', TEST_ROLE))
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

    def test_table_column_and_not_and(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)

            # Grant with and AND of ORs
            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_TBL,
                 'abac_test.v1=true and (abac_test.v2 != true and abac_test.v3 != true)',
                 TEST_ROLE))

            # Assign v1, should see both columns
            conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL)
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 3)

            # Tag one of the columns with v2, it should be hidden now
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col1')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 2)

            # Tag the other column with the other tag, both should be hidden
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v3', TEST_DB, TEST_TBL, 'col2')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

    def test_table_column_and_or(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)

            # Assign abac_test.v1 to this table
            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_TBL,
                 'abac_test.v1 and IN (abac_test.v2, abac_test.v3)',
                 TEST_ROLE))

            # Should see nothing
            conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL)
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)

            # Tag one of the columns with v2, it should be hidden now
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col1')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

            # Tag the other column with the other tag, both should be visible
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v3', TEST_DB, TEST_TBL, 'col2')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 2)

            # Unassign one of the columns with v2, it should be hidden now
            ctx.disable_auth()
            conn.unassign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col1')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

            # Unassign other columns with v1, it should be hidden now
            ctx.disable_auth()
            conn.unassign_attribute('abac_test', 'v3', TEST_DB, TEST_TBL, 'col2')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)

    def test_das_3117(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # grant != pii at the view level
                conn.execute_ddl(
                    'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB, ds, 'not abac_test.pii', TEST_ROLE))
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)

                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    def test_das_3119(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            # Assign the attribute to a col on the table and view
            conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_TBL, 'col1')

            # If cascading is on, then the above grant will auto-cascade to the view, but
            # if it isn't on, we need to assign it manually.
            has_col_attr = AbacTest.__col_has_attribute(
                conn, TEST_DB, TEST_VIEW, 'col1', 'abac_test', 'pii')
            if not has_col_attr:
                conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_VIEW, 'col1')

            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAS ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_TBL, 'abac_test.pii', TEST_ROLE))
            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAS ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_VIEW, 'abac_test.pii', TEST_ROLE))

            # User should have access to this column on both
            ctx.enable_token_auth(token_str=TEST_USER)

            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)
            self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 1)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_grant1(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +\
                    'abac_test.SALES AND NOT abac_test.PII TO ROLE %s') %\
                    (TEST_DB, ds, TEST_ROLE))

                # Should not have any access
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                # Just assign sales
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Also assign PII, now should have no access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_grant2(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN (abac_test.pii) TO ROLE %s') %\
                    (TEST_DB, TEST_ROLE))

                # Should not have any access
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one, now should not have access to that one
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, has_db_access=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to the other, now should have no access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_grant3(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) AND ' +\
                    'NOT abac_test.PII AND NOT abac_test.v1 TO ROLE %s') %\
                    (TEST_DB, TEST_ROLE))

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one and v1 to the other, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_grant4(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN(abac_test.PII, abac_test.v1) TO ROLE %s') % \
                    (TEST_DB, TEST_ROLE))

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one and v1 to the other, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0,
                                         skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_grant5(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN(abac_test.PII, abac_test.v1) TO ROLE %s') % \
                    (TEST_ROLE))

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one and v1 to the other, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)

                self.__verify_tbl_access(conn, TEST_DB, ds, 0,
                                         skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_grant6(self):
        grants = []
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            '(NOT abac_test.PII OR NOT abac_test.email) TO ROLE %s') % \
            (TEST_ROLE))
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            'NOT (abac_test.PII AND abac_test.email) TO ROLE %s') % \
            (TEST_ROLE))

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                for sql in grants:
                    ctx.disable_auth()
                    self.__cleanup(conn)

                    conn.execute_ddl(sql)

                    # Assign sales to one and marketing to another, should have both
                    conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                    conn.assign_attribute('abac_test', 'pii', TEST_DB, ds, 'col1')
                    conn.assign_attribute('abac_test', 'pii', TEST_DB, ds, 'col2')
                    conn.assign_attribute('abac_test', 'email', TEST_DB, ds, 'col2')
                    conn.assign_attribute('abac_test', 'email', TEST_DB, ds, 'col3')

                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 2)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_grant7(self):
        # Regression test for DAS-2928
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN(abac_test.PII, abac_test.EMAIL) TO ROLE %s') % \
                    (TEST_ROLE))

                # Assign sales to the table
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)

                # Assign PII to one and email to two different columns. These columns
                # should be hidden but the third column should be visible
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds, 'col1')
                conn.assign_attribute('abac_test', 'email', TEST_DB, ds, 'col2')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 1)

    def test_das_3122(self):
        # grant attribute privileges for database to be removed
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            conn.assign_attribute('abac_test', 'v1', TEST_DB)
            self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
            result = self.__show_grant_abac_role(conn)
            self.assertEqual(len(result), 1)

            # Drop and ensure privilege is removed
            conn.execute_ddl("DROP DATABASE %s CASCADE INCLUDING PERMISSIONS " %\
                             TEST_DB)
            result = self.__show_grant_abac_role(conn)
            self.assertEqual(len(result), 0)

    def test_das_3122_tbl(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                TV = 'TABLE'
                if ds == TEST_VIEW:
                    TV = 'VIEW'

                # grant attribute privileges for table to be removed
                conn.assign_attribute('abac_test', 'v1', TEST_DB)
                self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')

                # Ensure privileges for db and table
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 2)
                self.assertTrue("database" in result[0][0])
                self.assertTrue("table" in result[1][0])

                conn.execute_ddl("DROP %s %s.%s INCLUDING PERMISSIONS" %\
                                 (TV, TEST_DB, ds))

                # Ensure privilege for DB only. Table privilege should have been dropped.
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 1)
                self.assertTrue("database" in result[0][0])

    @unittest.skipIf(common.test_level_lt('checkin') and not PERF.run_perf(),
                     "Skipping below checkin test level")
    @pytest.mark.perf
    def test_fixture(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()
            self.__cleanup(conn, [TEST_DB, TEST_DB2])
            self.__fixture1(conn)

            # Grants that should all result in the same policies for these tests.
            grants = []
            grants.append(
                [('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES=true) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES!=false) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_DB, TEST_ROLE),
                 ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                 (TEST_DB2, TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_DB, TEST_ROLE),
                 ('GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                 (TEST_DB2, TEST_TBL, TEST_ROLE)])

            for grant in grants:
                for sql in grant:
                    conn.execute_ddl(sql)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 2)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 2)
                self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 2)
                self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL, 2)
                self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL2, 0, has_db_access=True)
                self.__verify_tbl_access(conn, TEST_DB2, TEST_VIEW, 0, has_db_access=True)

                ctx.disable_auth()
                for sql in grant:
                    self.__revoke(conn, sql)

            # Grant access to (sales and pii) or (marketing and v1)
            conn.execute_ddl(
                ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'abac_test.SALES and abac_test.pii OR ' +\
                'abac_test.MARKETING and abac_test.v1 ' +\
                'TO ROLE %s') % (TEST_ROLE))
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 1)
            self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 1)
            self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL, 2)
            self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL2, 1)
            self.__verify_tbl_access(conn, TEST_DB2, TEST_VIEW, 1)

            PERF.measure(lambda: self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1),
                          'access: db1.table1', TEST_USER, 'many')
            PERF.measure(lambda: self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 1),
                          'access: db1.table2', TEST_USER, 'many')
            PERF.measure(lambda: self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 1),
                          'access: db1.view', TEST_USER, 'many')
            PERF.measure(lambda: self.__verify_tbl_access(conn, TEST_DB2, TEST_VIEW, 1),
                          'access: db2.tbl1', TEST_USER, 'many')
            PERF.measure(lambda: self.__verify_tbl_access(conn, TEST_DB2, TEST_VIEW, 1),
                          'access: db2.view', TEST_USER, 'many')

    def test_white_list(self):
        # Test with a pii tag on the table and then white list on columns
        grants = []
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            'abac_test.SALES and ' + \
            '(not abac_test.pii OR abac_test.v1 or abac_test.v2) ' +\
            'TO ROLE %s') % (TEST_ROLE))
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            'abac_test.SALES and ' + \
            'not (abac_test.pii and not abac_test.v1 and not abac_test.v2) ' +\
            'TO ROLE %s') % (TEST_ROLE))

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for sql in grants:
                ctx.disable_auth()
                self.__cleanup(conn, [TEST_DB, TEST_DB2])

                # Creates a representative test fixture. This will:
                # Tag TEST_DB with department sales
                # Tag TEST_DB.TEST_TBL with pii tags.
                conn.assign_attribute('abac_test', 'sales', TEST_DB)
                conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_TBL)

                # Issue the grant
                conn.execute_ddl(sql)

                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0, has_db_access=True)

                # Tag some of the columns with non-pii tags.
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL, 'col1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

                # Tag some of the columns with non-pii tags.
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col2')
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL, 'col3')
                conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col3')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 3)

    def test_get_access_permissions(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE abac_test.v1 ' +
                'TO ROLE %s;') % (TEST_DB, TEST_TBL, TEST_ROLE))
            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +
                'abac_test.v2 TO ROLE %s;') % (TEST_DB, TEST_TBL2, TEST_ROLE))
            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +
                'abac_test.v3 TO ROLE %s;') % (TEST_DB, TEST_TBL2, TEST_ROLE))
            # Add a safeguard policy to check that it does not break the
            # permission computation.
            conn.execute_ddl((
                'RESTRICT SELECT ON CATALOG WHERE 1!=1 ' +
                'FROM ROLE %s;') % (TEST_ROLE))

            # Test that TEST_DB.TEST_TBL has expected attribute expressions
            params = _thrift_api.TGetAccessPermissionsParams()
            params.users_or_groups = []
            params.database = TEST_DB
            params.filter = TEST_TBL
            #pylint: disable=protected-access
            permissions = \
                conn._underlying_client().GetAccessPermissions(params).permissions
            #pylint: enable=protected-access
            test_role_permissions = [
                perm for perm in permissions
                if perm.database == TEST_DB and perm.table == TEST_TBL]
            self.assertEqual(len(test_role_permissions), 1)
            self.assertEqual(len(test_role_permissions[0].attribute_expression), 1)
            self.assertEqual(
                test_role_permissions[0].attribute_expression[0].__dict__,
                {
                    'role_name' : TEST_ROLE,
                    'expression' : 'abac_test.v1'})

            # Test that TEST_DB.TEST_TBL2 has expected attribute expressions
            params = _thrift_api.TGetAccessPermissionsParams()
            params.users_or_groups = []
            params.database = TEST_DB
            params.filter = TEST_TBL2
            #pylint: disable=protected-access
            permissions = \
                conn._underlying_client().GetAccessPermissions(params).permissions
            #pylint: enable=protected-access
            test_role_permissions = [
                perm for perm in permissions
                if perm.database == TEST_DB and perm.table == TEST_TBL2]
            self.assertEqual(len(test_role_permissions), 2)
            self.assertEqual(len(test_role_permissions[0].attribute_expression), 1)
            self.assertEqual(len(test_role_permissions[1].attribute_expression), 1)

            roles = [
                exp.role_name
                for exp in test_role_permissions[0].attribute_expression]
            roles = roles + [
                exp.role_name
                for exp in test_role_permissions[1].attribute_expression]
            expressions = [
                exp.expression for exp in test_role_permissions[0].attribute_expression]
            expressions = expressions + [
                exp.expression for exp in test_role_permissions[1].attribute_expression]

            self.assertEqual(set(roles), set([TEST_ROLE]))
            self.assertEqual(set(expressions), set(['abac_test.v2', 'abac_test.v3']))

    def test_drop_db(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()

            # Create our desired state of a single DB and table in it and a unique
            # role and user
            conn.execute_ddl("DROP TABLE IF EXISTS %s.%s" % (TEST_DB_DROP, TEST_TBL_DROP))
            conn.execute_ddl("DROP DATABASE IF EXISTS %s" % (TEST_DB_DROP))
            conn.execute_ddl("CREATE DATABASE %s" % (TEST_DB_DROP))
            conn.execute_ddl("CREATE TABLE %s.%s (i int)" % (TEST_DB_DROP, TEST_TBL_DROP))
            conn.execute_ddl("DROP ROLE IF EXISTS %s" % (TEST_ROLE_DROP))
            conn.execute_ddl("CREATE ROLE %s" % (TEST_ROLE_DROP))
            conn.execute_ddl("GRANT ROLE %s to GROUP %s"
                             % (TEST_ROLE_DROP, TEST_USER_DROP))

            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE NOT IN (abac_test.v1) ' +
                'TO ROLE %s;') % (TEST_DB_DROP, TEST_TBL_DROP, TEST_ROLE_DROP))

            # Assign the tag to the table
            conn.assign_attribute('abac_test', 'pii', TEST_DB_DROP, TEST_TBL_DROP)

            # Ensure 'show databases' works for admin
            dbs = [db[0] for db in conn.execute_ddl('show databases')]
            self.assertTrue(TEST_DB_DROP in dbs)

            ctx.enable_token_auth(token_str=TEST_USER_DROP)

            # Ensure 'show databases' works for test user
            dbs = [db[0] for db in conn.execute_ddl('show databases')]
            self.assertTrue(TEST_DB_DROP in dbs)

            ctx.disable_auth()

            # Drop the DB and table
            conn.execute_ddl("DROP TABLE IF EXISTS %s.%s" % (TEST_DB_DROP, TEST_TBL_DROP))
            conn.execute_ddl("DROP DATABASE IF EXISTS %s" % (TEST_DB_DROP))

            ctx.enable_token_auth(token_str=TEST_USER_DROP)

            # Ensure 'show databases' works for test user (db shouldn't be there)
            dbs = [db[0] for db in conn.execute_ddl('show databases')]
            self.assertTrue(TEST_DB_DROP not in dbs)

    def test_complex_invalid_path(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Path doesn't exist, should error
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(\
                    ('GRANT SELECT(s1.not_a_col) ON TABLE rs_complex.struct_t_view ' +\
                     'TO ROLE %s') % TEST_ROLE)
            self.assertTrue(
                'Verify that both table and columns exist' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(\
                    ('GRANT SELECT(s1.f1.f2) ON TABLE rs_complex.struct_t_view ' +\
                     'TO ROLE %s') % TEST_ROLE)
            self.assertTrue(
                'Verify that both table and columns exist' in str(ex_ctx.exception))

    def test_complex_types_view(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            if ENABLE_COMPLEX_TYPE_TAGS:
                conn.assign_attribute('abac_test', 'v1', 'rs_complex',
                                      'struct_t_view', 's1.f1')
                conn.assign_attribute('abac_test', 'v1', 'rs_complex',
                                      'struct_t_view', 's1.f2')
            else:
                conn.assign_attribute('abac_test', 'v1', 'rs_complex',
                                      'struct_t_view', 's1')

            conn.execute_ddl(\
                ('GRANT SELECT ON TABLE rs_complex.struct_t_view HAVING ATTRIBUTE ' +\
                'not in (abac_test.v1) TO ROLE %s') % (TEST_ROLE))

            # Ensure privileges for db and table
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, 'rs_complex', 'struct_t_view', 1)

    @unittest.skipIf(common.test_level_lt('checkin'), "Skipping below checkin test level")
    def test_wide_view(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            conn.assign_attribute(
                'abac_test', 'v1',
                'customer', 'web_rawhits_standard_view', 'hit_time_gmt')
            conn.execute_ddl(\
                ('GRANT SELECT ON database customer HAVING ATTRIBUTE ' +\
                'not in (abac_test.v1) TO ROLE %s') % (TEST_ROLE))

            # Ensure privileges for db and table
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(
                conn, 'customer', 'web_rawhits_standard_view', 892, timeout=10)

    def test_transform_basic(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__init_test_role(conn)
            conn.create_attribute('abac_test', 'v1')
            conn.execute_ddl('GRANT SELECT ON CATALOG HAVING ATTRIBUTE abac_test.v1 ' +
                             'TRANSFORM abac_test.v1 WITH tokenize() ' +
                             'TO ROLE abac_test_role')

            conn.assign_attribute('abac_test', 'v1', 'okera_system',
                                  'group_names', 'group_name')
            # Should have tags
            ds = conn.list_datasets('okera_system', name='group_names')[0]
            self.assertTrue(ds.attribute_values is None)

    def test_transform_core(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            self.__init_test_role(conn)

            # Grant to just email in the clear and mask the credit card number
            conn.execute_ddl('GRANT SELECT ON DATABASE abac_db HAVING ATTRIBUTE IN ' +
                             '(pii.ip_address, pii.credit_card, pii.email_address) ' +
                             'TRANSFORM pii.credit_card WITH mask_ccn(__COLUMN__) ' +
                             'TRANSFORM pii.email_address WITH mask() ' +
                             'TO ROLE abac_test_role')

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('abac_db.user_account_data')[0]
            self.assertEqual(4, len(result))
            self.assertEqual('185.247.200.252', result['ipv4_address'])
            self.assertEqual('d646:af6:16d9:5a46:72c0:9a90:d78f:24e7',
                             result['ipv6_address'])
            self.assertEqual('XXXXXXXXXXXXXXX5516', result['creditcardnumber'])
            self.assertEqual('XXXXXX.XXXX@XXXX.XX', result['email'])

            # Try on the view.
            result = conn.scan_as_json('abac_db.user_account_data_view')[0]
            self.assertEqual(4, len(result))
            self.assertEqual('185.247.200.252', result['ipv4_address'])
            self.assertEqual('d646:af6:16d9:5a46:72c0:9a90:d78f:24e7',
                             result['ipv6_address'])
            self.assertEqual('XXXXXXXXXXXXXXX5516', result['creditcardnumber'])
            self.assertEqual('XXXXXX.XXXX@XXXX.XX', result['email'])

    def test_transform_compound_expr(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            self.__init_test_role(conn)

            # Grant to just email in the clear and mask the credit card number
            conn.execute_ddl('GRANT SELECT ON DATABASE abac_db HAVING ATTRIBUTE IN ' +
                             '(pii.ip_address, pii.email_address) ' +
                             'TRANSFORM pii.email_address WITH lower(mask(__COLUMN__)) ' +
                             'TO ROLE abac_test_role')

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('abac_db.user_account_data')[0]
            self.assertEqual(3, len(result))
            self.assertEqual('xxxxxx.xxxx@xxxx.xx', result['email'])

    def test_transform_user_attribute(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            conn.unassign_attribute('abac_test', 'v1', 'abac_db', 'user_attribute_test')
            self.__init_test_role(conn)

            # Grant where user attribute matches column
            conn.execute_ddl('GRANT SELECT ON DATABASE abac_db ' +
                             'WHERE user_attribute("whoami") = attr ' +
                             'TO ROLE abac_test_role')

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('abac_db.user_attribute_test')
            self.assertEqual(1, len(result))
            self.assertEqual(TEST_USER, result[0]['name'])

            # Set a new policy that also adds a table attribute
            ctx.disable_auth()
            conn.execute_ddl('REVOKE SELECT ON DATABASE abac_db ' +
                             'WHERE user_attribute("whoami") = attr ' +
                             'FROM ROLE abac_test_role')
            conn.execute_ddl('GRANT SELECT ON DATABASE abac_db ' +
                             'WHERE user_attribute("whoami") = attr ' +
                             'AND table_attribute("abac_test.v1") IS NOT NULL ' +
                             'TO ROLE abac_test_role')

            # Should still work for admin
            result = conn.scan_as_json('abac_db.user_attribute_test')
            self.assertEqual(3, len(result))
            self.assertEqual('hello', result[0]['name'])
            self.assertEqual('testuser', result[1]['name'])
            self.assertEqual(TEST_USER, result[2]['name'])

            # Table is not tagged, should fail for test user
            ctx.enable_token_auth(token_str=TEST_USER)
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                result = conn.scan_as_json('abac_db.user_attribute_test')
            self.assertTrue('Access to this dataset is' in str(ex_ctx.exception))

            # Add table tag, should be accessible to test user now.
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v1', 'abac_db', 'user_attribute_test')

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('abac_db.user_attribute_test')
            self.assertEqual(1, len(result))
            self.assertEqual(TEST_USER, result[0]['name'])

    def test_transform_core_all_types(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            self.__init_test_role(conn)

            conn.execute_ddl('GRANT SELECT ON DATABASE abac_db HAVING ATTRIBUTE ' +
                             'IN (abac.int_col) ' +
                             'TRANSFORM abac.int_col WITH tokenize() ' +
                             'TO ROLE abac_test_role')

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('abac_db.all_types')[0]
            self.assertEqual(4, len(result))
            self.assertEqual(102, result['tinyint_col'])
            self.assertEqual(22971, result['smallint_col'])
            self.assertEqual(733288971, result['int_col'])
            self.assertEqual(7333064010443628721, result['bigint_col'])

            # Now try the view
            result = conn.scan_as_json('abac_db.all_types_view')[0]
            self.assertEqual(4, len(result))
            self.assertEqual(110, result['tinyint_col'])
            self.assertEqual(24217, result['smallint_col'])
            self.assertEqual(733288971, result['int_col'])
            self.assertEqual(7333064010443628721, result['bigint_col'])

    def test_transform_filter_core(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            self.__init_test_role(conn)

            # Grant to just email in the clear and mask the credit card number
            conn.execute_ddl('GRANT SELECT ON DATABASE abac_db HAVING ATTRIBUTE IN ' +
                             '(pii.ip_address, abac.string_col) ' +
                             'EXCEPT TRANSFORM pii.credit_card WITH mask_ccn() ' +
                             'EXCEPT TRANSFORM pii.email_address WITH mask() ' +
                             'WHERE ipv4_address like "185%" '
                             'TO ROLE abac_test_role')

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('abac_db.user_account_data')
            self.assertEqual(2, len(result))
            self.assertEqual('185.247.200.252', result[0]['ipv4_address'])
            self.assertEqual('d646:af6:16d9:5a46:72c0:9a90:d78f:24e7',
                             result[0]['ipv6_address'])
            self.assertEqual('XXXXXXXXXXXXXXX5516', result[0]['creditcardnumber'])
            self.assertEqual('XXXXXX.XXXX@XXXX.XX', result[0]['email'])
            self.assertEqual('185.181.192.251', result[1]['ipv4_address'])
            self.assertEqual('e2c8:4a45:6dd9:2fd5:6c42:b81f:12ec:394e',
                             result[1]['ipv6_address'])
            self.assertEqual('XXXXXXXXXXXXXXX5825', result[1]['creditcardnumber'])
            self.assertEqual('XXX.XXXXXXXXX.XXXXX@XXXXXXXXXXXXX.XXX', result[1]['email'])

            # Now try the view
            result = conn.scan_as_json('abac_db.user_account_data_view')
            self.assertEqual(2, len(result))
            self.assertEqual('185.247.200.252', result[0]['ipv4_address'])
            self.assertEqual('d646:af6:16d9:5a46:72c0:9a90:d78f:24e7',
                             result[0]['ipv6_address'])
            self.assertEqual('XXXXXXXXXXXXXXX5516', result[0]['creditcardnumber'])
            self.assertEqual('XXXXXX.XXXX@XXXX.XX', result[0]['email'])
            self.assertEqual('185.181.192.251', result[1]['ipv4_address'])
            self.assertEqual('e2c8:4a45:6dd9:2fd5:6c42:b81f:12ec:394e',
                             result[1]['ipv6_address'])
            self.assertEqual('XXXXXXXXXXXXXXX5825', result[1]['creditcardnumber'])
            self.assertEqual('XXX.XXXXXXXXX.XXXXX@XXXXXXXXXXXXX.XXX', result[1]['email'])

            # Now try on a table where this column doesn't exist
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                result = conn.scan_as_json('abac_db.all_types')
            self.assertTrue('Access to this dataset is' in str(ex_ctx.exception))

    def test_transform_noaccess_filter(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            self.__init_test_role(conn)

            # Grant to the ip_address column (in clear) with a filter on the email
            # column which the user does not have access to.
            conn.execute_ddl('GRANT SELECT ON DATABASE abac_db HAVING ATTRIBUTE IN ' +
                             '(pii.ip_address) ' +
                             'WHERE email like "ac%" ' +
                             'TO ROLE abac_test_role')

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('abac_db.user_account_data')
            self.assertEqual(2, len(result))
            self.assertEqual('244.23.83.241', result[0]['ipv4_address'])
            self.assertEqual('a678:6bb0:7cb2:1f75:bc1d:e41f:b469:ce0c',
                             result[0]['ipv6_address'])
            self.assertEqual('216.154.135.203', result[1]['ipv4_address'])
            self.assertEqual('ad13:4b2f:7557:b429:383d:1660:2368:d81b',
                             result[1]['ipv6_address'])

            # Now try the view
            result = conn.scan_as_json('abac_db.user_account_data_view')
            self.assertEqual(2, len(result))
            self.assertEqual('244.23.83.241', result[0]['ipv4_address'])
            self.assertEqual('a678:6bb0:7cb2:1f75:bc1d:e41f:b469:ce0c',
                             result[0]['ipv6_address'])
            self.assertEqual('216.154.135.203', result[1]['ipv4_address'])
            self.assertEqual('ad13:4b2f:7557:b429:383d:1660:2368:d81b',
                             result[1]['ipv6_address'])

    # This test creates a transform grant that tokenizes a tagged column. We'll assign
    # this tag to an increasing number of columns and verify the results
    def test_transform_all_types(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            # The hash varies from table to table right now. Rethink how we
            # implement this (no ref integrity for small types by default).
            for tbl in ['rs.alltypes', 'rs.alltypes_s3_view']:
                print("Running test against %s" % tbl)
                db = tbl.split('.')[0]
                t = tbl.split('.')[1]
                for scope in ['CATALOG', 'DATABASE rs', 'TABLE ' + tbl]:
                    ctx.disable_auth()
                    self.__init_test_role(conn)

                    conn.execute_ddl(('GRANT SELECT ON %s HAVING ATTRIBUTE ' +
                                      'abac_test.v1 TRANSFORM abac_test.v1 WITH ' +
                                      'tokenize() TO ROLE abac_test_role') % scope)

                    # Clean up attributes from previous run
                    for col in ['bool_col', 'tinyint_col', 'smallint_col', 'int_col',
                                'bigint_col', 'float_col', 'double_col', 'string_col',
                                'varchar_col', 'char_col', 'timestamp_col',
                                'decimal_col']:
                        conn.unassign_attribute('abac_test', 'v1', db, t, col)

                    # Assign tag to bool col
                    conn.assign_attribute('abac_test', 'v1', db, t, 'bool_col')
                    # Scan as testuser
                    ctx.enable_token_auth(token_str=TEST_USER)
                    result = conn.scan_as_json(tbl)
                    self.assertEqual(len(result), 2)
                    self.assertEqual(len(result[0]), 1)

                    # Assign attribute to more columns
                    ctx.disable_auth()
                    for col in ['tinyint_col', 'smallint_col', 'int_col', 'bigint_col']:
                        conn.assign_attribute('abac_test', 'v1', db, t, col)

                    # Scan as testuser
                    ctx.enable_token_auth(token_str=TEST_USER)
                    result = conn.scan_as_json(tbl)
                    self.assertEqual(len(result), 2)
                    self.assertEqual(len(result[0]), 5)
                    if tbl == 'rs.alltypes_s3_view':
                        self.assertTrue(result[0]['bool_col'])
                        self.assertEqual(result[1]['tinyint_col'], 105)
                        self.assertEqual(result[0]['smallint_col'], 13107)
                        self.assertEqual(result[0]['int_col'], 733288971)
                        self.assertEqual(result[0]['bigint_col'], 7333064010443628721)
                    else:
                        self.assertTrue(result[0]['bool_col'])
                        self.assertEqual(result[1]['tinyint_col'], 28)
                        self.assertEqual(result[0]['smallint_col'], 26731)
                        self.assertEqual(result[1]['int_col'], 953486778)
                        self.assertEqual(result[0]['bigint_col'], 7333064010443628721)

                    # Assign attribute to remaining columns
                    ctx.disable_auth()
                    for col in ['float_col', 'double_col', 'string_col',
                                'varchar_col', 'char_col', 'timestamp_col',
                                'decimal_col']:
                        conn.assign_attribute('abac_test', 'v1', db, t, col)

                    # Scan as testuser
                    ctx.enable_token_auth(token_str=TEST_USER)
                    result = conn.scan_as_json(tbl)
                    self.assertEqual(len(result), 2)
                    self.assertEqual(len(result[0]), 12)
                    if tbl == 'rs.alltypes_s3_view':
                        self.assertTrue(result[0]['bool_col'])
                        self.assertEqual(result[1]['tinyint_col'], 105)
                        self.assertEqual(result[0]['smallint_col'], 13107)
                        self.assertEqual(result[0]['int_col'], 733288971)
                        self.assertEqual(result[0]['bigint_col'], 7333064010443628721)
                        self.assertAlmostEqual(result[1]['float_col'], 0.1422174870967865)
                        self.assertAlmostEqual(
                            result[0]['double_col'], 0.38167445002882344)
                        self.assertEqual(
                            result[0]['timestamp_col'], '2164-05-29 01:37:54.000')
                        self.assertEqual(str(result[1]['decimal_col']), '0.4169613811')
                        self.assertEqual(result[1]['string_col'], 'gtyjx')
                        self.assertEqual(result[0]['varchar_col'], 'aixuu2')
                        self.assertEqual(result[1]['char_col'], 'kfle4')
                    else:
                        self.assertTrue(result[0]['bool_col'])
                        self.assertEqual(result[1]['tinyint_col'], 28)
                        self.assertEqual(result[0]['smallint_col'], 26731)
                        self.assertEqual(result[1]['int_col'], 953486778)
                        self.assertEqual(result[0]['bigint_col'], 7333064010443628721)
                        self.assertAlmostEqual(result[1]['float_col'], 0.8782930374145508)
                        self.assertAlmostEqual(
                            result[0]['double_col'], 0.337034002190266)
                        self.assertEqual(
                            result[0]['timestamp_col'], '2543-10-23 08:33:47.000')
                        self.assertEqual(str(result[1]['decimal_col']), '0.0286983588')
                        self.assertEqual(result[1]['string_col'], 'gtyjx')
                        self.assertEqual(result[0]['varchar_col'], 'aixuu2')
                        self.assertEqual(result[1]['char_col'], 'kfle4')

                    # Unassign these, should lose access
                    ctx.disable_auth()
                    for col in ['float_col', 'double_col', 'string_col',
                                'varchar_col', 'char_col', 'timestamp_col',
                                'decimal_col']:
                        conn.unassign_attribute('abac_test', 'v1', db, t, col)

                    ctx.enable_token_auth(token_str=TEST_USER)
                    result = conn.scan_as_json(tbl)
                    self.assertEqual(len(result), 2)
                    self.assertEqual(len(result[0]), 5)
                    if tbl == 'rs.alltypes_s3_view':
                        self.assertTrue(result[0]['bool_col'])
                        self.assertEqual(result[1]['tinyint_col'], 105)
                        self.assertEqual(result[0]['smallint_col'], 13107)
                        self.assertEqual(result[0]['int_col'], 733288971)
                        self.assertEqual(result[0]['bigint_col'], 7333064010443628721)
                    else:
                        self.assertTrue(result[0]['bool_col'])
                        self.assertEqual(result[1]['tinyint_col'], 28)
                        self.assertEqual(result[0]['smallint_col'], 26731)
                        self.assertEqual(result[1]['int_col'], 953486778)
                        self.assertEqual(result[0]['bigint_col'], 7333064010443628721)

    # Test assigning the tag at the table level
    def test_transform_table_all_types(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            for scope in ['CATALOG', 'DATABASE rs', 'TABLE rs.alltypes']:
                ctx.disable_auth()
                self.__init_test_role(conn)

                conn.execute_ddl(('GRANT SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v1 TRANSFORM abac_test.v1 WITH ' +
                                  'tokenize() TO ROLE abac_test_role') % scope)
                # Assign attribute at table level, should grant all columns
                conn.unassign_attribute('abac_test', 'v1', 'rs', 'alltypes')
                conn.assign_attribute('abac_test', 'v1', 'rs', 'alltypes')

                # Scan as testuser
                ctx.enable_token_auth(token_str=TEST_USER)
                result = conn.scan_as_json('rs.alltypes')
                self.assertEqual(len(result), 2)
                self.assertEqual(len(result[0]), 12)
                self.assertTrue(result[0]['bool_col'])
                self.assertEqual(result[1]['tinyint_col'], 28)
                self.assertEqual(result[0]['smallint_col'], 26731)
                self.assertEqual(result[1]['int_col'], 953486778)
                self.assertEqual(result[0]['bigint_col'], 7333064010443628721)
                self.assertAlmostEqual(result[1]['float_col'], 0.8782930374145508)
                self.assertAlmostEqual(
                    result[0]['double_col'], 0.337034002190266)
                self.assertEqual(
                    result[0]['timestamp_col'], '2543-10-23 08:33:47.000')
                self.assertEqual(str(result[1]['decimal_col']), '0.0286983588')
                self.assertEqual(result[1]['string_col'], 'gtyjx')
                self.assertEqual(result[0]['varchar_col'], 'aixuu2')
                self.assertEqual(result[1]['char_col'], 'kfle4')

    # Test multiple grants to different attributes and transforms
    def test_transform_multiple_grants(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            conn.create_attribute('abac_test', 'v2')
            conn.create_attribute('abac_test', 'v3')
            conn.create_attribute('abac_test', 'v4')
            conn.create_attribute('abac_test', 'v5')
            for scope in ['CATALOG', 'DATABASE rs', 'TABLE rs.alltypes']:
                ctx.disable_auth()
                self.__init_test_role(conn)

                # Clean up attributes from previous run
                for t in ['v1', 'v2', 'v3', 'v4', 'v5']:
                    conn.unassign_attribute('abac_test', t, 'rs', 'alltypes')
                for col in ['bool_col', 'tinyint_col', 'smallint_col', 'int_col',
                            'bigint_col', 'float_col', 'double_col', 'string_col',
                            'varchar_col', 'char_col', 'timestamp_col', 'decimal_col']:
                    conn.unassign_attribute('abac_test', 'v1', 'rs', 'alltypes', col)
                    conn.unassign_attribute('abac_test', 'v2', 'rs', 'alltypes', col)
                    conn.unassign_attribute('abac_test', 'v3', 'rs', 'alltypes', col)
                    conn.unassign_attribute('abac_test', 'v4', 'rs', 'alltypes', col)
                    conn.unassign_attribute('abac_test', 'v5', 'rs', 'alltypes', col)

                # Assign different tags to different cols
                conn.assign_attribute('abac_test', 'v1', 'rs', 'alltypes', 'bool_col')
                conn.assign_attribute('abac_test', 'v2', 'rs', 'alltypes', 'int_col')
                conn.assign_attribute('abac_test', 'v3', 'rs', 'alltypes', 'float_col')
                conn.assign_attribute('abac_test', 'v4', 'rs', 'alltypes', 'decimal_col')
                conn.assign_attribute('abac_test', 'v5', 'rs', 'alltypes', 'bigint_col')

                # Grant abac_test.v1 tag
                conn.execute_ddl(('GRANT SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v1 TRANSFORM abac_test.v1 WITH ' +
                                  'tokenize() TO ROLE abac_test_role') % scope)
                # Scan as testuser
                ctx.enable_token_auth(token_str=TEST_USER)
                result = conn.scan_as_json('rs.alltypes')
                self.assertEqual(len(result), 2)
                self.assertEqual(len(result[0]), 1)
                self.assertTrue(result[0]['bool_col'])

                # Grant abac_test.v2, v3 tag
                ctx.disable_auth()
                conn.execute_ddl(('GRANT SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v2 TRANSFORM abac_test.v2 WITH ' +
                                  'tokenize() TO ROLE abac_test_role') % scope)
                conn.execute_ddl(('GRANT SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v3 TRANSFORM abac_test.v3 WITH ' +
                                  'tokenize() TO ROLE abac_test_role') % scope)
                # Scan as testuser
                ctx.enable_token_auth(token_str=TEST_USER)
                result = conn.scan_as_json('rs.alltypes')
                self.assertEqual(len(result), 2)
                self.assertEqual(len(result[0]), 3)
                self.assertTrue(result[0]['bool_col'])
                self.assertEqual(result[1]['int_col'], 953486778)
                self.assertAlmostEqual(result[1]['float_col'], 0.8782930374145508)

                # Grant abac_test.v4, v5 tag
                ctx.disable_auth()
                conn.execute_ddl(('GRANT SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v4 TRANSFORM abac_test.v4 WITH ' +
                                  'tokenize() TO ROLE abac_test_role') % scope)
                conn.execute_ddl(('GRANT SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v5 TRANSFORM abac_test.v5 WITH '
                                  'tokenize() TO ROLE abac_test_role') % scope)
                # Scan as testuser
                ctx.enable_token_auth(token_str=TEST_USER)
                result = conn.scan_as_json('rs.alltypes')
                self.assertEqual(len(result), 2)
                self.assertEqual(len(result[0]), 5)
                self.assertTrue(result[0]['bool_col'])
                self.assertEqual(result[1]['int_col'], 953486778)
                self.assertAlmostEqual(result[1]['float_col'], 0.8782930374145508)
                self.assertEqual(result[0]['bigint_col'], 7333064010443628721)
                self.assertEqual(str(result[1]['decimal_col']), '0.0286983588')

                # Revoke abac_test.v1, v3, v5 tag
                ctx.disable_auth()
                conn.execute_ddl(('REVOKE SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v1 TRANSFORM abac_test.v1 WITH ' +
                                  'tokenize() FROM ROLE abac_test_role') % scope)
                conn.execute_ddl(('REVOKE SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v3 TRANSFORM abac_test.v3 WITH ' +
                                  'tokenize() FROM ROLE abac_test_role') % scope)
                conn.execute_ddl(('REVOKE SELECT ON %s HAVING ATTRIBUTE ' +
                                  'abac_test.v5 TRANSFORM abac_test.v5 WITH ' +
                                  'tokenize() FROM ROLE abac_test_role') % scope)
                # Scan as testuser
                ctx.enable_token_auth(token_str=TEST_USER)
                result = conn.scan_as_json('rs.alltypes')
                self.assertEqual(len(result), 2)
                self.assertEqual(len(result[0]), 2)
                self.assertEqual(result[1]['int_col'], 953486778)
                self.assertEqual(str(result[1]['decimal_col']), '0.0286983588')

    @pytest.mark.skipif(not ENABLE_COMPLEX_TYPE_TAGS,
                        reason='Only valid with complex tags enabled.')
    def test_transform_core_complex_types(self):
        print(not ENABLE_COMPLEX_TYPE_TAGS)
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.create_attribute('abac_test', 'v1')
            self.__init_test_role(conn)

            conn.execute_ddl('GRANT SELECT ON DATABASE rs_complex ' +
                             'TRANSFORM abac_test.v1 WITH tokenize() ' +
                             'TO ROLE abac_test_role')
            conn.assign_attribute('abac_test', 'v1', 'rs_complex', 'struct_t', 'id')
            conn.assign_attribute('abac_test', 'v1', 'rs_complex', 'struct_t', 's1.f2')
            conn.assign_attribute('abac_test', 'v1',
                                  'rs_complex', 'array_struct_array', 'a1.f1')

            # As root
            result = conn.scan_as_json('rs_complex.struct_t')[0]
            self.assertEqual(
                {'id': 123, 's1': {'f1': 'field1', 'f2': 1}},
                result)
            result = conn.scan_as_json('rs_complex.array_struct_array')[0]
            self.assertEqual(
                {'a1': [{'a2': ['jk'], 'f1': 'ab', 'f2': 'c'}]},
                result)

            # As test user this should tokenize f2
            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.scan_as_json('rs_complex.struct_t')[0]
            self.assertEqual(
                {'id': 8759031353374307690, 's1': {'f1': 'field1',
                                                   'f2': 8834530745862350009}},
                result)

            # In this case, the tag is on a nested type which we don't currently
            # support. We fail this query (vs returning it unsafely).
            # TODO: this should tokenize.
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.scan_as_json('rs_complex.array_struct_array')
            self.assertTrue('does not have full access to path' in str(ex_ctx.exception),
                            msg=str(ex_ctx.exception))

    def test_multiple_grants_same_object(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__init_test_role(conn)

            # Grant on 5 different tags individually
            for v in ['v1', 'v2', 'v3', 'v4', 'v5']:
                conn.create_attribute('abac_test', v)
                conn.execute_ddl(('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                                 'abac_test.%s TO ROLE abac_test_role') % v)
            self.assertEqual(5, len(self.__show_grant_abac_role(conn)))

            # Revoke one
            conn.execute_ddl(('REVOKE SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                              'abac_test.%s FROM ROLE abac_test_role') % 'v1')
            self.assertEqual(4, len(self.__show_grant_abac_role(conn)))

            # Revoke two and three
            conn.execute_ddl(('REVOKE SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                              'abac_test.%s FROM ROLE abac_test_role') % 'v2')
            conn.execute_ddl(('REVOKE SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                              'abac_test.%s FROM ROLE abac_test_role') % 'v3')
            self.assertEqual(2, len(self.__show_grant_abac_role(conn)))

            # Revoke the last two
            conn.execute_ddl(('REVOKE SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                              'abac_test.%s FROM ROLE abac_test_role') % 'v4')
            conn.execute_ddl(('REVOKE SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                              'abac_test.%s FROM ROLE abac_test_role') % 'v5')
            self.assertEqual(0, len(self.__show_grant_abac_role(conn)))

    def test_create_with_if_not_exists(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'create_if_not_exists_test'
            create_table_stmt1 = """CREATE TABLE %s.%s (
                c1 int ATTRIBUTE abac_test.v1,
                c2 int ATTRIBUTE abac_test.v2
            )""" % (TEST_DB, table_name)
            create_table_stmt2 = """CREATE TABLE IF NOT EXISTS %s.%s (
                c1 int ATTRIBUTE abac_test.v1,
                c2 int ATTRIBUTE abac_test.v2 abac_test.v3
            )""" % (TEST_DB, table_name)

            conn.execute_ddl(create_table_stmt1)
            assert AbacTest.__col_has_attribute(
                conn, TEST_DB, table_name, 'c1', 'abac_test', 'v1')
            assert AbacTest.__col_has_attribute(
                conn, TEST_DB, table_name, 'c2', 'abac_test', 'v2')
            assert not AbacTest.__col_has_attribute(
                conn, TEST_DB, table_name, 'c2', 'abac_test', 'v3')

            # This should not error and should not replace anything
            conn.execute_ddl(create_table_stmt2)

    def test_lineage_with_drops(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'lineage_with_drops'
            view_name = 'lineage_with_drops_child'
            create_table_stmt = """CREATE TABLE %s.%s (
                c1 int,
                c2 int
            )""" % (TEST_DB, table_name)
            create_view_stmt = "CREATE VIEW %s.%s AS SELECT * FROM %s.%s" % (
                TEST_DB, view_name, TEST_DB, table_name)
            drop_view_stmt = "DROP VIEW %s.%s" % (TEST_DB, view_name)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(create_view_stmt)
            tables = conn.list_datasets(db=TEST_DB, name=table_name)
            assert len(tables) == 1
            assert tables[0].metadata['okera.view.children'] == '%s.%s' % (
                TEST_DB, view_name)

            # After we drop and recreate it should stay the same
            conn.execute_ddl(drop_view_stmt)
            conn.execute_ddl(create_view_stmt)
            tables = conn.list_datasets(db=TEST_DB, name=table_name)
            assert len(tables) == 1
            assert tables[0].metadata['okera.view.children'] == '%s.%s' % (
                TEST_DB, view_name)

    def test_inheritance_aggregation(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'inheritance_on_aggregation'
            view_name = 'inheritance_on_aggregation_view'
            create_table_stmt = """CREATE TABLE %s.%s (
                c1 int,
                c2 int
            )""" % (TEST_DB, table_name)
            create_view_stmt = """CREATE VIEW %s.%s AS SELECT c1, count(*)
                FROM %s.%s
                GROUP BY c1""" % (TEST_DB, view_name, TEST_DB, table_name)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(create_view_stmt)

            conn.assign_attribute('abac_test', 'v1', TEST_DB, table_name, 'c1')
            assert AbacTest.__col_has_attribute(
                conn, TEST_DB, table_name, 'c1', 'abac_test', 'v1')
            assert not AbacTest.__col_has_attribute(
                conn, TEST_DB, view_name, 'c1', 'abac_test', 'v1')

    def test_inherit_multiple_attribute_assignments(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            for c in list_configs(conn, TConfigType.AUTOTAGGER_REGEX):
                if c['namespace'] == 'abac_test' and c['tag'] == 'v1':
                    delete_config(conn, TConfigType.AUTOTAGGER_REGEX, str(c['id']))

            # Setup the rule to match a specific column name
            params = {}
            params['name'] = 'awesome_rule'
            params['namespace'] = 'abac_test'
            params['tag'] = 'v1'
            params['description'] = 'a great regex'
            params['min_rows'] = '100000000'
            params['max_rows'] = '100000000'
            params['match_rate'] = '1.0'
            params['match_column_name'] = 'true'
            params['match_column_comment'] = 'true'
            params['tag'] = 'v1'
            params['expression'] = 'c1_awesome'
            upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, None, params)

            self.__cleanup(conn)
            table_name = 'inheritance_on_aggregation'
            view_name = 'inheritance_on_aggregation_view'
            create_table_stmt = """CREATE TABLE %s.%s (
                c1_awesome int,
                c2 int
            )""" % (TEST_DB, table_name)
            create_view_stmt = """CREATE VIEW %s.%s AS SELECT * FROM %s.%s""" % (
                TEST_DB, view_name, TEST_DB, table_name)
            autotag_stmt = 'ALTER TABLE %s.%s EXECUTE AUTOTAG' % (TEST_DB, table_name)

            conn.execute_ddl(create_table_stmt)
            assert not AbacTest.__col_has_attribute(
                conn, TEST_DB, table_name, 'c1_awesome', 'abac_test', 'v1')

            # After the autotag execution, the column should now have the tag on it
            conn.execute_ddl(autotag_stmt)
            assert AbacTest.__col_has_attribute(
                conn, TEST_DB, table_name, 'c1_awesome', 'abac_test', 'v1')

            # We also add a manual assignment
            conn.assign_attribute('abac_test', 'v1', TEST_DB, table_name, 'c1_awesome')
            assert AbacTest.__col_has_attribute(
                conn, TEST_DB, table_name, 'c1_awesome', 'abac_test', 'v1')

            # c1_awesome is now tagged twice with abac_test.v1, one from a manual
            # assignment and from the autotagging rule. When we create the view, we
            # should only cascade this once.
            conn.execute_ddl(create_view_stmt)
            assert AbacTest.__col_has_attribute(
                conn, TEST_DB, view_name, 'c1_awesome', 'abac_test', 'v1')

    def test_inheritance_lineage_join(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'inheritance_lineage'
            view_name = 'inheritance_lineage_view'
            view_name2 = 'inheritance_lineage_view2'
            create_table_stmt = """CREATE TABLE %s.%s (
                c1 int,
                c2 int
            )""" % (TEST_DB, table_name)
            create_view_stmt = """CREATE VIEW %s.%s AS
                SELECT a.c1 FROM %s.%s a JOIN %s.%s b ON a.c1=b.c1
                """ % (TEST_DB, view_name, TEST_DB, table_name, TEST_DB, table_name)
            create_view_stmt2 = """CREATE VIEW %s.%s AS
                SELECT * FROM %s.%s
                """ % (TEST_DB, view_name2, TEST_DB, view_name)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(create_view_stmt)

            table = conn.list_datasets(db=TEST_DB, name=table_name)[0]
            view = conn.list_datasets(db=TEST_DB, name=view_name)[0]

            assert TBLPROP_CHILDREN in table.metadata
            assert table.metadata[TBLPROP_CHILDREN] == ('%s.%s' % (TEST_DB, view_name))

            assert TBLPROP_BASE in view.metadata
            assert TBLPROP_PARENTS in view.metadata
            assert view.metadata[TBLPROP_BASE] == ('%s.%s' % (TEST_DB, table_name))
            assert view.metadata[TBLPROP_PARENTS] == ('%s.%s' % (TEST_DB, table_name))

            conn.execute_ddl(create_view_stmt2)
            view = conn.list_datasets(db=TEST_DB, name=view_name)[0]
            view2 = conn.list_datasets(db=TEST_DB, name=view_name2)[0]

            assert TBLPROP_CHILDREN in view.metadata
            assert view.metadata[TBLPROP_CHILDREN] == ('%s.%s' % (TEST_DB, view_name2))

            assert TBLPROP_BASE in view2.metadata
            assert TBLPROP_PARENTS in view2.metadata
            assert view2.metadata[TBLPROP_BASE] == ('%s.%s' % (TEST_DB, table_name))
            assert view2.metadata[TBLPROP_PARENTS] == ('%s.%s' % (TEST_DB, view_name))

    @pytest.mark.skip(reason="Currently broken - lineage not correct for UNION ALL")
    def test_inheritance_lineage_union(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'inheritance_lineage'
            view_name = 'inheritance_lineage_view'
            view_name2 = 'inheritance_lineage_view2'
            create_table_stmt = """CREATE TABLE %s.%s (
                c1 int,
                c2 int
            )""" % (TEST_DB, table_name)
            create_view_stmt = """CREATE VIEW %s.%s AS
                SELECT * FROM %s.%s a UNION ALL SELECT * FROM %s.%s
                """ % (TEST_DB, view_name, TEST_DB, table_name, TEST_DB, table_name)
            create_view_stmt2 = """CREATE VIEW %s.%s AS
                SELECT * FROM %s.%s
                """ % (TEST_DB, view_name2, TEST_DB, view_name)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(create_view_stmt)

            table = conn.list_datasets(db=TEST_DB, name=table_name)[0]
            view = conn.list_datasets(db=TEST_DB, name=view_name)[0]

            assert TBLPROP_CHILDREN in table.metadata
            assert table.metadata[TBLPROP_CHILDREN] == ('%s.%s' % (TEST_DB, view_name))

            assert TBLPROP_BASE in view.metadata
            assert TBLPROP_PARENTS in view.metadata
            assert view.metadata[TBLPROP_BASE] == ('%s.%s' % (TEST_DB, table_name))
            assert view.metadata[TBLPROP_PARENTS] == ('%s.%s' % (TEST_DB, table_name))

            conn.execute_ddl(create_view_stmt2)
            view = conn.list_datasets(db=TEST_DB, name=view_name)[0]
            view2 = conn.list_datasets(db=TEST_DB, name=view_name2)[0]

            assert TBLPROP_CHILDREN in view.metadata
            assert view.metadata[TBLPROP_CHILDREN] == ('%s.%s' % (TEST_DB, view_name2))

            assert TBLPROP_BASE in view2.metadata
            assert TBLPROP_PARENTS in view2.metadata
            assert view2.metadata[TBLPROP_BASE] == ('%s.%s' % (TEST_DB, table_name))
            assert view2.metadata[TBLPROP_PARENTS] == ('%s.%s' % (TEST_DB, view_name))

    def test_inheritance_lineage_unnest(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'inheritance_lineage'
            view_name = 'inheritance_lineage_view'
            create_table_stmt = """CREATE EXTERNAL TABLE %s.%s
                LIKE PARQUET 's3://cerebro-customers/chase/zd1238_parquet/product/'
                STORED AS PARQUET
                LOCATION 's3://cerebro-customers/chase/zd1238_parquet/product/'
            """ % (TEST_DB, table_name)
            create_view_stmt = """CREATE VIEW %s.%s AS SELECT ** FROM %s.%s
                """ % (TEST_DB, view_name, TEST_DB, table_name)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(create_view_stmt)

            table = conn.list_datasets(db=TEST_DB, name=table_name)[0]
            view = conn.list_datasets(db=TEST_DB, name=view_name)[0]

            assert TBLPROP_CHILDREN in table.metadata
            assert table.metadata[TBLPROP_CHILDREN] == ('%s.%s' % (TEST_DB, view_name))

            assert TBLPROP_BASE in view.metadata
            assert TBLPROP_PARENTS in view.metadata
            assert view.metadata[TBLPROP_BASE] == ('%s.%s' % (TEST_DB, table_name))
            assert view.metadata[TBLPROP_PARENTS] == ('%s.%s' % (TEST_DB, table_name))

    @pytest.mark.skipif(not ENABLE_COMPLEX_TYPE_TAGS,
                        reason='Only valid with complex tags enabled.')
    def test_tag_inheritance_complex_type(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'inheritance_lineage'
            view_name = 'inheritance_lineage_view'
            create_table_stmt = """CREATE TABLE %s.%s (
                s1 struct<f1: string, s2: struct<f21: string, f22: string>>)
            """ % (TEST_DB, table_name)
            create_view_stmt = """CREATE VIEW %s.%s AS SELECT * FROM %s.%s
                """ % (TEST_DB, view_name, TEST_DB, table_name)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(create_view_stmt)
            conn.execute_ddl('ALTER TABLE %s.%s ADD COLUMN ATTRIBUTE s1.f1 abac_test.v1' % (TEST_DB, table_name))
            conn.execute_ddl('ALTER TABLE %s.%s ADD COLUMN ATTRIBUTE s1.f1 abac_test.v2' % (TEST_DB, table_name))
            conn.execute_ddl('ALTER TABLE %s.%s ADD COLUMN ATTRIBUTE s1.s2.f21 abac_test.v1' % (TEST_DB, table_name))
            conn.execute_ddl('ALTER TABLE %s.%s ADD COLUMN ATTRIBUTE s1.s2.f21 abac_test.v2' % (TEST_DB, table_name))

            table = conn.list_datasets(db=TEST_DB, name=table_name)[0]
            view = conn.list_datasets(db=TEST_DB, name=view_name)[0]

            assert self.__verify_column_has_tag(table, 's1.f1', 'abac_test.v1')
            assert self.__verify_column_has_tag(table, 's1.f1', 'abac_test.v2')
            assert self.__verify_column_has_tag(table, 's1.s2.f21', 'abac_test.v1')
            assert self.__verify_column_has_tag(table, 's1.s2.f21', 'abac_test.v2')

            assert self.__verify_column_has_tag(view, 's1.f1', 'abac_test.v1')
            assert self.__verify_column_has_tag(view, 's1.f1', 'abac_test.v2')
            assert self.__verify_column_has_tag(view, 's1.s2.f21', 'abac_test.v1')
            assert self.__verify_column_has_tag(view, 's1.s2.f21', 'abac_test.v2')

            # Make sure the other complex fields do not have these attributes
            assert not self.__verify_column_has_tag(table, 's1.s2', 'abac_test.v1')
            assert not self.__verify_column_has_tag(table, 's1.s2', 'abac_test.v2')
            assert not self.__verify_column_has_tag(table, 's1.s2.f22', 'abac_test.v1')
            assert not self.__verify_column_has_tag(table, 's1.s2.f22', 'abac_test.v2')
            assert not self.__verify_column_has_tag(view, 's1.s2', 'abac_test.v1')
            assert not self.__verify_column_has_tag(view, 's1.s2', 'abac_test.v2')
            assert not self.__verify_column_has_tag(view, 's1.s2.f22', 'abac_test.v1')
            assert not self.__verify_column_has_tag(view, 's1.s2.f22', 'abac_test.v2')

            # TODO: the DDL does not support dropping attributes on complex types, so do it
            # via RPC
            # conn.execute_ddl('ALTER TABLE %s.%s DROP COLUMN ATTRIBUTE s1.f1 abac_test.v1' % (TEST_DB, table_name))
            # conn.execute_ddl('ALTER TABLE %s.%s DROP COLUMN ATTRIBUTE s1.f1 abac_test.v2' % (TEST_DB, table_name))
            # conn.execute_ddl('ALTER TABLE %s.%s DROP COLUMN ATTRIBUTE s1.s2.f21 abac_test.v1' % (TEST_DB, table_name))
            # conn.execute_ddl('ALTER TABLE %s.%s DROP COLUMN ATTRIBUTE s1.s2.f21 abac_test.v2' % (TEST_DB, table_name))
            conn.unassign_attribute('abac_test', 'v1', TEST_DB, table_name, 's1.f1')
            conn.unassign_attribute('abac_test', 'v2', TEST_DB, table_name, 's1.f1')
            conn.unassign_attribute('abac_test', 'v1', TEST_DB, table_name, 's1.s2.f21')
            conn.unassign_attribute('abac_test', 'v2', TEST_DB, table_name, 's1.s2.f21')

            table = conn.list_datasets(db=TEST_DB, name=table_name)[0]
            view = conn.list_datasets(db=TEST_DB, name=view_name)[0]

            assert not self.__verify_column_has_tag(table, 's1.f1', 'abac_test.v1')
            assert not self.__verify_column_has_tag(table, 's1.f1', 'abac_test.v2')
            assert not self.__verify_column_has_tag(table, 's1.s2.f21', 'abac_test.v1')
            assert not self.__verify_column_has_tag(table, 's1.s2.f21', 'abac_test.v2')

            assert not self.__verify_column_has_tag(view, 's1.f1', 'abac_test.v1')
            assert not self.__verify_column_has_tag(view, 's1.f1', 'abac_test.v2')
            assert not self.__verify_column_has_tag(view, 's1.s2.f21', 'abac_test.v1')
            assert not self.__verify_column_has_tag(view, 's1.s2.f21', 'abac_test.v2')

            # Make sure the other complex fields do not have these attributes
            assert not self.__verify_column_has_tag(table, 's1.s2', 'abac_test.v1')
            assert not self.__verify_column_has_tag(table, 's1.s2', 'abac_test.v2')
            assert not self.__verify_column_has_tag(table, 's1.s2.f22', 'abac_test.v1')
            assert not self.__verify_column_has_tag(table, 's1.s2.f22', 'abac_test.v2')
            assert not self.__verify_column_has_tag(view, 's1.s2', 'abac_test.v1')
            assert not self.__verify_column_has_tag(view, 's1.s2', 'abac_test.v2')
            assert not self.__verify_column_has_tag(view, 's1.s2.f22', 'abac_test.v1')
            assert not self.__verify_column_has_tag(view, 's1.s2.f22', 'abac_test.v2')

    def test_filter_with_tag_selection(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'airlines'
            create_table_stmt = """CREATE EXTERNAL TABLE %s.%s
                LIKE PARQUET 's3://cerebrodata-test/airlines/parquet_sampled/'
                STORED AS PARQUET
                LOCATION 's3://cerebrodata-test/airlines/parquet_sampled/'
            """ % (TEST_DB, table_name)

            # This grant should only apply to table with the appropriate
            # tag, and our table does not have this tag.
            grant_stmt = """GRANT SELECT ON TABLE %s.%s
                HAVING ATTRIBUTE IN (%s.%s)
                WHERE origin='SEA'
                TO ROLE %s
            """ % (TEST_DB, table_name, 'abac_test', 'v1', TEST_ROLE)

            # This grant gives us access to SELECT on the table, as without
            # it the above grant is not sufficient
            grant2_stmt = """GRANT SELECT ON TABLE %s.%s
                TRANSFORM (%s.%s) WITH tokenize()
                TO ROLE %s
            """ % (TEST_DB, table_name, 'abac_test', 'v2', TEST_ROLE)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(grant_stmt)
            conn.execute_ddl(grant2_stmt)

            ctx.enable_token_auth(token_str=TEST_USER)
            res = conn.scan_as_json(
                """SELECT origin, count(*) as cnt
                   FROM %s.%s
                   GROUP BY origin
                """ % (TEST_DB, table_name),
                dialect='okera')

            # Should return a match for every city
            self.assertEqual(len(res), 339)

            # Add the tag to the table, making the WHERE clause become
            # applicable, and ensure it returns only entries for SEA
            attr_ddl = """ALTER TABLE %s.%s ADD ATTRIBUTE %s.%s""" % (
                TEST_DB, table_name, 'abac_test', 'v1'
            )

            ctx.disable_auth()
            conn.execute_ddl(attr_ddl)

            ctx.enable_token_auth(token_str=TEST_USER)
            res = conn.scan_as_json(
                """SELECT origin, count(*) as cnt
                   FROM %s.%s
                   GROUP BY origin
                """ % (TEST_DB, table_name),
                dialect='okera')

            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]['origin'], 'SEA')
            self.assertEqual(res[0]['cnt'], 6516)

    def test_filter_for_admin_user(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            table_name = 'airlines'
            create_table_stmt = """CREATE EXTERNAL TABLE %s.%s
                LIKE PARQUET 's3://cerebrodata-test/airlines/parquet_sampled/'
                STORED AS PARQUET
                LOCATION 's3://cerebrodata-test/airlines/parquet_sampled/'
            """ % (TEST_DB, table_name)

            # Two grants, one that adds a filter and one that gives full access.
            # This should result in no filter (union semantics).
            grant_stmt = """GRANT SELECT ON TABLE %s.%s
                WHERE origin='SEA'
                TO ROLE %s
            """ % (TEST_DB, table_name, TEST_ROLE)
            grant_full_stmt = "GRANT SELECT ON TABLE %s.%s TO ROLE %s" % (
                TEST_DB, table_name, TEST_ROLE)

            conn.execute_ddl(create_table_stmt)
            conn.execute_ddl(grant_stmt)
            conn.execute_ddl(grant_full_stmt)

            ctx.enable_token_auth(token_str=TEST_USER)
            explain = conn.execute_ddl(
                "EXPLAIN SELECT * FROM %s.%s" % (TEST_DB, table_name))
            self.assertTrue('predicates' not in explain, msg=explain)

            # Should return a match for every city, as predicate shouldn't be applied
            res = conn.scan_as_json(
                """SELECT origin, count(*) as cnt
                   FROM %s.%s
                   GROUP BY origin
                """ % (TEST_DB, table_name),
                dialect='okera')
            self.assertEqual(len(res), 339)

    @unittest.skip("Test requires server to start with -enable-data-exposing-mock-udfs")
    def test_data_exposing_udfs(self):
        ctx = common.get_test_context()
        DB = 'test_expose_data_udf_db'
        with common.get_planner(ctx) as conn:
            self.__cleanup(conn)
            self._recreate_test_db(conn, DB)
            self._recreate_test_role(conn, TEST_ROLE, [TEST_USER])
            conn.create_attribute(DB, 'v1')
            conn.create_attribute(DB, 'v2')
            self._create_all_types(conn, DB)
            conn.assign_attribute(DB, 'v1', DB, 'alltypes', "string_col")
            conn.assign_attribute(DB, 'v2', DB, 'alltypes', "varchar_col")

            # Set up a grant that transforms the two tagged columns.
            conn.execute_ddl("""
                GRANT SELECT ON TABLE %s.alltypes
                TRANSFORM %s.%s WITH %s
                TRANSFORM %s.%s WITH %s
                TO ROLE %s""" % (DB, DB, 'v1', 'mask()', DB, 'v2', 'tokenize()', TEST_ROLE))

            ctx.enable_token_auth(token_str=TEST_USER)
            data = conn.scan_as_json(
                'SELECT int_col, string_col, varchar_col FROM %s.%s' % (DB, 'alltypes'))
            self.assertEqual(2, data[0]['int_col'])
            self.assertEqual(8, data[1]['int_col'])
            self.assertEqual('XXXXX', data[0]['string_col'])
            self.assertEqual('XXXXX', data[1]['string_col'])
            self.assertEqual('aixuu2', data[0]['varchar_col'])
            self.assertEqual('djlui8', data[1]['varchar_col'])

            # Now grant select to the whole table. This would normally take precedence
            # but mask() has been configured to be higher precedence.
            ctx.disable_auth()
            conn.execute_ddl("""
                GRANT SELECT ON TABLE %s.alltypes TO ROLE %s""" % (DB, TEST_ROLE))

            ctx.enable_token_auth(token_str=TEST_USER)
            data = conn.scan_as_json(
                'SELECT int_col, string_col, varchar_col FROM %s.%s' % (DB, 'alltypes'))
            self.assertEqual(2, data[0]['int_col'])
            self.assertEqual(8, data[1]['int_col'])
            self.assertEqual('XXXXX', data[0]['string_col'])
            self.assertEqual('XXXXX', data[1]['string_col'])
            self.assertEqual('vchar1', data[0]['varchar_col'])
            self.assertEqual('vchar2', data[1]['varchar_col'])

if __name__ == "__main__":
    unittest.main()
