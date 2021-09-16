# Copyright 2021 Okera Inc. All Rights Reserved.
#
# Some scenario tests for steward delegation
#
# pylint: disable=broad-except
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals
# pylint: disable=bad-continuation
# pylint: disable=broad-except

from okera import context
from okera.tests import pycerebro_test_common as common

from okera import _thrift_api

# User and role that are stewards
ROLE = "steward_test_role"
ROLE_MANAGING = "steward_test_role_managing"
USER = "stewardtestuser"
USER_ROLE = "_okera_internal_role_%s" % USER
USER_NO_ACCESS = "stewardtestusernoaccess"
USER_NORMAL = 'stewardtestusernormal'
USER_NORMAL_ROLE = "_okera_internal_role_%s" % USER_NORMAL

# Objects granted stewardship over
CXN = "steward_test_connection"
DB = "steward_test_db"
TBL = "%s.steward_test_table" % (DB)

class StewardTest(common.TestBase):
    # Test granting AS OWNER on the catalog for creating
    # both connections and databases
    def test_steward_1(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()

            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % (DB),
                "DROP DATACONNECTION IF EXISTS %s" % (CXN),
                "DROP ROLE IF EXISTS %s" % (ROLE),
                "DROP ROLE IF EXISTS %s" % (USER_ROLE),

                # Create the role and grant it to the user
                "CREATE ROLE %s" % (ROLE),
                "GRANT ROLE %s TO GROUP %s" % (ROLE, USER),

                # Grant the role the right permissions
                "GRANT CREATE_AS_OWNER ON CATALOG TO ROLE %s" % (ROLE),
                "GRANT CREATE_DATACONNECTION_AS_OWNER ON CATALOG TO ROLE %s" % (ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # Create the connection, DB and table
            ddls = [
                """CREATE DATACONNECTION %s CXNPROPERTIES
                    (
                    'connection_type'='JDBC',
                    'jdbc_driver'='mysql',
                    'host'='cerebro-db-test-long-running.cyn8yfvyuugz.us-west-2.rds.amazonaws.com',
                    'port'='3306',
                    'user_key'='awsps:///mysql/username',
                    'password_key'='awsps:///mysql/password',
                    'jdbc.db.name'='jdbc_test'
                    )
                """ % (CXN),

                "CREATE DATABASE %s" % (DB),
                """CREATE EXTERNAL TABLE %s STORED as JDBC
                        TBLPROPERTIES(
                        'driver' = 'mysql',
                        'okera.connection.name' = '%s',
                        'jdbc.db.name'='jdbc_test',
                        'jdbc.schema.name'='public',
                        'table' = 'filter_pushdown_test'
                )""" % (TBL, CXN)
            ]

            # First, do a check that the "no access" user does not
            # have access to create the objects
            ctx.enable_token_auth(token_str=USER_NO_ACCESS)

            for ddl in ddls:
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl(ddl)
                self.assertTrue('not have privileges' in str(ex_ctx.exception))

            # Now, check on the real user
            ctx.enable_token_auth(token_str=USER)

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = conn.scan_as_json('select bigint_col from %s WHERE smallint_col=2' % (TBL))
            assert len(res) == 1
            assert res[0]['bigint_col'] == 4

    # Test granting AS OWNER on the catalog for creating
    # connections, but pre-create the DB and grant access
    # on it (we use CREATE_AS_OWNER so the user can also
    # select on it)
    def test_steward_2(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()

            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % (DB),
                "DROP DATACONNECTION IF EXISTS %s" % (CXN),
                "DROP ROLE IF EXISTS %s" % (ROLE),
                "DROP ROLE IF EXISTS %s" % (USER_ROLE),

                # Create the role and grant it to the user
                "CREATE ROLE %s" % (ROLE),
                "GRANT ROLE %s TO GROUP %s" % (ROLE, USER),

                # Create the DB
                "CREATE DATABASE %s" % (DB),

                # Grant the role the right permissions
                "GRANT CREATE_DATACONNECTION_AS_OWNER ON CATALOG TO ROLE %s" % (ROLE),
                "GRANT CREATE_AS_OWNER ON DATABASE %s TO ROLE %s" % (DB, ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # Create the connection, DB and table
            ddls = [
                """CREATE DATACONNECTION %s CXNPROPERTIES
                    (
                    'connection_type'='JDBC',
                    'jdbc_driver'='mysql',
                    'host'='cerebro-db-test-long-running.cyn8yfvyuugz.us-west-2.rds.amazonaws.com',
                    'port'='3306',
                    'user_key'='awsps:///mysql/username',
                    'password_key'='awsps:///mysql/password',
                    'jdbc.db.name'='jdbc_test'
                    )
                """ % (CXN),

                """CREATE EXTERNAL TABLE %s STORED as JDBC
                        TBLPROPERTIES(
                        'driver' = 'mysql',
                        'okera.connection.name' = '%s',
                        'jdbc.db.name'='jdbc_test',
                        'jdbc.schema.name'='public',
                        'table' = 'filter_pushdown_test'
                )""" % (TBL, CXN)
            ]

            # First, do a check that the "no access" user does not
            # have access to create the objects
            ctx.enable_token_auth(token_str=USER_NO_ACCESS)

            for ddl in ddls:
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl(ddl)
                self.assertTrue('not have privileges' in str(ex_ctx.exception))

            # Now, check on the real user
            ctx.enable_token_auth(token_str=USER)

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = conn.scan_as_json('select bigint_col from %s WHERE smallint_col=2' % (TBL))
            assert len(res) == 1
            assert res[0]['bigint_col'] == 4

    # Test ensuring that a steward can create tables using
    # CREATE TABLE LIKE FILE
    def test_steward_3(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()

            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % (DB),
                "DROP ROLE IF EXISTS %s" % (ROLE),
                "DROP ROLE IF EXISTS %s" % (USER_ROLE),

                # Create the role and grant it to the user
                "CREATE ROLE %s" % (ROLE),
                "GRANT ROLE %s TO GROUP %s" % (ROLE, USER),

                # Create the DB
                "CREATE DATABASE %s" % (DB),

                # Grant the role the right permissions
                "GRANT CREATE_AS_OWNER ON DATABASE %s TO ROLE %s" % (DB, ROLE),
                "GRANT ALL ON URI 's3://cerebrodata-test/' TO ROLE %s" % (ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # Create the connection, DB and table
            ddls = [
                """CREATE EXTERNAL TABLE %s
                   LIKE PARQUET 's3://cerebrodata-test/alltypes_parquet'
                   STORED AS PARQUET
                   LOCATION 's3://cerebrodata-test/alltypes_parquet'""" % (TBL)
            ]

            # First, do a check that the "no access" user does not
            # have access to create the objects
            ctx.enable_token_auth(token_str=USER_NO_ACCESS)

            for ddl in ddls:
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl(ddl)
                self.assertTrue('not have privileges' in str(ex_ctx.exception))

            # Now, check on the real user
            ctx.enable_token_auth(token_str=USER)

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = conn.scan_as_json('select count(*) as cnt from %s' % (TBL))
            assert len(res) == 1
            assert res[0]['cnt'] == 8

    # End-to-end test including role management delegation:
    # 1. Grant the steward the following abilities:
    #       * Creating roles
    #       * Creating tables in our test DB
    #       * URI access on the necessary URI
    #       * Grant option on the test DB
    # 2. Steward creates a test role, creates a table, and grants
    #    access on the table to the normal user
    # 3. Normal user can now run the query
    def test_steward_4(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()

            ddls = [
                "DROP DATABASE IF EXISTS %s CASCADE" % (DB),
                "DROP ROLE IF EXISTS %s" % (ROLE),
                "DROP ROLE IF EXISTS %s" % (USER_ROLE),
                "DROP ROLE IF EXISTS %s" % (ROLE_MANAGING),
                "DROP ROLE IF EXISTS %s" % (USER_NORMAL_ROLE),

                # Create the role and grant it to the user
                "CREATE ROLE %s" % (ROLE),
                "GRANT ROLE %s TO GROUP %s" % (ROLE, USER),

                # Create the DB
                "CREATE DATABASE %s" % (DB),

                # Grant the role the right permissions
                "GRANT CREATE_AS_OWNER ON DATABASE %s TO ROLE %s" % (DB, ROLE),
                "GRANT ALL ON URI 's3://cerebrodata-test/' TO ROLE %s" % (ROLE),
                "GRANT CREATE_ROLE_AS_OWNER ON CATALOG TO ROLE %s" % (ROLE),
                "GRANT SELECT ON DATABASE %s TO ROLE %s WITH GRANT OPTION" % (DB, ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # Create the connection, DB and table
            ddls = [
                "CREATE ROLE %s" % (ROLE_MANAGING),

                """CREATE EXTERNAL TABLE %s
                   LIKE PARQUET 's3://cerebrodata-test/alltypes_parquet'
                   STORED AS PARQUET
                   LOCATION 's3://cerebrodata-test/alltypes_parquet'""" % (TBL),

                "GRANT SELECT ON TABLE %s TO ROLE %s" % (TBL, ROLE_MANAGING),
                "GRANT ROLE %s TO GROUP %s" % (ROLE_MANAGING, USER_NORMAL),
            ]

            # First, do a check that the "no access" user does not
            # have access to create the objects
            ctx.enable_token_auth(token_str=USER_NO_ACCESS)

            for ddl in ddls:
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl(ddl)
                self.assertTrue(
                    'not have privileges' in str(ex_ctx.exception) or
                    'does not exist' in str(ex_ctx.exception))

            # Now, check on the real user
            ctx.enable_token_auth(token_str=USER)

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # Now, switch to a normal user (who was just granted access to this
            # table), and verify they can run a query
            ctx.enable_token_auth(token_str=USER_NORMAL)

            res = conn.scan_as_json('select count(*) as cnt from %s' % (TBL))
            assert len(res) == 1
            assert res[0]['cnt'] == 8

            # Verify the no access user can't run the query
            ctx.enable_token_auth(token_str=USER_NO_ACCESS)

            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.scan_as_json('select count(*) as cnt from %s' % (TBL))
            self.assertTrue('not have privileges' in str(ex_ctx.exception))