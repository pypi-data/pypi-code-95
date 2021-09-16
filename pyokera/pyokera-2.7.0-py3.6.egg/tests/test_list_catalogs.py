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
from okera._thrift_api import (TAccessPermissionLevel, TAccessPermissionScope)

class ListCatalogsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(ListCatalogsTest, cls).setUpClass()

    def test_list_catalogs(self):
        TEST_USER1 = 'list_catalogs_test_user1'
        TEST_USER2 = 'list_catalogs_test_user2'
        TEST_ROLE1 = 'list_catalogs_test_role1'
        TEST_ROLE2 = 'list_catalogs_test_role2'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP ROLE IF EXISTS %s'% TEST_ROLE1)
            conn.execute_ddl('CREATE ROLE %s' % TEST_ROLE1)
            conn.execute_ddl('DROP ROLE IF EXISTS %s'% TEST_ROLE2)
            conn.execute_ddl('CREATE ROLE %s' % TEST_ROLE2)
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE1, TEST_USER1))
            conn.execute_ddl('GRANT ROLE %s TO GROUP %s' % (TEST_ROLE2, TEST_USER2))
            # Grant some catalog privileges to role1 but none to role2
            conn.execute_ddl('GRANT CREATE ON CATALOG TO ROLE %s'% TEST_ROLE1)
            conn.execute_ddl('GRANT SELECT ON CATALOG TO ROLE %s'% TEST_ROLE1)
            conn.execute_ddl('GRANT CREATE_AS_OWNER ON CATALOG TO ROLE %s'% TEST_ROLE1)

            # list Catalogs test (with "root" as requesting_user)
            result = conn.list_catalogs(requesting_user='root')
            self.assertTrue(len(result.catalogs) == 1)
            for catalog in result.catalogs:
                self.assertTrue(catalog.name == 'okera')
                catalog_privs = catalog.access_levels[TAccessPermissionScope.SERVER]
                assert TAccessPermissionLevel.ALL in catalog_privs

            # list Catalogs test (with no requesting_user)
            result = conn.list_catalogs()
            self.assertTrue(len(result.catalogs) == 1)
            for catalog in result.catalogs:
                self.assertTrue(catalog.name == 'okera')
                catalog_privs = catalog.access_levels[TAccessPermissionScope.SERVER]
                assert TAccessPermissionLevel.ALL in catalog_privs

            # list Catalogs test (with TEST_USER1 as requesting_use)
            result = conn.list_catalogs(requesting_user=TEST_USER1)
            self.assertTrue(len(result.catalogs) == 1)
            for catalog in result.catalogs:
                self.assertTrue(catalog.name == 'okera')
                catalog_privs = catalog.access_levels[TAccessPermissionScope.SERVER]
                assert TAccessPermissionLevel.CREATE in catalog_privs
                assert TAccessPermissionLevel.SELECT in catalog_privs
                assert TAccessPermissionLevel.CREATE_AS_OWNER in catalog_privs

            # list Catalogs test (No access levels for the TEST_USER2)
            result = conn.list_catalogs(requesting_user=TEST_USER2)
            self.assertTrue(len(result.catalogs) == 1)
            for catalog in result.catalogs:
                self.assertTrue(catalog.name == 'okera')
                catalog_privs = catalog.access_levels[TAccessPermissionScope.SERVER]
                self.assertTrue(len(catalog_privs) == 0)

            # Set up a user with only SELECT and check catalog permission
            role = 'list_catalogs_temp_role'
            user = 'list_catalogs_temp_user'
            ctx.enable_token_auth('root')
            conn.execute_ddl("create role if not exists {}".format(role))
            conn.execute_ddl("GRANT ROLE {} TO GROUP {}".format(role, user))
            conn.execute_ddl("GRANT SELECT ON CATALOG TO ROLE {}".format(role))
            ctx.enable_token_auth(user)
            result = conn.list_catalogs(user)
            for catalog in result.catalogs:
                self.assertTrue(catalog.name == 'okera')
                catalog_privs = catalog.access_levels[TAccessPermissionScope.SERVER]
                self.assertTrue(len(catalog_privs) == 1)
                assert TAccessPermissionLevel.SELECT in catalog_privs

            ctx.enable_token_auth('root')
            conn.execute_ddl("drop role if exists {}".format(role))

    def test_catalog_access_levels(self):
        DB = "test_catalog_access_db"
        TBL1 = "%s.tbl1" % DB
        CRAWLER = "test_catalog_access_crawler"
        CRAWLER_DB = "_okera_crawler_%s" % CRAWLER
        CRAWLER_SRC = "s3://cerebrodata-test/empty/"

        ROLE = "test_catalog_access_role"
        USER = "test_catalog_access_user"

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                # Create the base objects
                "DROP DATABASE IF EXISTS %s CASCADE" % DB,
                "DROP DATABASE IF EXISTS %s CASCADE" % CRAWLER_DB,
                "CREATE DATABASE %s" % DB,
                "CREATE TABLE %s (col1 int)" % TBL1,
                "CREATE CRAWLER %s SOURCE '%s'" % (CRAWLER, CRAWLER_SRC),

                # Grant access to them in a variety of ways
                "DROP ROLE IF EXISTS %s" % ROLE,
                "CREATE ROLE %s" % ROLE,
                "GRANT ROLE %s TO GROUP %s" % (ROLE, USER),

                # First, grant some CATALOG-only things
                "GRANT CREATE_CRAWLER_AS_OWNER ON CATALOG TO ROLE %s" % (ROLE),
                "GRANT VIEW_AUDIT ON CATALOG TO ROLE %s" % (ROLE),

                # Grant some privileges at all data levels
                "GRANT CREATE_AS_OWNER ON CATALOG TO ROLE %s" % (ROLE),
                "GRANT CREATE ON DATABASE %s TO ROLE %s" % (DB, ROLE),
                "GRANT VIEW_COMPLETE_METADATA ON TABLE %s TO ROLE %s" % (TBL1, ROLE),
                "GRANT SELECT(col1) ON TABLE %s TO ROLE %s" % (TBL1, ROLE),

                # Grant some crawler privileges
                "GRANT DROP ON CRAWLER %s TO ROLE %s" % (CRAWLER, ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            result = conn.list_catalogs(requesting_user=USER)
            assert len(result.catalogs) == 1

            catalog = result.catalogs[0]
            access_levels = catalog.access_levels

            # Check the catalog permissions
            assert len(access_levels[TAccessPermissionScope.SERVER]) == 3
            assert TAccessPermissionLevel.CREATE_AS_OWNER in access_levels[TAccessPermissionScope.SERVER]
            assert TAccessPermissionLevel.CREATE_CRAWLER_AS_OWNER in access_levels[TAccessPermissionScope.SERVER]
            assert TAccessPermissionLevel.VIEW_AUDIT in access_levels[TAccessPermissionScope.SERVER]

            # Check the database permissions
            assert len(access_levels[TAccessPermissionScope.DATABASE]) == 5
            assert TAccessPermissionLevel.VIEW_AUDIT in access_levels[TAccessPermissionScope.DATABASE]
            assert TAccessPermissionLevel.CREATE in access_levels[TAccessPermissionScope.DATABASE]
            assert TAccessPermissionLevel.VIEW_COMPLETE_METADATA in access_levels[TAccessPermissionScope.DATABASE]
            assert TAccessPermissionLevel.SELECT in access_levels[TAccessPermissionScope.DATABASE]
            assert TAccessPermissionLevel.CREATE_AS_OWNER in access_levels[TAccessPermissionScope.DATABASE]

            # Check the crawler permissions
            assert len(access_levels[TAccessPermissionScope.CRAWLER]) == 1
            assert TAccessPermissionLevel.DROP in access_levels[TAccessPermissionScope.CRAWLER]

if __name__ == "__main__":
    unittest.main()
