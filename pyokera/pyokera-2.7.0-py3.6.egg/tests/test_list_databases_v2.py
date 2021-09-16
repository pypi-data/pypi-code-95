# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Some integration tests for auth in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-return
# pylint: disable=duplicate-code

import unittest
import os

#from okera import context, _thrift_api
#from datetime import datetime
from okera.tests import pycerebro_test_common as common
from okera._thrift_api import (TAttribute, TAttributeMatchLevel, TAccessPermissionLevel)
from time import perf_counter

TEST_USER = 'list_dbs_test_user'
TEST_ROLE = 'list_dbs_test_role'

TEST_MODE_GLUE = False
# We should do better check here to assert for True.
if 'TEST_MODE_GLUE' in os.environ:
    TEST_MODE_GLUE = True

class ListDatabasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup().
        """
        super(ListDatabasesTest, cls).setUpClass()

    def test_list_databases_basic(self):
        USER = 'mktg_analyst'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("create role if not exists temp_role")
            conn.execute_ddl("GRANT ROLE temp_role TO GROUP temp_user")
            conn.execute_ddl("create database if not exists temp_database")
            conn.execute_ddl("""
                grant CREATE_AS_OWNER on database temp_database to role temp_role""")
            # list databases test (exact match)
            result = conn.list_databases_v2(exact_names_filter=['demo_test'],
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 1)

            # list databases test (pattern match)
            result = conn.list_databases_v2(name_pattern_filter='*tpc*',
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 10)

            # Verify that when 'names_only' flag is set, no other metadata
            # (like attributes, datasets count, db access levels etc) is populated except
            # db_name
            result = conn.list_databases_v2(name_pattern_filter='*tpc*',
                                            limit=10, page_token=None, names_only=True)

            returned_dbs = []
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue(len(result.databases) == 10)
            for database in result.databases:
                self.assertTrue(database.name in returned_dbs)
                self.assertTrue(database.datasets_count == 0)
                self.assertTrue(len(database.attribute_values) == 0)
                self.assertTrue(database.access_levels is None)
                assert database.has_grant is False

            result = conn.list_databases_v2(name_pattern_filter='okera_sample|rs',
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 2)

            # list databases test (no filter criteria)
            result = conn.list_databases_v2()
            self.assertTrue(len(result.databases) == 10)

            # list databases test (very weird pattern. Should return empty list)
            result = conn.list_databases_v2(name_pattern_filter='*WeirdPattern*',
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 0)

            # list databases test (for access levels)
            ctx.enable_token_auth(token_str=USER)
            result = conn.list_databases_v2(exact_names_filter=['marketing_database'],
                                            limit=10, page_token=None)
            for database in result.databases:
                self.assertTrue(database.name == ['marketing_database'])
                self.assertTrue(database.datasets_count == 3)
                assert TAccessPermissionLevel.SHOW in database.access_levels
                assert TAccessPermissionLevel.CREATE_AS_OWNER in database.access_levels
                assert TAccessPermissionLevel.SELECT not in database.access_levels
            self.assertTrue(len(result.databases) == 1)

            # list databases test (when there are no tables in the db)
            ctx.enable_token_auth(token_str='temp_user')
            result = conn.list_databases_v2(exact_names_filter=['temp_database'],
                                            limit=10, page_token=None)
            for database in result.databases:
                self.assertTrue(database.name == ['temp_database'])
                self.assertTrue(database.datasets_count == 0)
                assert TAccessPermissionLevel.SHOW not in database.access_levels
                assert TAccessPermissionLevel.CREATE_AS_OWNER in database.access_levels
                assert TAccessPermissionLevel.SELECT not in database.access_levels
            self.assertTrue(len(result.databases) == 1)

            # Now verify that when 'names_only' flag is set, no other metadata
            # (like attributes, datasets count, db access levels etc) is populated except
            # db_name
            result = conn.list_databases_v2(exact_names_filter=['temp_database'],
                                            limit=10, page_token=None, names_only=True)
            for database in result.databases:
                self.assertTrue(database.name == ['temp_database'])
                self.assertTrue(database.datasets_count == 0)
                self.assertTrue(database.access_levels is None)
            self.assertTrue(len(result.databases) == 1)

            # Drop temp_database
            ctx.enable_token_auth(token_str='root')
            conn.execute_ddl('DROP DATABASE IF EXISTS temp_database CASCADE')

    @unittest.skipIf(not TEST_MODE_GLUE,
                     "Estimated count only supported for glue.")
    def test_list_db_estimated_count(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # list databases test (no filter criteria)
            result = conn.list_databases_v2(name_pattern_filter='okera*', limit=1)
            print(result)
            self.assertTrue(result is not None)
            self.assertTrue(result.databases[0].is_datasets_count_estimated is False)

            # create databases
            conn.execute_ddl('DROP DATABASE IF EXISTS page_test_db CASCADE')
            conn.execute_ddl('CREATE DATABASE page_test_db')

            # create 101 tables 0-100
            for i in range(101):
                tbl = "t_%s" % i
                conn.execute_ddl('CREATE TABLE page_test_db.%s(c1 int, c11 int)' % tbl)

            result = conn.list_databases_v2(exact_names_filter=['page_test_db'])
            print(result)
            self.assertTrue(result is not None)
            self.assertTrue(result.databases[0].datasets_count == 100)
            self.assertTrue(result.databases[0].is_datasets_count_estimated is True)

            # drop and re-create test role and assign it to a group
            # it would lose its old privileges.
            conn.execute_ddl('DROP ROLE IF EXISTS %s'% TEST_ROLE)
            conn.execute_ddl('CREATE ROLE %s'% TEST_ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE, TEST_USER))
            # GRANT SELECT on just one table for the role TEST_ROLE.
            conn.execute_ddl('GRANT SELECT ON TABLE %s to ROLE %s' %
                             ("page_test_db.t_1", TEST_ROLE))

            # list databases test for user who has only one table access.
            # the flag is_datasets_count_estimated should be False in this case.
            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(exact_names_filter=['page_test_db'])
            print(result)
            self.assertTrue(result is not None)
            self.assertTrue(result.databases[0].datasets_count == 1)
            self.assertTrue(result.databases[0].is_datasets_count_estimated is False)

            ctx.enable_token_auth(token_str='root')
            conn.execute_ddl('DROP ROLE IF EXISTS %s' % TEST_ROLE)
            conn.execute_ddl('DROP DATABASE IF EXISTS page_test_db CASCADE')


    def test_list_databases_tag_filter1(self):
        """ Test to verify that list_databases() api returns correct databases after
            applying attributes (tag) filter with combination of any level of match
            i.e. DATABASE_ONLY, DATABASE_PLUS, TABLE_ONLY, COLUMN_ONLY etc.
            Scenario to test is different tags on the same database  at different levels.
        """
        db1 = 'attributes_test_db1'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # create attributes
            conn.delete_attribute('test_namespace', 'test_key1')
            conn.create_attribute('test_namespace', 'test_key1')
            conn.delete_attribute('test_namespace', 'test_key2')
            conn.create_attribute('test_namespace', 'test_key2')
            conn.delete_attribute('test_namespace', 'test_key3')
            conn.create_attribute('test_namespace', 'test_key3')

            # create databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db1)
            conn.execute_ddl('CREATE DATABASE %s' % db1)

            # create tables
            conn.execute_ddl('CREATE TABLE %s.t1(c1 int, c11 int)' % db1)

            # Assign attributes at DB level, Table level and Column level
            conn.assign_attribute('test_namespace', 'test_key1', db1)
            conn.assign_attribute('test_namespace', 'test_key2', db1, 't1')
            conn.assign_attribute('test_namespace', 'test_key3', db1, 't1', 'c1')

            # Create TAttribute objects required for testing
            attributes = []
            attr1_db_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key1')
            attr1_tab_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key2')
            attr1_col_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key3')

            # should return the database: db1
            # Input tag is on DATABASE level and Match_Level = DATABASE_ONLY
            # Tag filter matches at DB level only
            attributes.append(attr1_db_level)
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_ONLY)
            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db1])

            # should return the database: db1
            # Input tag is on DATABASE level and Match_Level = DATABASE_PLUS
            # Tag filter matches at DB, Table and Column level
            attributes.clear()
            attributes.append(attr1_db_level)
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_PLUS)
            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db1])

            # No Db should be returned.
            # Input tags are on TABLE and COLUMN level and Match_Level = DATABASE_ONLY
            # Tag filter matches at DB level only
            attributes.clear()
            attributes.append(attr1_tab_level)
            attributes.append(attr1_col_level)
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_ONLY)
            self.assertTrue(len(result.databases) == 0)

            # should return the database: db1
            # Input tags are on TABLE and COLUMN level and Match_Level = DATABASE_PLUS
            # Tag filter matches at DB, TABLE and COLUMN level
            attributes.clear()
            attributes.append(attr1_tab_level)
            attributes.append(attr1_col_level)
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_PLUS)
            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db1])

            # drop databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db1)

    def test_list_databases_tag_filter2(self):
        """ Test to verify that list_databases() api returns correct databases after
            applying attributes (tag) filter with combination of any level of match
            i.e. DATABASE_ONLY, DATABASE_PLUS, TABLE_ONLY, COLUMN_ONLY etc.
            Scenario to test is different tags on different databases at different levels.
        """
        db2 = 'attributes_test_db2'
        db3 = 'attributes_test_db3'
        db4 = 'attributes_test_db4'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # create attributes
            conn.delete_attribute('test_namespace', 'test_key4')
            conn.create_attribute('test_namespace', 'test_key4')
            conn.delete_attribute('test_namespace', 'test_key5')
            conn.create_attribute('test_namespace', 'test_key5')
            conn.delete_attribute('test_namespace', 'test_key6')
            conn.create_attribute('test_namespace', 'test_key6')

            # create databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db2)
            conn.execute_ddl('CREATE DATABASE %s' % db2)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db3)
            conn.execute_ddl('CREATE DATABASE %s' % db3)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db4)
            conn.execute_ddl('CREATE DATABASE %s' % db4)

            # create tables
            conn.execute_ddl('CREATE TABLE %s.t2(c2 int, c22 int)' % db2)
            conn.execute_ddl('CREATE TABLE %s.t3(c3 int, c33 int)' % db3)
            conn.execute_ddl('CREATE TABLE %s.t4(c4 int, c44 int)' % db4)

            # Assign attributes at DB level, Table level and Column level
            conn.assign_attribute('test_namespace', 'test_key4', db2)
            conn.assign_attribute('test_namespace', 'test_key5', db3, 't3')
            conn.assign_attribute('test_namespace', 'test_key6', db4, 't4', 'c4')

            attributes = []
            attr2_db_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key4')
            attr3_tab_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key5')
            attr4_col_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key6')
            attributes.append(attr2_db_level)
            attributes.append(attr3_tab_level)
            attributes.append(attr4_col_level)

            # should return the database: db2
            # Input tags are on DB, TABLE, & COLUMN level and Match_Level = DATABASE_ONLY
            # Tag filter matches at DB level only
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_ONLY)
            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db2])

            # should return the database: db3
            # Input tags are on DB, TABLE, & COLUMN level and Match_Level = TABLE_ONLY
            # Tag filter matches at TABLE level only
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_ONLY)
            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db3])

            # should return the database: db4
            # Input tags are on DB, TABLE, & COLUMN level and Match_Level = COLUMN_ONLY
            # Tag filter matches at COLUMN level only
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.COLUMN_ONLY)
            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db4])

            # should return the database: db2, db3 and db4
            # Input tags are on DB, TABLE, & COLUMN level and Match_Level = DATABASE_PLUS
            # Tag filter matches at DB, TABLE, & COLUMN level
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_PLUS)
            self.assertTrue(len(result.databases) == 3)
            returned_dbs = []
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db2] in returned_dbs)
            self.assertTrue([db3] in returned_dbs)
            self.assertTrue([db4] in returned_dbs)

            # should return the database: db3 and db4
            # Input tags are on DB, TABLE, & COLUMN level and Match_Level = TABLE_PLUS
            # Tag filter matches at TABLE & COLUMN level
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_PLUS)
            self.assertTrue(len(result.databases) == 2)
            returned_dbs.clear()
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db3] in returned_dbs)
            self.assertTrue([db4] in returned_dbs)

            # should return the database: db2, db3 and db4
            # Input tags are on DB, TABLE, & COLUMN level and Match_Level = None or NULL
            # if no Match_Level is specified, Tag filter matches at ALL levels
            result = conn.list_databases_v2(tags=attributes)
            self.assertTrue(len(result.databases) == 3)
            returned_dbs.clear()
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db2] in returned_dbs)
            self.assertTrue([db3] in returned_dbs)
            self.assertTrue([db4] in returned_dbs)

            # drop databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db2)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db3)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db4)

    def test_list_databases_tag_filter3(self):
        """ Test to verify that list_databases() api returns correct databases after
            applying attributes (tag) filter with combination of any level of match
            i.e. DATABASE_ONLY, DATABASE_PLUS, TABLE_ONLY, COLUMN_ONLY etc.
            Scenario to test is same tag on different databases at different levels.
        """
        db5 = 'attributes_test_db5'
        db6 = 'attributes_test_db6'
        db7 = 'attributes_test_db7'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # create attribute
            conn.delete_attribute('test_namespace', 'test_key7')
            conn.create_attribute('test_namespace', 'test_key7')

            # create databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db5)
            conn.execute_ddl('CREATE DATABASE %s' % db5)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db6)
            conn.execute_ddl('CREATE DATABASE %s' % db6)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db7)
            conn.execute_ddl('CREATE DATABASE %s' % db7)

            # create tables
            conn.execute_ddl('CREATE TABLE %s.t5(c5 int, c55 int)' % db5)
            conn.execute_ddl('CREATE TABLE %s.t6(c6 int, c66 int)' % db6)
            conn.execute_ddl('CREATE TABLE %s.t7(c7 int, c77 int)' % db7)

            # assign same key (common key) to multiple dbs at different levels
            conn.assign_attribute('test_namespace', 'test_key7', db5)
            conn.assign_attribute('test_namespace', 'test_key7', db6, 't6')
            conn.assign_attribute('test_namespace', 'test_key7', db7, 't7', 'c7')

            attributes = []
            attr7_all_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key7')
            attributes.append(attr7_all_level)

            # should return the database: db5
            # Input tag is on DB, TABLE, & COLUMN level and Match_Level = DATABASE_ONLY
            # Tag filter matches at DATABASE level only
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_ONLY)
            self.assertTrue(len(result.databases) == 1)
            returned_dbs = []
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db5] in returned_dbs)

            # should return the database: db6
            # Input tag is on DB, TABLE, & COLUMN level and Match_Level = TABLE_ONLY
            # Tag filter matches at TABLE level only
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_ONLY)
            self.assertTrue(len(result.databases) == 1)
            returned_dbs.clear()
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db6] in returned_dbs)

            # should return the database: db7
            # Input tag is on DB, TABLE, & COLUMN level and Match_Level = COLUMN_ONLY
            # Tag filter matches at TABLE level only
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.COLUMN_ONLY)
            self.assertTrue(len(result.databases) == 1)
            returned_dbs.clear()
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db7] in returned_dbs)

            # should return the database: db5, db6, db7
            # Input tag is on DB, TABLE, & COLUMN level and Match_Level = DATABASE_PLUS
            # Tag filter matches at DB, TABLE and COLUMN level
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_PLUS)
            self.assertTrue(len(result.databases) == 3)
            returned_dbs.clear()
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db5] in returned_dbs)
            self.assertTrue([db6] in returned_dbs)
            self.assertTrue([db7] in returned_dbs)

            # should return the database: db6, db7
            # Input tag is on DB, TABLE, & COLUMN level and Match_Level = TABLE_PLUS
            # Tag filter matches at TABLE and COLUMN level
            result = conn.list_databases_v2(
                tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_PLUS)
            self.assertTrue(len(result.databases) == 2)
            returned_dbs.clear()
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db6] in returned_dbs)
            self.assertTrue([db7] in returned_dbs)

            # should return the database: db5, db6, db7
            # Input tag is on DB, TABLE, & COLUMN level and Match_Level = None or NULL
            # if no Match_Level is specified, Tag filter matches at ALL levels
            result = conn.list_databases_v2(tags=attributes)
            self.assertTrue(len(result.databases) == 3)
            returned_dbs.clear()
            for database in result.databases:
                returned_dbs.append(database.name)
            self.assertTrue([db5] in returned_dbs)
            self.assertTrue([db6] in returned_dbs)
            self.assertTrue([db7] in returned_dbs)

            ########## Test for 'names_only flag ###########
            # Test to verify that when 'names_only' flag is set, no other metadata
            # (like attributes, datasets count, db access levels etc.) is populated except db_name.
            # Also, the flag should work with all the filters. Here, we are testing it
            # with tags filter.

            # names_only flag is not set, result should populate all the metadata
            result = conn.list_databases_v2( tags=attributes,
                tag_match_level=TAttributeMatchLevel.DATABASE_ONLY)

            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db5])
                self.assertTrue(database.datasets_count == 1)
                self.assertTrue(len(database.attribute_values) == 1)
                self.assertTrue(len(database.access_levels) == 1)
                assert TAccessPermissionLevel.ALL in database.access_levels
                assert database.has_grant is True

            # names_only flag is set, result should NOT populate any metadata except db_name
            result = conn.list_databases_v2( tags=attributes,
                tag_match_level=TAttributeMatchLevel.DATABASE_ONLY, names_only=True)

            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db5])
                self.assertTrue(database.datasets_count == 0)
                self.assertTrue(len(database.attribute_values) == 0)
                self.assertTrue(database.access_levels is None)
                assert database.has_grant is False

            # drop databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db5)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db6)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db7)

    def test_list_databases_access_levels(self):
        """ Test to verify that correct access levels are populated for databases and
            catalog privilege levels are correctly copied to the list of database access
            levels.
        """
        db1 = 'access_lvls_test_db1'
        db2 = 'access_lvls_test_db2'
        db3 = 'access_lvls_test_db3'
        db4 = 'access_lvls_test_db4'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # create test role and assign it to a group
            conn.execute_ddl('DROP ROLE IF EXISTS %s'% TEST_ROLE)
            conn.execute_ddl('CREATE ROLE %s'% TEST_ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE, TEST_USER))
            # Grant privileges on catalog level
            conn.execute_ddl('GRANT CREATE ON CATALOG TO ROLE %s'% TEST_ROLE)
            conn.execute_ddl('GRANT SHOW ON CATALOG TO ROLE %s'% TEST_ROLE)
            conn.execute_ddl('GRANT CREATE_AS_OWNER ON CATALOG TO ROLE %s'% TEST_ROLE)
            # create database
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db1)
            conn.execute_ddl('CREATE DATABASE %s' % db1)
            # create table
            conn.execute_ddl('CREATE TABLE %s.t1(c1 int, c11 int)' % db1)
            # grant privileges on database level
            conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s to ROLE %s WITH GRANT OPTION'\
                        % (db1, TEST_ROLE))
            conn.execute_ddl('GRANT INSERT ON DATABASE %s to ROLE %s'% (db1, TEST_ROLE))

            # Test to verify that catalog access levels are copied to database within it
            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(exact_names_filter=[db1])

            for database in result.databases:
                print('Database Name: {0}'.format(database.name))
                print('Dataset Counts: {0}'.format(database.datasets_count))
                print('Access Levels: {0}'.format(database.access_levels))
                print('Has Grant Option: {0}'.format(database.has_grant))
            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db1])
                self.assertTrue(database.datasets_count == 1)
                self.assertTrue(len(database.access_levels) == 4)
                assert TAccessPermissionLevel.CREATE in database.access_levels
                assert TAccessPermissionLevel.SHOW in database.access_levels
                assert TAccessPermissionLevel.SELECT in database.access_levels
                assert TAccessPermissionLevel.INSERT in database.access_levels
                assert TAccessPermissionLevel.CREATE_AS_OWNER not in \
                    database.access_levels
                assert database.has_grant is True

            # Now verify that when 'names_only' flag is set, no other metadata
            # (like attributes, datasets count, db access levels etc) is populated except
            # db_names
            result = conn.list_databases_v2(exact_names_filter=[db1], names_only=True)

            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db1])
                self.assertTrue(database.datasets_count == 0)
                self.assertTrue(database.access_levels is None)
                assert database.has_grant is False

            # Switch back to admin and create a database with no table and no privileges
            # It should inherit catalog privileges (CREATE, SHOW but not CREATE_AS_OWNER)
            ctx.disable_auth()
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db2)
            conn.execute_ddl('CREATE DATABASE %s' % db2)

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(exact_names_filter=[db2])

            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db2])
                self.assertTrue(database.datasets_count == 0)
                self.assertTrue(len(database.access_levels) == 2)
                assert TAccessPermissionLevel.CREATE in database.access_levels
                assert TAccessPermissionLevel.SHOW in database.access_levels
                assert TAccessPermissionLevel.CREATE_AS_OWNER not in \
                    database.access_levels
                assert not database.has_grant

            # Test for a user having INSERT on catalog and abac-privilege on database
            # Switch back to admin
            ctx.disable_auth()
            # drop and re-create test role and assign it to a group
            # it would lose its old privileges.
            conn.execute_ddl('DROP ROLE IF EXISTS %s'% TEST_ROLE)
            conn.execute_ddl('CREATE ROLE %s'% TEST_ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE, TEST_USER))
            # grant privileges on catalog level
            conn.execute_ddl('GRANT INSERT ON CATALOG TO ROLE %s'% TEST_ROLE)
            # create database
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db3)
            conn.execute_ddl('CREATE DATABASE %s' % db3)
            # create table
            conn.execute_ddl('CREATE TABLE %s.t3(c3 int, c33 int)' % db3)
            # create attribute
            conn.delete_attribute('ns_test_access_lvls', 'test_key')
            conn.create_attribute('ns_test_access_lvls', 'test_key')
            # assign attribute to the database
            conn.assign_attribute('ns_test_access_lvls', 'test_key', db3)
            # Grant abac privilege on database to test_role
            conn.execute_ddl('GRANT SELECT ON DATABASE %s HAVING attribute in (%s) \
                to ROLE %s'% (db3, 'ns_test_access_lvls.test_key', TEST_ROLE))

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(exact_names_filter=[db3])

            self.assertTrue(len(result.databases) == 1)
            for database in result.databases:
                self.assertTrue(database.name == [db3])
                self.assertTrue(database.datasets_count == 1)
                self.assertTrue(len(database.access_levels) == 2)
                assert TAccessPermissionLevel.INSERT in database.access_levels
                assert TAccessPermissionLevel.SELECT in database.access_levels

            ctx.disable_auth()

            # create database
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db4)
            conn.execute_ddl('CREATE DATABASE %s' % db4)

            result = conn.list_databases_v2(exact_names_filter=[db4])
            # Check that admin has grant by default
            assert len(result.databases) == 1
            for database in result.databases:
                assert database.name == [db4]
                assert database.has_grant

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(exact_names_filter=[db4])
            # Check that user hasn't grant by default
            assert len(result.databases) == 1
            for database in result.databases:
                assert database.name == [db4]
                assert not database.has_grant

            ctx.disable_auth()
            conn.execute_ddl(
                    'GRANT SELECT ON CATALOG TO ROLE %s WITH GRANT OPTION'% TEST_ROLE)

            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(exact_names_filter=[db4])
            # Check that has grant is inherited from catalog permission
            assert len(result.databases) == 1
            for database in result.databases:
                assert database.name == [db4]
                assert database.has_grant

            ctx.disable_auth()
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db1)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db2)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db3)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db4)

    @unittest.skip("This is one-time test to gather perf stats for names_only flag." \
        "New test/s would be added later to test performance of the listDatabases() api.")
    def test_list_databases_perf_test_for_names_only_flag(self):
        """ Test to verify that the listDatabases() api is fast enough with names_only flag
            even if there are several thousand databases, each containing multiple tables.
        """
        DB  = 'perf_test_for_names_only_flag'
        TBL = 'table'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # create test role and assign it to a group
            conn.execute_ddl('DROP ROLE IF EXISTS %s'% TEST_ROLE)
            conn.execute_ddl('CREATE ROLE %s'% TEST_ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE, TEST_USER))

            start = perf_counter()
            for i in range(0, 2000):
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % (DB + str(i+1)))
                conn.execute_ddl('CREATE DATABASE %s' % (DB + str(i+1)))
                for j in range(0, 5):
                    conn.execute_ddl('CREATE TABLE %s.%s(c1 int, c2 int)' \
                        % ((DB + str(i+1)), (TBL + str(j+1))))
                conn.execute_ddl('GRANT SELECT ON TABLE %s.%s to ROLE %s' \
                    % ((DB + str(i+1)), (TBL + str(j+1)), TEST_ROLE))
            end = perf_counter()
            print("\nElapsed Time in seconds for Creating DBs and Tables: %s" % (end - start))

            # Test to record elapsed time for listDatabases() api without names_only flag
            start = perf_counter()
            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(limit=10100)
            end = perf_counter()
            print("\nElapsed Time in seconds listDatabases() api w/o names_only flag: %s" % (end - start))
            print(len(result.databases))

            # Test to record elapsed time for listDatabases() api with names_only flag
            start = perf_counter()
            ctx.enable_token_auth(token_str=TEST_USER)
            result = conn.list_databases_v2(limit=10100, names_only=True)
            end = perf_counter()
            print("\nElapsed Time in seconds listDatabases() api with names_only flag: %s" % (end - start))
            print(len(result.databases))

if __name__ == "__main__":
    unittest.main()
