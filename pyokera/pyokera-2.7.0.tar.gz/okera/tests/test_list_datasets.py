# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Some integration tests for auth in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-return
# pylint: disable=duplicate-code

import unittest

#from okera import context, _thrift_api
#from datetime import datetime
from okera.tests import pycerebro_test_common as common
from okera._thrift_api import (TAttribute, TAttributeMatchLevel, TGetDatasetsParams,
    TRecordServiceException)
from okera import odas

TEST_ROLE = "test_connection_filter_role"
TEST_USER = "test_connection_filter_user"
ROOT_USER = "root"
PSQL_CXN = 'test_connection_filter_psql_connection'
MYSQL_CXN = 'test_connection_filter_mysql_connection'
DB1 = 'test_connection_filter_db1'
DB2 = 'test_connection_filter_db2'
TBL1 = 'all_types'
TBL2 = 'scan_key_test'
TBL3 = 'all_numeric_types'
TBL4 = 'filter_pushdown_test'
NAMESPACE = 'test_namespace'
TAG1 = 'test_tag_1'
TAG2 = 'test_tag_2'
CREATE_PSQL_CXN = """
        CREATE DATACONNECTION %s CXNPROPERTIES
        ('connection_type'='JDBC',
        'jdbc_driver'='postgresql',
        'host'='jdbcpsqltest.cyn8yfvyuugz.us-west-2.rds.amazonaws.com',
        'port'='5432',
        'user_key'='awssm://postgres-jdbcpsqltest-username',
        'password_key'='awssm://postgres-jdbcpsqltest-password',
        'jdbc.db.name'='jdbc_test',
        'jdbc.schema.name'='public')
    """ % PSQL_CXN
CREATE_MYSQL_CXN = """
        CREATE DATACONNECTION %s CXNPROPERTIES
        ('connection_type'='JDBC',
        'jdbc_driver'='mysql',
        'host'='cerebro-db-test-long-running.cyn8yfvyuugz.us-west-2.rds.amazonaws.com',
        'port'='3306',
        'user_key'='awsps:///mysql/username',
        'password_key'='awsps:///mysql/password',
        'jdbc.db.name'='jdbc_test')
    """ % MYSQL_CXN

def get_table_names(result):
    return ["%s.%s" % (t.db[0], t.name) for t in result.datasets]

class ListDatasetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(ListDatasetsTest, cls).setUpClass()
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % DB1)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % DB2)
            conn.execute_ddl('DROP DATACONNECTION IF EXISTS %s' % PSQL_CXN)
            conn.execute_ddl('DROP DATACONNECTION IF EXISTS %s' % MYSQL_CXN)
            conn.execute_ddl(CREATE_PSQL_CXN)
            conn.execute_ddl(CREATE_MYSQL_CXN)

            # create DB1 using PSQL_CXN and load TBL1 in it using load_definitions
            conn.execute_ddl("""CREATE DATABASE %s DBPROPERTIES(
                'okera.connection.name' = '%s')""" % (DB1, PSQL_CXN))
            conn.execute_ddl("""ALTER DATABASE %s LOAD DEFINITIONS(%s, %s)""" \
                % (DB1, TBL1, TBL2))

            # create DB2 and manually create TBL2 with PSQL_CXN and TBL3 with MYSQL_CXN
            conn.execute_ddl('CREATE DATABASE %s' % DB2)
            conn.execute_ddl("""
                CREATE EXTERNAL TABLE %s.%s
                STORED as JDBC
                TBLPROPERTIES(
                'driver' = 'postgresql',
                'okera.connection.name' = '%s',
                'jdbc.db.name'='jdbc_test',
                'jdbc.schema.name'='public',
                'table' = '%s'
                )""" % (DB2, TBL3, PSQL_CXN, TBL3))
            conn.execute_ddl("""
                CREATE EXTERNAL TABLE %s.%s
                STORED as JDBC
                TBLPROPERTIES(
                'driver' = 'mysql',
                'okera.connection.name' = '%s',
                'jdbc.db.name'='jdbc_test',
                'jdbc.schema.name'='public',
                'table' = '%s'
                )""" % (DB2, TBL4, MYSQL_CXN, TBL4))

            # create test role and assign it to a group
            conn.execute_ddl('DROP ROLE IF EXISTS %s'% TEST_ROLE)
            conn.execute_ddl('CREATE ROLE %s'% TEST_ROLE)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE, TEST_USER))

            # grant 'ALL' to the test role on DB2
            conn.execute_ddl('GRANT ALL ON DATABASE %s TO ROLE %s' % (DB2, TEST_ROLE))

            # create attributes
            conn.create_attribute(NAMESPACE, TAG1)
            conn.create_attribute(NAMESPACE, TAG2)

            # assign attributes at table level
            conn.assign_attribute(NAMESPACE, TAG1, DB1, TBL1)
            conn.assign_attribute(NAMESPACE, TAG2, DB1, TBL2)
            conn.assign_attribute(NAMESPACE, TAG1, DB2, TBL3)
            conn.assign_attribute(NAMESPACE, TAG2, DB2, TBL4)

    def _get_datasets(self, conn,
                      databases=None, dataset_names=None, filter=None,
                      tags=None, tag_match_level=None, connection_name=None,
                      offset=None, count=None):
        """ RPC to call GetDatasets()
        """
        request = TGetDatasetsParams()
        if conn.ctx._get_user():
            request.requesting_user = conn.ctx._get_user()
        request.databases = databases
        request.dataset_names = dataset_names
        request.filter = filter
        request.attributes = tags
        if tag_match_level:
            request.attr_match_level = TAttributeMatchLevel._NAMES_TO_VALUES[tag_match_level]
        request.connection_name = connection_name
        request.offset = offset
        request.count = count
        return conn._underlying_client().GetDatasets(request).datasets

    def test_tag_filter(self):
        """ Test for multi-tag filter
        """
        db1 = 'attributes_test_db1'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # create attributes
            conn.create_attribute('test_namespace', 'test_key1')
            conn.create_attribute('test_namespace', 'test_key2')
            conn.create_attribute('test_namespace', 'test_key3')

            # create databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db1)
            conn.execute_ddl('CREATE DATABASE %s' % db1)

            # create tables
            conn.execute_ddl('CREATE TABLE %s.t1(c1 int, c11 int)' % db1)
            conn.execute_ddl('CREATE TABLE %s.t2(c2 int, c22 int)' % db1)
            conn.execute_ddl('CREATE TABLE %s.t3(c3 int, c33 int)' % db1)

            conn.assign_attribute('test_namespace', 'test_key1', db1)
            conn.assign_attribute('test_namespace', 'test_key2', db1, 't1')
            conn.assign_attribute('test_namespace', 'test_key3', db1, 't2', 'c2')

            # Create TAttribute objects required for testing
            attributes = []
            attr1_db_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key1')
            attr2_tab_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key2')
            attr3_col_level = common.TestBase._get_t_attribute_obj('test_namespace', 'test_key3')

            # No Table should be returned.
            # Input tag is on DATABASE level and Match_Level = TABLE_ONLY
            attributes.append(attr1_db_level)
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_ONLY)
            self.assertTrue(len(datasets) == 0)

            # should return the table: t1
            # Input tag is on TABLE level and Match_Level = TABLE_ONLY
            attributes.clear()
            attributes.append(attr2_tab_level)
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_ONLY)
            self.assertTrue(len(datasets) == 1)
            for dataset in datasets:
                self.assertTrue(dataset.name == 't1')

            # No Table should be returned.
            # Input tag is on TABLE level and Match_Level = TABLE_ONLY
            attributes.clear()
            attributes.append(attr3_col_level)
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_ONLY)
            self.assertTrue(len(datasets) == 0)

            # should return the table: t1, t2
            # Input tags are on TABLE & COLUMN level and Match_Level = TABLE_PLUS
            attributes.clear()
            attributes.append(attr2_tab_level)
            attributes.append(attr3_col_level)
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.TABLE_PLUS)
            self.assertTrue(len(datasets) == 2)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue('t1' in returned_tbls)
            self.assertTrue('t2' in returned_tbls)

            # should return the table: t2
            # Input tags are on TABLE & COLUMN level and Match_Level = COLUMN_ONLY
            attributes.clear()
            attributes.append(attr2_tab_level)
            attributes.append(attr3_col_level)
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.COLUMN_ONLY)
            self.assertTrue(len(datasets) == 1)
            for dataset in datasets:
                self.assertTrue(dataset.name == 't2')

            # No Table should be returned.
            # Input tags are on DB, TABLE & COLUMN level and Match_Level = DATABASE_ONLY
            attributes.clear()
            attributes.append(attr1_db_level)
            attributes.append(attr2_tab_level)
            attributes.append(attr3_col_level)
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_ONLY)
            self.assertTrue(len(datasets) == 0)

            # should return the table: t1, t2, t3
            # Input tags are on DB, TABLE & COLUMN level and Match_Level = DATABASE_PLUS
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_PLUS)
            self.assertTrue(len(datasets) == 3)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue('t1' in returned_tbls)
            self.assertTrue('t2' in returned_tbls)
            self.assertTrue('t3' in returned_tbls)

            # test to verify that if a tag matches at the DB level, all the tables
            # within that DB (after honoring other filters) should be returned
            # should return the table: t1, t2, t3
            # Input tags are only on DB level and Match_Level = DATABASE_PLUS
            attributes.clear()
            attributes.append(attr1_db_level)
            datasets = conn.list_datasets(
                db1, tags=attributes, tag_match_level=TAttributeMatchLevel.DATABASE_PLUS)
            self.assertTrue(len(datasets) == 3)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue('t1' in returned_tbls)
            self.assertTrue('t2' in returned_tbls)
            self.assertTrue('t3' in returned_tbls)

            # drop databases
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db1)

    def test_connection_filter(self):
        """
            Test for connection_name filter only.
            No other filter would be input other than connection_name filter.
        """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # DB1 has TBL1 which is associated with PSQL_CXN
            # DB1 has TBL2 which is associated with PSQL_CXN
            # DB2 has TBL3 which is associated with PSQL_CXN
            # DB2 has TBL4 which is associated with MYSQL_CXN
            # Test user has 'ALL' on DB2 but no access on DB1

            #  ********** Run tests as Root User ************
            ctx.enable_token_auth(token_str=ROOT_USER)
            # list datasets for connection_name = PSQL_CXN
            # TBL1, TBL2 and TBL3 should be returned as they are associated with PSQL_CXN
            datasets = self._get_datasets(conn, connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 3)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for connection_name = MYSQL_CXN
            # only TLB4 should be returned as it is the only one associated with MYSQL_CXN
            datasets = self._get_datasets(conn, connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for connection_name which does not exist
            # API should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._get_datasets(conn, connection_name='non_existing_connection')
            self.assertTrue('AnalysisException: Connection name does not exist.'
                in str(ex_ctx.exception))

            #  ********** Run tests as Test User ************
            ctx.enable_token_auth(token_str=TEST_USER)
            # list datasets for connection_name = PSQL_CXN (Test user)
            # Test user has full access on DB2 but none on DB1
            # only TBL3 should be returned as it is in DB2 and associated with PSQL_CXN
            # TBL1 & TBL2 should not be returned as they are in DB1 and user has no access on DB1
            datasets = self._get_datasets(conn, connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 not in returned_tbls)
            self.assertTrue(TBL2 not in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for connection_name = MYSQL_CXN (Test user)
            # Test user has full access on DB2 but none on DB1
            # only TBL4 should be returned as it is in DB2 and associated with MYSQL_CXN
            datasets = self._get_datasets(conn, connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for connection_name which does not exist (Test user)
            # API should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._get_datasets(conn, connection_name='non_existing_connection')
            self.assertTrue('AnalysisException: Connection name does not exist.'
                in str(ex_ctx.exception))

    def test_connection_filter_should_not_return_internal_dbs(self):
        """
            Test for connection_name filter only.
            connection_filter should not return internal cralwer dbs.
        """
        INTERNAL_CRAWLER_DB = "_okera_crawler_connection_filter_test_db"
        TBL5 = "table_in_crawler_db"
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # DB1 has TBL1 which is associated with PSQL_CXN
            # DB1 has TBL2 which is associated with PSQL_CXN
            # DB2 has TBL3 which is associated with PSQL_CXN
            # DB2 has TBL4 which is associated with MYSQL_CXN
            # Test user has 'ALL' on DB2 but no access on DB1

            #  ********** Run tests as Root User ************
            ctx.enable_token_auth(token_str=ROOT_USER)
            # create internal crawler db and manually create TBL5 with PSQL_CXN
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % INTERNAL_CRAWLER_DB)
            conn.execute_ddl('CREATE DATABASE %s' % INTERNAL_CRAWLER_DB)
            conn.execute_ddl("""
                CREATE EXTERNAL TABLE %s.%s
                STORED as JDBC
                TBLPROPERTIES(
                'driver' = 'postgresql',
                'okera.connection.name' = '%s',
                'jdbc.db.name'='jdbc_test',
                'jdbc.schema.name'='public',
                'table' = '%s'
                )""" % (INTERNAL_CRAWLER_DB, TBL5, PSQL_CXN, TBL1))

            # list datasets for connection_name = PSQL_CXN
            # TBL1, TBL2 and TBL3 should be returned as they are associated with PSQL_CXN
            # TBL5 should not be returned as it is in internal crawler DB.
            datasets = self._get_datasets(conn, connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 3)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)
            self.assertTrue(TBL5 not in returned_tbls)

            # drop internal crawler db
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % INTERNAL_CRAWLER_DB)

    def test_conn_filter_with_databases_filter(self):
        """
            Test for connection_name filter in combination with database filter
        """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # DB1 has TBL1 which is associated with PSQL_CXN
            # DB1 has TBL2 which is associated with PSQL_CXN
            # DB2 has TBL3 which is associated with PSQL_CXN
            # DB2 has TBL4 which is associated with MYSQL_CXN
            # Test user has 'ALL' on DB2 but no access on DB1

            #  ********** Run tests as Root User ************
            ctx.enable_token_auth(token_str=ROOT_USER)
            # list datasets for DB1 (without specifying connection_name filter)
            # TBL1 and TBL2 should be returned  (and not TBL3 and TBL4)
            datasets = self._get_datasets(conn, databases=[DB1])
            self.assertTrue(len(datasets) == 2)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)

            # list datasets for DB2 (without specifying connection_name filter)
            # TBL3 and TBL4 should be returned  (and not TBL1 and TBL2)
            datasets = self._get_datasets(conn, databases=[DB2])
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for database = DB1 and connection_name = PSQL_CXN
            # TBL1 - returned as it's in DB1 and associated with PSQL_CXN
            # TBL2 - returned as it's in DB1 and associated with PSQL_CXN
            # TBL3 - not returned even though it is with PSQL_CXN as it's not in DB1
            # TBL4 - not returned as it's neither in DB1 and nor associated with PSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB1], connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)

            # list datasets for database = DB1 and connection_name = MYSQL_CXN
            # TBL1 and TBL2 - not returned as they are not associated with MYSQL_CXN
            # TBL3 and TBL4 - not returned as they are not in DB1
            datasets = self._get_datasets(conn, databases=[DB1], connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for database = DB2 and connection_name = PSQL_CXN
            # TBL1 - not returned even though it is with PSQL_CXN as it's not in DB2
            # TBL2 - not returned even though it is with PSQL_CXN as it's not in DB2
            # TBL3 - returned as it's in DB2 and associated with PSQL_CXN
            # TBL4 - not returned as it's not associated with PSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB2], connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for database = DB2 and connection_name = MYSQL_CXN
            # TBL1 - not returned as it's neither in DB2 and nor associated with MYSQL_CXN
            # TBL2 - not returned as it's neither in DB2 and nor associated with MYSQL_CXN
            # TBL3 - not returned as it's not associated with MYSQL_CXN
            # TBL4 - returned as it's in DB2 and associated with MYSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB2], connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL4 in returned_tbls)


            # list datasets for database = DB1,DB2 and connection_name = PSQL_CXN
            # TBL1 - returned as it's in DB1 and associated with PSQL_CXN
            # TBL2 - returned as it's in DB1 and associated with PSQL_CXN
            # TBL3 - returned as it's in DB2 and associated with PSQL_CXN
            # TBL4 - not returned as it's not associated with PSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB1, DB2],
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 3)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for aatabase = DB1 and connection_name = 'non_existing_connection'
            # API should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                datasets = self._get_datasets(conn, databases=[DB1],
                                              connection_name='non_existing_connection')
            self.assertTrue('AnalysisException: Connection name does not exist.'
                in str(ex_ctx.exception))

            #  ********** Run tests as Test User ************
            ctx.enable_token_auth(token_str=TEST_USER)

            # list datasets for database = DB1 (test user)
            # Test user has no access on DB1
            # so No Table should be returned
            datasets = self._get_datasets(conn, databases=[DB1])
            self.assertTrue(len(datasets) == 0)

            # list datasets for database = DB2 (test user)
            # Test user has full access on DB2
            # TBL3 and TBL4 should be returned
            datasets = self._get_datasets(conn, databases=[DB2])
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for database = DB1 and connection_name = PSQL_CXN (test user)
            # Test user has no access on DB1
            # so No Table should be returned
            datasets = self._get_datasets(conn, databases=[DB1], connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for database = DB1 and connection_name = MYSQL_CXN (test user)
            # Test user has no access on DB1
            # so No Table should be returned
            datasets = self._get_datasets(conn, databases=[DB1], connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for database = DB2 and connection_name = PSQL_CXN (test user)
            # Test user has full access on DB2
            # only TBL3 should be returned as it is in DB2 and associated with PSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB2], connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for database = DB2 and connection_name = MYSQL_CXN (test user)
            # Test user has full access on DB2
            # only TBL4 should be returned as it is in DB2 and associated with MYSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB2], connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for database = DB1,DB2 and connection_name = PSQL_CXN (test user)
            # Test user has no access on DB1
            # TBL1 - not returned as it's in DB1
            # TBL2 -  not returned as it's in DB1
            # TBL3 - returned as it's in DB2 and associated with PSQL_CXN
            # TBL4 - not returned as it's not associated with PSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB1, DB2],
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for aatabase = DB1 and connection_name = 'non_existing_connection' (test user)
            # API should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                datasets = self._get_datasets(conn, databases=[DB1],
                                              connection_name='non_existing_connection')
            self.assertTrue('AnalysisException: Connection name does not exist.'
                in str(ex_ctx.exception))

            ctx.enable_token_auth(token_str=ROOT_USER)

    def test_conn_filter_with_pattern_filter(self):
        """
            Test for connection_name filter in combination with DBs and filter string
        """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # DB1 has TBL1 which is associated with PSQL_CXN
            # DB1 has TBL2 which is associated with PSQL_CXN
            # DB2 has TBL3 which is associated with PSQL_CXN
            # DB2 has TBL4 which is associated with MYSQL_CXN
            # Test user has 'ALL' on DB2 but no access on DB1

            #  ********** Run tests as Root User ************
            ctx.enable_token_auth(token_str=ROOT_USER)
            # list datasets for DB1 and filter='types'
            # only TBL1 should be returned as it's in DB1 and its name matches the pattern
            datasets = self._get_datasets(conn, databases=[DB1], filter='types')
            self.assertTrue(len(datasets) == 1)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)

            # list datasets for DB2 and filter='types'
            # only TBL3 should be returned as it's in DB2 and its name matches the pattern
            datasets = self._get_datasets(conn, databases=[DB2], filter='types')
            self.assertTrue(len(datasets) == 1)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for databases=DB1, filter='types' and connection_name=PSQL_CXN
            # only TBL1 should be returned as it's in DB1 and its name matches the pattern
            # and it's also associated with PSQL_CXN
            datasets = self._get_datasets(conn, databases=[DB1], filter='types',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)

            # list datasets for databases=DB1, filter='types' and connection_name=MYSQL_CXN
            # No table should be returned none of them qualify for all three conditions
            datasets = self._get_datasets(conn, databases=[DB1], filter='types',
                                          connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for DB2 and filter='numeric' and connection_name=MYSQL_CXN
            # only TBL4 should be returned as it qualifies for all three conditions
            datasets = self._get_datasets(conn, databases=[DB2], filter='test',
                                          connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for DB2 and filter='test' and connection_name=PSQL_CXN
            # No table should be returned none of them qualify for all three conditions
            datasets = self._get_datasets(conn, databases=[DB2], filter='test',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for DB1 & DB2 and filter='types'
            # TBL1 should be returned as it's in DB1 and its name matches the pattern
            # TBL3 should be returned as it's in DB2 and its name matches the pattern
            datasets = self._get_datasets(conn, databases=[DB1,DB2], filter='test')
            self.assertTrue(len(datasets) == 2)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for DB1 & DB2 and filter='non_existing_pattern'
            # No Table sould be returned due to failure of filter condition
            datasets = self._get_datasets(conn, databases=[DB1,DB2],
                                          filter='non_existing_pattern')
            self.assertTrue(len(datasets) == 0)

            # list datasets for DB1 & DB2 and filter='test' and connection_name=PSQL_CXN
            # only TBL2 should be returned as it qualifies for all three conditions
            datasets = self._get_datasets(conn, databases=[DB1,DB2], filter='test',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL2 in returned_tbls)

            # list datasets for DB1 & DB2 and filter='test' and connection_name=MYSQL_CXN
            # only TBL4 should be returned as it qualifies for all three conditions
            datasets = self._get_datasets(conn, databases=[DB1,DB2], filter='test',
                                          connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls = []
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for DB1 & DB2 and filter='non_existing_pattern' and connection_name=MYSQL_CXN
            # No Table sould be returned due to failure of filter condition
            datasets = self._get_datasets(conn, databases=[DB1,DB2],
                                          filter='non_existing_pattern',
                                          connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for DB1 & DB2 and filter='test' and connection_name='non_existing_connection'
            # API should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                datasets = self._get_datasets(conn, databases=[DB1,DB2],
                                              filter='test',
                                              connection_name='non_existing_connection')
            self.assertTrue('AnalysisException: Connection name does not exist.'
                in str(ex_ctx.exception))

    def test_conn_filter_with_tag_filter(self):
        """
            Test for connection_name filter in combination with tag filter.
            Scenarios with other filter combinations would also be tested.
        """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # DB1 has TBL1 which is associated with PSQL_CXN
            # DB1 has TBL2 which is associated with PSQL_CXN
            # DB2 has TBL3 which is associated with PSQL_CXN
            # DB2 has TBL4 which is associated with MYSQL_CXN
            # DB1.TBL1 has TAG1
            # DB1.TBL2 has TAG2
            # DB2.TBL3 has TAG1
            # DB2.TBL4 has TAG2
            # Test user has 'ALL' on DB2 but no access on DB1

            # Create TAttribute objects required for testing
            T_TAG1 = common.TestBase._get_t_attribute_obj(NAMESPACE, TAG1)
            T_TAG2 = common.TestBase._get_t_attribute_obj(NAMESPACE, TAG2)
            T_NON_EXISTING_TAG = common.TestBase._get_t_attribute_obj(NAMESPACE, 'non_existing_tag')

            #  ********** Run tests as Root User ************
            ctx.enable_token_auth(token_str=ROOT_USER)
            returned_tbls = []

            # ****** Test cases for "Tag filters" only
            # list datasets for tags=TAG1 & TAG2 and tag_match_level=DATABASE_PLUS
            # TBL1, TB2, TBL3 and TBL4 all of them should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='DATABASE_PLUS')
            self.assertTrue(len(datasets) == 4)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for tags=TAG1 & TAG2 and tag_match_level=DATABASE_ONLY
            # No tables should be returned as both the tags are on TABLE level
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='DATABASE_ONLY')
            self.assertTrue(len(datasets) == 0)

            # list datasets for tags=TAG1 & TAG2 and tag_match_level=TABLE_PLUS
            # TBL1, TB2, TBL3 and TBL4 all of them should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_PLUS')
            self.assertTrue(len(datasets) == 4)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for tags=TAG1 & TAG2 and tag_match_level=TABLE_ONLY
            # TBL1, TB2, TBL3 and TBL4 all of them should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY')
            self.assertTrue(len(datasets) == 4)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for tags=TAG1 & TAG2 and tag_match_level=COLUMN_ONLY
            # No tables should be returned as both the tags are on TABLE level
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='COLUMN_ONLY')
            self.assertTrue(len(datasets) == 0)

            # ********* Test cases for 'connection filter' with 'Tag filter' *******

            # list datasets for tags=TAG1 & TAG2 and connection_name=PSQL_CXN
            # TBL1, TB2 & TBL3 should be returned as they qualify for the conditions
            # TBL4 should not be returned as it's not associated with PSQL_CXN
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 3)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)


            # list datasets for tags=TAG1 & TAG2 and connection_name=PSQL_CXN
            # No tables should be returned as both the tags are on TABLE level
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='DATABASE_ONLY',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for tags=TAG2 and connection_name=MYSQL_CXN
            # only TBL4 should be returned as they qualify for the conditions
            # TBL1 & TBL3 should not be returned as they do not have TAG2
            # TBL2 should not be returned as it's not associated with MYSQL_CXN
            datasets = self._get_datasets(conn, tags=[T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          connection_name=MYSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL4 in returned_tbls)

            # list datasets for tags=TAG1 and connection_name=PSQL_CXN
            # TBL1 & TBL3 should be returned as they qualify for the conditions
            # TBL2 should not be returned as it does not have TAG1
            # TBL4 should not be returned as it's not associated with PSQL_CXN
            datasets = self._get_datasets(conn, tags=[T_TAG1],
                                          tag_match_level='TABLE_ONLY',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for tags=NON_EXISTING_TAG and connection_name=PSQL_CXN
            # No Table should be returned
            datasets = self._get_datasets(conn, tags=[T_NON_EXISTING_TAG],
                                          tag_match_level='TABLE_ONLY',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 0)

            # list datasets for tags=TAG1 & TAG2 and connection_name='non_existing_connection'
            # API should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                              tag_match_level='TABLE_ONLY',
                                              connection_name='non_existing_connection')
            self.assertTrue('AnalysisException: Connection name does not exist.'
                in str(ex_ctx.exception))

    def test_multiple_filter_combinations(self):
        """
            Test for multiple combinations of filters.
        """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # DB1 has TBL1 which is associated with PSQL_CXN
            # DB1 has TBL2 which is associated with PSQL_CXN
            # DB2 has TBL3 which is associated with PSQL_CXN
            # DB2 has TBL4 which is associated with MYSQL_CXN
            # DB1.TBL1 has TAG1
            # DB1.TBL2 has TAG2
            # DB2.TBL3 has TAG1
            # DB2.TBL4 has TAG2
            # Test user has 'ALL' on DB2 but no access on DB1

            # Create TAttribute objects required for testing
            T_TAG1 = common.TestBase._get_t_attribute_obj(NAMESPACE, TAG1)
            T_TAG2 = common.TestBase._get_t_attribute_obj(NAMESPACE, TAG2)
            T_NON_EXISTING_TAG = common.TestBase._get_t_attribute_obj(NAMESPACE, 'non_existing_tag')

            #  ********** Run tests as Root User ************
            ctx.enable_token_auth(token_str=ROOT_USER)
            returned_tbls = []

            ### Filter combination: tag, filter string, connection
            # list datasets for tags=TAG1 & TAG2, filter='test' & connection_name=PSQL_CXN
            # only TBL2 should be returned as it qualifies for all three conditions
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY', filter='test',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL2 in returned_tbls)

            ### Filter combination: tag, filter string, connection
            # list datasets for tags=TAG1 & TAG2, filter='types' & connection_name=PSQL_CXN
            # TBL1 & TBL3 should be returned as it qualifies for all three conditions
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY', filter='types',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)

            ### Filter combination: database names, tag, filter string, connection
            # list datasets for databases =  DB1, tags = TAG1 & TAG2, filter='types'
            # and connection_name=PSQL_CXN
            # only TBL1 should be returned as it qualifies for all four conditions
            datasets = self._get_datasets(conn, databases=[DB1], tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY', filter='types',
                                          connection_name=PSQL_CXN)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)

            ### Filter combination: dataset names and tags
            # list datasets for datasets =  TBL1, TBL2 & TBL3 and Tags = TAG1 & TAG2
            # TBL1 and TBL3 should be returned as they qualify for both conditions
            dataset_names = [(DB1 + '.' + TBL1), (DB1 + '.' + TBL2), (DB2 + '.' + TBL3)]
            datasets = self._get_datasets(conn, dataset_names=dataset_names,
                                          tags=[T_TAG1],
                                          tag_match_level='TABLE_ONLY')
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL3 in returned_tbls)

            ### Filter combination: dataset names and tags
            # list datasets for datasets = TBL1, TBL2 & TBL3 and Tags = T_NON_EXISTING_TAG
            # No Table qualifies for T_NON_EXISTING_TAG
            dataset_names = [(DB1 + '.' + TBL1), (DB1 + '.' + TBL2), (DB2 + '.' + TBL3)]
            datasets = self._get_datasets(conn, dataset_names=dataset_names,
                                          tags=[T_NON_EXISTING_TAG],
                                          tag_match_level='TABLE_ONLY')
            self.assertTrue(len(datasets) == 0)

    def test_invalid_filter_combinations(self):
        """ Test for verifying that certain filter combinations do not work. For example:
            - dataset_names and databases       can not be specified together
            - dataset_names and filter string   can not be specified together
            - dataset_names and connection_name can not be specified together
        """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:

            dataset_names = [(DB1 + '.' + TBL1), (DB2 + '.' + TBL3)]
            databases = [DB1, DB2]
            filter = 'numeric'
            connection_name = PSQL_CXN

            # verifying dataset_names and databases filter combination
            # api should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._get_datasets(conn, dataset_names=dataset_names, databases=databases)
            self.assertTrue(
                'AnalysisException: Cannot specify both dataset_names and databases.'
                in str(ex_ctx.exception))

            # verifying dataset_names and filter string combination
            # api should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._get_datasets(conn, dataset_names=dataset_names, filter=filter)
            self.assertTrue(
                'AnalysisException: Cannot specify both dataset_names and filter.'
                in str(ex_ctx.exception))

            # verifying dataset_names and connection_name filter combination
            # api should throw an AnalysisException
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                self._get_datasets(conn, dataset_names=dataset_names, connection_name=connection_name)
            self.assertTrue(
                'AnalysisException: Cannot specify both dataset_names and connection_name.'
                in str(ex_ctx.exception))

    def test_pagination(self):
        """
            Test pagination with multiple filter combinations.
        """
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # DB1 has TBL1 which is associated with PSQL_CXN
            # DB1 has TBL2 which is associated with PSQL_CXN
            # DB2 has TBL3 which is associated with PSQL_CXN
            # DB2 has TBL4 which is associated with MYSQL_CXN
            # DB1.TBL1 has TAG1
            # DB1.TBL2 has TAG2
            # DB2.TBL3 has TAG1
            # DB2.TBL4 has TAG2
            # Test user has 'ALL' on DB2 but no access on DB1

            # Create TAttribute objects required for testing
            T_TAG1 = common.TestBase._get_t_attribute_obj(NAMESPACE, TAG1)
            T_TAG2 = common.TestBase._get_t_attribute_obj(NAMESPACE, TAG2)
            T_NON_EXISTING_TAG = common.TestBase._get_t_attribute_obj(NAMESPACE, 'non_existing_tag')

            #  ********** Run tests as Root User ************
            ctx.enable_token_auth(token_str=ROOT_USER)
            returned_tbls = []

            # *********** Pagination with Tag filters *********
            # list datasets for tags=TAG1 & TAG2 and offset=0, count=2 (page 1)
            # TBL1, TB2 should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          offset=0, count=2)
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)

            # list datasets for tags=TAG1 & TAG2 and offset=2, count=2  (page 2)
            # TBL3, TB4 should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          offset=2, count=2)
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)
            self.assertTrue(TBL4 in returned_tbls)

            # *********** Pagination with Tag and Connection filters *********
            # list datasets for tags=TAG1 & TAG2 , connection_name=PSQL_CXN
            # and offset=0, count=2  (page 1)
            # TBL1, TB2 should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          connection_name=PSQL_CXN,
                                          offset=0, count=2)
            self.assertTrue(len(datasets) == 2)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)
            self.assertTrue(TBL2 in returned_tbls)

            # list datasets for tags=TAG1 & TAG2 , connection_name=PSQL_CXN
            # and offset=2, count=2  (page 2)
            # only TBL3 should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          connection_name=PSQL_CXN,
                                          offset=2, count=2)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL3 in returned_tbls)

            # list datasets for tags=TAG1 & TAG2 , connection_name=PSQL_CXN
            # and offset=4, count=2  (page 3)
            # No Table should be returned
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          connection_name=PSQL_CXN,
                                          offset=4, count=2)
            self.assertTrue(len(datasets) == 0)

            # *********** Pagination with Tag and 'filter string' filters *********
            # list datasets for tags=TAG1 & TAG2 , filter='types'
            # and offset=0, count=2  (page 1)
            # only TBL1 should be returned
            # BUG: There is a bug here. Ideally, TBL1 and TBL3 should be returned as
            # both of them qualify for the conditions. However, we carry out the
            # pagination before applying the 'filter string', that's why result is incorrect.
            # TODO: Rethink and Rewrite the pagination logic
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          filter='types',
                                          offset=0, count=2)
            self.assertTrue(len(datasets) == 1)
            returned_tbls.clear()
            for dataset in datasets:
                returned_tbls.append(dataset.name)
            self.assertTrue(TBL1 in returned_tbls)

            # *********** Pagination with Tag and dataset_names filters *********
            # list datasets for tags=TAG1 & TAG2 , dataset_names=DB2.TBL3
            # and offset=0, count=2  (page 1)
            # No Table should be returned.
            # BUG: There is a bug here. Ideally, TBL3 should be returned as it qualifies
            # for the input conditions. However, we carry out the pagination twice
            # in case of dataset_names filter, that's why result is incorrect.
            # TODO: Rethink and Rewrite the pagination logic
            dataset_names = dataset_names = [DB2 + '.' + TBL3]
            datasets = self._get_datasets(conn, tags=[T_TAG1,T_TAG2],
                                          tag_match_level='TABLE_ONLY',
                                          dataset_names=dataset_names,
                                          offset=0, count=2)
            self.assertTrue(len(datasets) == 0)

    def test_list_datasets_is_public(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            role = "list_datasets_is_public_role"
            user = "list_datasets_is_public_role_user"
            db = "list_datasets_is_public_role_db"
            tbl1 = "%s.tbl1" % (db)
            tbl2 = "%s.tbl2" % (db)

            ctx.disable_auth()
            setup_ddls = [
                # Create a role and grant it to the user
                # This role will have an ABAC permission on a DB,
                # and the user should not see the tables in that DB as public
                "DROP ROLE IF EXISTS %s" % (role),
                "CREATE ROLE %s" % (role),
                "GRANT ROLE %s TO GROUP %s" % (role, user),

                # Create a DB and tables that we can grant on
                "DROP DATABASE IF EXISTS %s CASCADE" % (db),
                "CREATE DATABASE %s" % (db),
                "CREATE TABLE %s (col1 string)" % (tbl1),
                "CREATE TABLE %s (col1 string)" % (tbl2),

                # Grant an ABAC privilege on one of the tables
                "GRANT SELECT ON TABLE %s WHERE 1 = 1 TO ROLE %s" % (tbl1, role),

                # Grant the other table to the public role
                "GRANT SELECT ON TABLE %s TO ROLE %s" % (tbl2, "okera_public_role"),
            ]

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            # Switch to the user
            ctx.enable_token_auth(token_str=user)

            # `tbl1` should not be public even though it has an ABAC
            # privilege on it.
            request = TGetDatasetsParams()
            request.dataset_names = [tbl1]
            request.requesting_user = user
            res = conn._underlying_client().GetDatasets(request)
            assert len(res.datasets) == 1
            assert len(res.is_public) == 1
            assert res.is_public[0] == False

            # `tbl2` should be public as it is granted to okera_public_role
            request = TGetDatasetsParams()
            request.dataset_names = [tbl2]
            request.requesting_user = user
            res = conn._underlying_client().GetDatasets(request)
            assert len(res.datasets) == 1
            assert len(res.is_public) == 1
            assert res.is_public[0] == True

    def test_list_datasets_with_db(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            role = "list_datasets_is_public_role"
            user = "list_datasets_is_public_role_user"
            db = "list_datasets_is_public_role_db1"
            tbl = "%s.tbl1" % (db)

            ctx.disable_auth()
            setup_ddls = [
                # Create a role and grant it to the user
                # This role will have an ABAC permission on a DB,
                # and the user should not see the tables in that DB as public
                "DROP ROLE IF EXISTS %s" % (role),
                "CREATE ROLE %s" % (role),
                "GRANT ROLE %s TO GROUP %s" % (role, user),

                # Create a DB and tables that we can grant on
                "DROP DATABASE IF EXISTS %s CASCADE" % (db),
                "CREATE DATABASE %s" % (db),
                "CREATE TABLE %s (col1 string)" % (tbl),

                "GRANT SELECT ON DATABASE %s TO ROLE %s" % (db, role),
            ]

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            # Switch to the user
            ctx.enable_token_auth(token_str=user)

            tbl_name = tbl.split(".")[1]

            datasets = conn.list_datasets(db)
            assert len(datasets) == 1
            assert datasets[0].name == tbl_name and datasets[0].db[0] == db

            datasets = conn.list_datasets(db, filter=tbl_name)
            assert len(datasets) == 1
            assert datasets[0].name == tbl_name and datasets[0].db[0] == db

            datasets = conn.list_datasets(db, name=tbl_name)
            assert len(datasets) == 1
            assert datasets[0].name == tbl_name and datasets[0].db[0] == db

    def test_list_datasets_count_only(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            role = "list_datasets_count_only_role"
            user = "list_datasets_count_only_user"
            db1 = "list_datasets_count_only_db1"
            tbl11 = "%s.tbl1" % (db1)
            tbl12 = "%s.tbl2" % (db1)
            db2 = "list_datasets_count_only_db2"
            tbl21 = "%s.tbl1" % (db2)
            tbl22 = "%s.tbl2" % (db2)

            ctx.disable_auth()
            setup_ddls = [
                # Create a role and grant it to the user
                # This role will have an ABAC permission on a DB,
                # and the user should not see the tables in that DB as public
                "DROP ROLE IF EXISTS %s" % (role),
                "CREATE ROLE %s" % (role),
                "GRANT ROLE %s TO GROUP %s" % (role, user),

                # Create a DB and tables that we can grant on
                "DROP DATABASE IF EXISTS %s CASCADE" % (db1),
                "CREATE DATABASE %s" % (db1),
                "CREATE TABLE %s (col1 string)" % (tbl11),
                "CREATE TABLE %s (col1 string)" % (tbl12),
                "DROP DATABASE IF EXISTS %s CASCADE" % (db2),
                "CREATE DATABASE %s" % (db2),
                "CREATE TABLE %s (col1 string)" % (tbl21),
                "CREATE TABLE %s (col1 string)" % (tbl22),

                # Grant on the DB and tables
                "GRANT SELECT ON DATABASE %s TO ROLE %s" % (db1, role),
                "GRANT SELECT ON TABLE %s TO ROLE %s" % (tbl22, role),
            ]

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            # Switch to the user
            ctx.enable_token_auth(token_str=user)

            # Verify the total count for our user is = 3 and
            # contains our tables
            request = TGetDatasetsParams()
            request.requesting_user = user
            request.databases = [db1, db2]
            request.count_only = True
            request.names_only = True
            res = conn._underlying_client().GetDatasets(request)
            tables = get_table_names(res)
            assert len(tables) == 3
            assert tbl11 in tables
            assert tbl12 in tables
            assert tbl21 not in tables
            assert tbl22 in tables

            # Verify it handles filters
            request = TGetDatasetsParams()
            request.requesting_user = user
            request.databases = [db1, db2]
            request.filter = 'tbl1'
            request.count_only = True
            request.names_only = True
            res = conn._underlying_client().GetDatasets(request)
            tables = get_table_names(res)
            assert len(tables) == 1
            assert tbl11 in tables
            assert tbl12 not in tables
            assert tbl21 not in tables
            assert tbl22 not in tables

            # Verify only name_only+count_only will work
            request = TGetDatasetsParams()
            request.requesting_user = user
            request.databases = [db1, db2]
            request.count_only = True
            request.names_only = False
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                res = conn._underlying_client().GetDatasets(request)
            self.assertTrue('Cannot specify count_only without names_only' in str(ex_ctx.exception))

            # Verify count_only + dataset names fails
            request = TGetDatasetsParams()
            request.requesting_user = user
            request.dataset_names = [tbl11]
            request.count_only = True
            request.names_only = True
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                res = conn._underlying_client().GetDatasets(request)
            self.assertTrue('Cannot specify both dataset_names and count_only' in str(ex_ctx.exception))

if __name__ == "__main__":
    unittest.main()
