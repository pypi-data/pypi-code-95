# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for role granting
#
# pylint: disable=too-many-public-methods,no-self-use

import json
import unittest

from okera import _thrift_api
from okera.tests import pycerebro_test_common as common
from okera._thrift_api import (
    TAccessPermissionLevel,
    TAccessPermissionScope,
)
from okera._util import (
    ExprUtils
)

TEST_USER = 'roles_test_user'
TEST_USER2 = 'roles_test_user2'

OKERA_PUBLIC_ROLE = 'okera_public_role'

def disable_auth(ctx, params):
    ctx.disable_auth()
    params.requesting_user = None

def enable_auth(ctx, params, user):
    ctx.enable_token_auth(token_str=user)
    params.requesting_user = user

def get_grantable_roles(conn, params):
    #pylint: disable=protected-access
    return conn._underlying_client().GetGrantableRoles(params)
    #pylint: enable=protected-access

def get_role(conn, name, ast=False):
    #pylint: disable=protected-access
    params = _thrift_api.TGetRoleParams()
    params.role_name = name
    params.return_structured_exprs = ast
    if conn.ctx._get_user():
        params.requesting_user = conn.ctx._get_user()
    return conn._underlying_client().GetRole(params)
    #pylint: enable=protected-access

def list_roles(conn, params, limit=None):
    #pylint: disable=protected-access
    if conn.ctx._get_user():
        params.requesting_user = conn.ctx._get_user()
    if limit is not None:
        params.limit = limit
    else:
        params.limit = 0
    return conn._underlying_client().ListRoles(params)
    #pylint: enable=protected-access

def contains_role(role_name, roles):
    for role in roles:
        if role.role_name == role_name:
            return True

    return False

def get_role_by_name(role_name, roles):
    for role in roles:
        if role.role_name == role_name:
            return role

    return None

# def cleanup_for_user(conn, user):
#     conn.ctx.enable_token_auth(conn)
#     roles_for_user

class RolesTest(common.TestBase):
    # NOTE: this test will likely need to change once we can properly
    # ACL roles themselves, since then we will return just a subset of
    # roles.
    def test_get_grantable_roles(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            params = _thrift_api.TGetGrantableRolesParams()

            # Set up a role and grant it to the user's group
            disable_auth(ctx, params)
            conn.execute_ddl("DROP ROLE IF EXISTS grantable_role")
            conn.execute_ddl("CREATE ROLE grantable_role")
            conn.execute_ddl("GRANT ROLE grantable_role to GROUP %s" % TEST_USER)

            # As an admin, we should always be able to see all roles
            disable_auth(ctx, params)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertTrue("grantable_role" in retrieved_roles)

            # Even though we have the test role, our user does not have
            # any roles that have a privilege with GRANT OPTION, so we
            # should not get back any roles
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # As an admin, grant a privilege with GRANT OPTION to the
            # role we created
            disable_auth(ctx, params)
            conn.execute_ddl("""
            GRANT SELECT ON TABLE okera_sample.sample
            TO ROLE grantable_role WITH GRANT OPTION""")
            admin_roles = get_grantable_roles(conn, params).roles

            # Even though there is a grant with GRANT OPTION, it's on
            # a specific table, and we specify no parameters, which is
            # equivalent to searching for grants on the CATALOG
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # Now, we will check with specific parameters
            params.database = "okera_sample"
            params.table = "sample"

            # As a user, we should now get back all the roles since we have a
            # privilege that has a GRANT OPTION that matches our scope. The set of
            # roles should be the same as what the admin got.
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

            # Now, we will check with specific parameters on a table we don't have
            params.database = "okera_sample"
            params.table = "users"

            # As a user, we should get no roles, as we don't have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # Now, we will check with specific parameters on just the DB
            params.database = "okera_sample"

            # As a user, we should get no roles, as we don't have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # As an admin, grant a privilege with GRANT OPTION to the
            # role we created
            disable_auth(ctx, params)
            conn.execute_ddl("""
            GRANT SELECT ON DATABASE okera_sample
            TO ROLE grantable_role WITH GRANT OPTION""")

            # As a user, we should now get all roles, as we have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

            # Now, we will check with specific parameters on just the DB,
            # with a different DB
            params.database = "okera_system"

            # As a user, we should get no roles, as we don't have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # Finally, let's add a grant to the CATALOG and then
            # a query with no parameters will work
            disable_auth(ctx, params)
            conn.execute_ddl("""
            GRANT SELECT ON SERVER
            TO ROLE grantable_role WITH GRANT OPTION""")

            # Now, we will check with no parameters
            params.database = ""
            params.table = ""

            # As a user, we should get all the roles, we have GRANT OPTION
            # at the CATALOG level
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

            # Additionally, even if we query on a specific DB (or even table),
            # we will now always get roles because our CATALOG level grant
            # allows us to see them.
            params.database = "okera_system"

            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

    def test_drop_privilege(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            obj_name = "drop_privilege_obj"
            role_name = "drop_privilege_role"

            # TODO: when we add ACLs on roles, should add a test here
            ddls = [
                # Setup role
                "DROP ROLE IF EXISTS %s" % (role_name),
                "CREATE ROLE %s" % (role_name),
                "GRANT ROLE %s TO GROUP %s" % (role_name, TEST_USER),

                # DB
                "DROP DATABASE IF EXISTS %s CASCADE" % (obj_name),
                "CREATE DATABASE %s" % (obj_name),
                "GRANT DROP ON DATABASE %s TO ROLE %s" % (obj_name, role_name),

                # Table
                "CREATE TABLE %s.%s (c1 string)" % (obj_name, obj_name),
                "GRANT DROP ON TABLE %s.%s TO ROLE %s" % (obj_name, obj_name, role_name),

                # View
                "CREATE VIEW %s.%s AS SELECT 1" % (obj_name, obj_name+"view"),
                "GRANT DROP ON TABLE %s.%s TO ROLE %s" % (obj_name,
                                                          obj_name+"view", role_name),

                # Attribute Namespace
                "DROP ATTRIBUTE IF EXISTS %s.%s" % (obj_name, obj_name),
                "CREATE ATTRIBUTE %s.%s" % (obj_name, obj_name),
                "GRANT DROP ON ATTRIBUTE NAMESPACE %s TO ROLE %s" % (obj_name, role_name),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # Switch to the user
            ctx.enable_token_auth(token_str=TEST_USER)

            # Verify we can drop everything (we do it in reverse order from the DDLs
            # to ensure we can drop the DB at the end, as it needs to be empty)
            drop_ddls = [
                "DROP ATTRIBUTE %s.%s" % (obj_name, obj_name),
                "DROP VIEW %s.%s" % (obj_name, obj_name+"view"),
                "DROP TABLE %s.%s" % (obj_name, obj_name),
                "DROP DATABASE %s" % (obj_name),
            ]

            for drop_ddl in drop_ddls:
                conn.execute_ddl(drop_ddl)

    def test_role_priv_drop(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_role"
            obj_role = "role_priv_test_role"

            for obj in ['CATALOG', 'ROLE %s' % obj_role]:
                for (priv, succeed) in [('DROP', True), ('ALL', True), ('MANAGE_GROUPS', False)]:
                    ctx.disable_auth()
                    setup_ddls = [
                        # Setup steward role
                        "DROP ROLE IF EXISTS %s" % (steward_role),
                        "CREATE ROLE %s" % (steward_role),
                        "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                        # Setup object role
                        "DROP ROLE IF EXISTS %s" % (obj_role),
                        "CREATE ROLE %s" % (obj_role),

                        # Grant specific privilege on specified object to the
                        # steward role
                        "GRANT %s ON %s TO ROLE %s" % (priv, obj, steward_role),
                    ]

                    for ddl in setup_ddls:
                        conn.execute_ddl(ddl)

                    # Switch to the user
                    ctx.enable_token_auth(token_str=TEST_USER)

                    # Verify we can drop the role
                    print("Trying to DROP ROLE with GRANT %s ON %s - should %s" % (
                        priv, obj, 'succeed' if succeed else 'fail'))

                    if succeed:
                        conn.execute_ddl('DROP ROLE %s' % obj_role)
                    else:
                        with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                            conn.execute_ddl('DROP ROLE %s' % obj_role)
                        self.assertTrue('to DROP this role' in str(ex_ctx.exception))

    def test_role_priv_create(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_role"
            obj_role = "role_priv_test_role"
            as_owner_role = "_okera_internal_role_%s" % (TEST_USER)

            # (privilege, should succeed, as_owner semantics)
            combinations = [
                ('ALL', True, False),
                ('CREATE_ROLE_AS_OWNER', True, True),
                ('CREATE', False, False),
            ]

            for obj in ['CATALOG']:
                for (priv, succeed, as_owner) in combinations:
                    ctx.disable_auth()
                    setup_ddls = [
                        # Setup steward role
                        "DROP ROLE IF EXISTS %s" % (steward_role),
                        "CREATE ROLE %s" % (steward_role),
                        "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                        # Cleanup the object role
                        "DROP ROLE IF EXISTS %s" % (obj_role),

                        # Cleanup the special per-user role to start from a clean slate
                        "DROP ROLE IF EXISTS %s" % (as_owner_role),

                        # Grant specific privilege on specified object to the
                        # steward role
                        "GRANT %s ON %s TO ROLE %s" % (priv, obj, steward_role),
                    ]

                    for ddl in setup_ddls:
                        conn.execute_ddl(ddl)

                    # Switch to the user
                    ctx.enable_token_auth(token_str=TEST_USER)

                    # Verify we can drop the role
                    print("Trying to CREATE ROLE with GRANT %s ON %s - should %s" % (
                        priv, obj, 'succeed' if succeed else 'fail'))

                    if succeed:
                        conn.execute_ddl('CREATE ROLE %s' % obj_role)
                    else:
                        with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                            conn.execute_ddl('CREATE ROLE %s' % obj_role)
                        self.assertTrue('to CREATE this role' in str(ex_ctx.exception))

                    if as_owner:
                        role_grants = conn.execute_ddl('SHOW GRANT ROLE %s' % as_owner_role)
                        print(role_grants)
                        assert len(role_grants) == 1
                        assert role_grants[0][0] == 'role'
                        assert role_grants[0][6] == obj_role
                        assert role_grants[0][9] == 'all'
                        assert role_grants[0][13] == 'false'
                    else:
                        with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                            conn.execute_ddl('SHOW GRANT ROLE %s' % as_owner_role)
                        self.assertTrue('does not exist' in str(ex_ctx.exception))

    def test_role_priv_manage_groups(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_role"
            obj_role = "role_priv_test_role"

            for obj in ['CATALOG', 'ROLE %s' % obj_role]:
                for (priv, succeed) in [('MANAGE_GROUPS', True), ('ALL', True), ('DROP', False)]:
                    ctx.disable_auth()
                    setup_ddls = [
                        # Setup steward role
                        "DROP ROLE IF EXISTS %s" % (steward_role),
                        "CREATE ROLE %s" % (steward_role),
                        "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                        # Setup object role
                        "DROP ROLE IF EXISTS %s" % (obj_role),
                        "CREATE ROLE %s" % (obj_role),

                        # Grant specific privilege on specified object to the
                        # steward role
                        "GRANT %s ON %s TO ROLE %s" % (priv, obj, steward_role),
                    ]

                    for ddl in setup_ddls:
                        conn.execute_ddl(ddl)

                    # Switch to the user
                    ctx.enable_token_auth(token_str=TEST_USER)

                    # Verify we can grant the role to a group
                    print("Trying to GRANT ROLE TO GROUP with GRANT %s ON %s - should %s" % (
                        priv, obj, 'succeed' if succeed else 'fail'))

                    if succeed:
                        conn.execute_ddl('GRANT ROLE %s TO GROUP some_group' % obj_role)
                    else:
                        with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                            conn.execute_ddl('GRANT ROLE %s TO GROUP some_group' % obj_role)
                        self.assertTrue('GRANT/REVOKE this role to groups.' in str(ex_ctx.exception))

                    # Verify we can revoke the role from a group
                    print("Trying to REVOKE ROLE FROM GROUP with GRANT %s ON %s - should %s" % (
                        priv, obj, 'succeed' if succeed else 'fail'))

                    if succeed:
                        conn.execute_ddl('REVOKE ROLE %s FROM GROUP some_group' % obj_role)
                    else:
                        with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                            conn.execute_ddl('REVOKE ROLE %s FROM GROUP some_group' % obj_role)
                        self.assertTrue('GRANT/REVOKE this role to groups.' in str(ex_ctx.exception))

    def test_role_priv_manage_permissions(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_role"
            obj_role = "role_priv_test_role"
            test_db = "role_priv_manage_permissions_db"

            for obj in ['CATALOG', 'ROLE %s' % obj_role]:
                for (priv, succeed) in [('MANAGE_PERMISSIONS', True), ('ALL', True), ('MANAGE_GROUPS', False)]:
                    ctx.disable_auth()
                    setup_ddls = [
                        # Setup DB
                        "DROP DATABASE IF EXISTS %s CASCADE" % (test_db),
                        "CREATE DATABASE %s" % (test_db),

                        # Setup steward role
                        "DROP ROLE IF EXISTS %s" % (steward_role),
                        "CREATE ROLE %s" % (steward_role),
                        "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                        # Setup object role
                        "DROP ROLE IF EXISTS %s" % (obj_role),
                        "CREATE ROLE %s" % (obj_role),

                        # Grant specific privilege on specified object to the
                        # steward role
                        "GRANT %s ON %s TO ROLE %s" % (priv, obj, steward_role),
                        "GRANT SELECT ON DATABASE %s TO ROLE %s WITH GRANT OPTION" % (test_db, steward_role),
                    ]

                    for ddl in setup_ddls:
                        conn.execute_ddl(ddl)

                    # Switch to the user
                    ctx.enable_token_auth(token_str=TEST_USER)

                    # Verify we can grant the role to a group
                    print("Trying to 'GRANT SELECT TO ROLE' with GRANT %s ON %s - should %s" % (
                        priv, obj, 'succeed' if succeed else 'fail'))

                    if succeed:
                        conn.execute_ddl('GRANT SELECT ON DATABASE %s TO ROLE %s' % (test_db, obj_role))
                    else:
                        with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                            conn.execute_ddl('GRANT SELECT ON DATABASE %s TO ROLE %s' % (test_db, obj_role))
                        self.assertTrue('not have privileges to GRANT' in str(ex_ctx.exception))

                    # Verify we can revoke the database from the role group
                    print("Trying to 'REVOKE SELECT FROM ROLE' with GRANT %s ON %s - should %s" % (
                        priv, obj, 'succeed' if succeed else 'fail'))

                    if succeed:
                        conn.execute_ddl('REVOKE SELECT ON DATABASE %s FROM ROLE %s' % (test_db, obj_role))
                    else:
                        with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                            conn.execute_ddl('REVOKE SELECT ON DATABASE %s FROM ROLE %s' % (test_db, obj_role))
                        self.assertTrue('not have privileges to REVOKE' in str(ex_ctx.exception))

    def test_role_priv_show_roles(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_role"
            obj_role1 = "role_priv_test_role1"
            obj_role2 = "role_priv_test_role2"
            obj_role3 = "role_priv_test_role3"
            obj_role4 = "role_priv_test_role4"

            for level in ['SHOW', 'MANAGE_GROUPS']:
                setup_ddls = [
                    "DROP ROLE IF EXISTS grantable_role",

                    # Setup steward role
                    "DROP ROLE IF EXISTS %s" % (steward_role),
                    "CREATE ROLE %s" % (steward_role),
                    "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                    # Setup object roles
                    "DROP ROLE IF EXISTS %s" % (obj_role1),
                    "CREATE ROLE %s" % (obj_role1),
                    "DROP ROLE IF EXISTS %s" % (obj_role2),
                    "CREATE ROLE %s" % (obj_role2),
                    "DROP ROLE IF EXISTS %s" % (obj_role3),
                    "CREATE ROLE %s" % (obj_role3),
                    "DROP ROLE IF EXISTS %s" % (obj_role4),
                    "CREATE ROLE %s" % (obj_role4),

                    # Grant the last role to us explicitly
                    "GRANT ROLE %s TO GROUP %s" % (obj_role4, TEST_USER),

                    # Grant specific privilege on specified object to the
                    # steward role
                    "GRANT %s ON ROLE %s TO ROLE %s" % (level, obj_role1, steward_role),
                    "GRANT %s ON ROLE %s TO ROLE %s" % (level, obj_role2, steward_role),
                ]

                for ddl in setup_ddls:
                    conn.execute_ddl(ddl)

                print("Running SHOW ROLES tests for access level: %s" % (level))

                # Switch to the user who has the roles
                ctx.enable_token_auth(token_str=TEST_USER)

                # SHOW ROLES should show us all the roles we have access to.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLES')]
                assert steward_role in show_roles
                assert obj_role1 in show_roles
                assert obj_role2 in show_roles
                assert obj_role3 not in show_roles
                assert obj_role4 in show_roles

                # SHOW CURRENT ROLES should show us all the roles we have.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW CURRENT ROLES')]
                assert steward_role in show_roles
                assert obj_role1 not in show_roles
                assert obj_role2 not in show_roles
                assert obj_role3 not in show_roles
                assert obj_role4 in show_roles

                # SHOW ROLE GRANT GROUP should show us all the group has, but since
                # it's our user group, this is equivalent to `SHOW CURRENT ROLES`
                show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLE GRANT GROUP %s' % TEST_USER)]
                assert steward_role in show_roles
                assert obj_role1 not in show_roles
                assert obj_role2 not in show_roles
                assert obj_role3 not in show_roles
                assert obj_role4 in show_roles

                # SHOW ALL ROLES is only accessible to admins.
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    show_roles = conn.execute_ddl('SHOW ALL ROLES')
                self.assertTrue("'roles_test_user' is not an admin" in str(ex_ctx.exception))

                # SHOW ROLE GRANT GROUP on a group the user is not in is
                # only accessible to admins.
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    show_roles = conn.execute_ddl('SHOW ROLE GRANT GROUP %s' % TEST_USER2)
                self.assertTrue("'roles_test_user' is not an admin" in str(ex_ctx.exception))

                # Switch to the other user who has no roles
                ctx.enable_token_auth(token_str=TEST_USER2)

                # SHOW ROLES should show us all the roles we have access to.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLES')]
                assert steward_role not in show_roles
                assert obj_role1 not in show_roles
                assert obj_role2 not in show_roles
                assert obj_role3 not in show_roles
                assert obj_role4 not in show_roles

                # SHOW CURRENT ROLES should show us all the roles we have.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW CURRENT ROLES')]
                assert steward_role not in show_roles
                assert obj_role1 not in show_roles
                assert obj_role2 not in show_roles
                assert obj_role3 not in show_roles
                assert obj_role4 not in show_roles

                # SHOW ROLE GRANT GROUP should show us all the group has, but since
                # it's our user group, this is equivalent to `SHOW CURRENT ROLES`
                show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLE GRANT GROUP %s' % TEST_USER2)]
                assert steward_role not in show_roles
                assert obj_role1 not in show_roles
                assert obj_role2 not in show_roles
                assert obj_role3 not in show_roles
                assert obj_role4 not in show_roles

                # SHOW ALL ROLES is only accessible to admins.
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    show_roles = conn.execute_ddl('SHOW ALL ROLES')
                self.assertTrue("'roles_test_user2' is not an admin" in str(ex_ctx.exception))

                # SHOW ROLE GRANT GROUP on a group the user is not in is
                # only accessible to admins.
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    show_roles = conn.execute_ddl('SHOW ROLE GRANT GROUP %s' % TEST_USER)
                self.assertTrue("'roles_test_user2' is not an admin" in str(ex_ctx.exception))

                # Switch to admin user
                ctx.disable_auth()

                # SHOW ROLES should show us all the roles we have access to.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLES')]
                assert steward_role in show_roles
                assert obj_role1 in show_roles
                assert obj_role2 in show_roles
                assert obj_role3 in show_roles
                assert obj_role4 in show_roles

                # SHOW CURRENT ROLES should show us all the roles we have.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW CURRENT ROLES')]
                assert steward_role not in show_roles
                assert obj_role1 not in show_roles
                assert obj_role2 not in show_roles
                assert obj_role3 not in show_roles
                assert obj_role4 not in show_roles
                assert 'admin_role' in show_roles

                # SHOW ALL ROLES is only accessible to admins.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW ALL ROLES')]
                assert steward_role in show_roles
                assert obj_role1 in show_roles
                assert obj_role2 in show_roles
                assert obj_role3 in show_roles
                assert obj_role4 in show_roles

                # SHOW ROLE GRANT GROUP on a group the user is not in is
                # only accessible to admins.
                show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLE GRANT GROUP %s' % TEST_USER)]
                assert steward_role in show_roles
                assert obj_role4 in show_roles

    def test_role_priv_show_roles_grant_option(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_role"
            obj_role1 = "role_priv_test_role1"
            obj_role2 = "role_priv_test_role2"

            setup_ddls = [
                "DROP ROLE IF EXISTS grantable_role",

                # Setup steward role
                "DROP ROLE IF EXISTS %s" % (steward_role),
                "CREATE ROLE %s" % (steward_role),
                "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                # Setup object roles
                "DROP ROLE IF EXISTS %s" % (obj_role1),
                "CREATE ROLE %s" % (obj_role1),
                "DROP ROLE IF EXISTS %s" % (obj_role2),
                "CREATE ROLE %s" % (obj_role2),

                # Grant specific privilege on specified object to the
                # steward role
                "GRANT SELECT ON TABLE okera_sample.sample TO ROLE %s WITH GRANT OPTION" % (steward_role),
                "GRANT MANAGE_GROUPS ON ROLE %s TO ROLE %s" % (obj_role1, steward_role),
            ]

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            print("Running SHOW ROLES tests WITH GRANT OPTION")

            # Switch to the user who has the roles
            ctx.enable_token_auth(token_str=TEST_USER)

            # SHOW ROLES should show us all the roles we have access to.
            show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLES')]
            assert steward_role in show_roles
            assert obj_role1 in show_roles
            assert obj_role2 not in show_roles

            # SHOW ALL ROLES is only accessible to admins or if you had
            # WITH GRANT OPTION
            show_roles = [x[0] for x in conn.execute_ddl('SHOW ALL ROLES')]
            assert steward_role in show_roles
            assert obj_role1 in show_roles
            assert obj_role2 not in show_roles

            # SHOW ROLE GRANT GROUP is only accessible to admins or if you had
            # WITH GRANT OPTION
            show_roles = [x[0] for x in conn.execute_ddl('SHOW ROLE GRANT GROUP %s' % TEST_USER2)]
            assert steward_role not in show_roles
            assert obj_role1 not in show_roles
            assert obj_role2 not in show_roles

    def test_role_priv_show_grant_role(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_role"
            obj_role1 = "role_priv_test_role1"
            obj_role2 = "role_priv_test_role2"
            obj_role3 = "role_priv_test_role3"
            obj_role4 = "role_priv_test_role4"

            for level in ['SHOW', 'MANAGE_GROUPS']:
                setup_ddls = [
                    # Setup steward role
                    "DROP ROLE IF EXISTS %s" % (steward_role),
                    "CREATE ROLE %s" % (steward_role),
                    "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                    # Setup object roles
                    "DROP ROLE IF EXISTS %s" % (obj_role1),
                    "CREATE ROLE %s" % (obj_role1),
                    "DROP ROLE IF EXISTS %s" % (obj_role2),
                    "CREATE ROLE %s" % (obj_role2),
                    "DROP ROLE IF EXISTS %s" % (obj_role3),
                    "CREATE ROLE %s" % (obj_role3),
                    "DROP ROLE IF EXISTS %s" % (obj_role4),
                    "CREATE ROLE %s" % (obj_role4),

                    # Grant the last role to us explicitly
                    "GRANT ROLE %s TO GROUP %s" % (obj_role4, TEST_USER),

                    # Grant specific privilege on specified object to the
                    # steward role
                    "GRANT %s ON ROLE %s TO ROLE %s" % (level, obj_role1, steward_role),
                    "GRANT %s ON ROLE %s TO ROLE %s" % (level, obj_role2, steward_role),
                ]

                for ddl in setup_ddls:
                    conn.execute_ddl(ddl)

                print("Running SHOW GRANT ROLE tests for access level: %s" % (level))

                # Switch to the user who has the roles
                ctx.enable_token_auth(token_str=TEST_USER)

                conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role1)

                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role3)
                self.assertTrue("'roles_test_user' is not an admin" in str(ex_ctx.exception))

                conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role4)

                # Switch to the other user who has no roles
                ctx.enable_token_auth(token_str=TEST_USER2)

                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role1)
                self.assertTrue("'roles_test_user2' is not an admin" in str(ex_ctx.exception))

                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role3)
                self.assertTrue("'roles_test_user2' is not an admin" in str(ex_ctx.exception))

                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role4)
                self.assertTrue("'roles_test_user2' is not an admin" in str(ex_ctx.exception))

                # Switch to admin user
                ctx.disable_auth()

                conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role1)
                conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role3)
                conn.execute_ddl('SHOW GRANT ROLE %s' % obj_role4)

    def test_get_role(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            test_attr_ns = "get_role_ns"
            test_attr = "%s.get_role_attr" % (test_attr_ns)
            test_role1 = "get_role_test_role"
            test_role2 = "get_role_test_role2"

            setup_ddls = [
                # Create an attribute
                "DROP ATTRIBUTE IF EXISTS %s" % (test_attr),
                "CREATE ATTRIBUTE %s" % (test_attr),

                # Setup role 1
                "DROP ROLE IF EXISTS %s" % (test_role1),
                "CREATE ROLE %s" % (test_role1),
                "GRANT ROLE %s TO GROUP %s" % (test_role1, TEST_USER),

                # Add grants of various kinds to ensure they get
                # serialized correctly
                "GRANT VIEW_AUDIT ON SERVER TO ROLE %s" % (test_role1),
                "GRANT ALTER ON DATABASE okera_sample TO ROLE %s" % (test_role1),
                "GRANT SHOW ON TABLE okera_sample.sample TO ROLE %s" % (test_role1),
                "GRANT SELECT(record) ON TABLE okera_sample.sample TO ROLE %s" % (test_role1),
                "GRANT ALL ON ATTRIBUTE NAMESPACE %s TO ROLE %s" % (test_attr_ns, test_role1),
                "GRANT MANAGE_GROUPS ON ROLE okera_public_role TO ROLE %s" % (test_role1),
                "GRANT ALL ON CRAWLER foobar TO ROLE %s" % (test_role1),
                """GRANT SELECT ON DATABASE okera_sample
                   HAVING ATTRIBUTE IN (%s)
                   TRANSFORM %s WITH mask()
                   WHERE record = 'abc'
                   TO ROLE %s""" % (test_attr, test_attr, test_role1),

                # Setup role 2, don't grant to user
                "DROP ROLE IF EXISTS %s" % (test_role2),
                "CREATE ROLE %s" % (test_role2),
            ]

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            # As admin, ensure we have access to the two roles we created
            role1 = get_role(conn, test_role1).role
            assert role1 is not None
            assert len(role1.privileges) == 8
            # Admin has 'ALL' access on any role so access_level should contain 'ALL'
            assert TAccessPermissionLevel.ALL in role1.access_levels

            role2 = get_role(conn, test_role2).role
            assert role2 is not None
            assert len(role2.privileges) == 0
            # Admin has 'ALL' access on any role so access_level should contain 'ALL'
            assert TAccessPermissionLevel.ALL in role1.access_levels

            # Switch to the user who has the roles
            ctx.enable_token_auth(token_str=TEST_USER)

            expected_privileges = [
                (TAccessPermissionScope.DATABASE, TAccessPermissionLevel.ALTER, 'okera_sample', '', '', None, None, None),
                (TAccessPermissionScope.TABLE, TAccessPermissionLevel.SHOW, 'okera_sample', 'sample', '', None, None, None),
                (TAccessPermissionScope.SERVER, TAccessPermissionLevel.VIEW_AUDIT, '', '', '', None, None, None),
                (TAccessPermissionScope.CRAWLER, TAccessPermissionLevel.ALL, None, None, None, 'foobar', None, None),
                (TAccessPermissionScope.COLUMN, TAccessPermissionLevel.SELECT, 'okera_sample', 'sample', 'record', None, None, None),
                (TAccessPermissionScope.ROLE, TAccessPermissionLevel.MANAGE_GROUPS, '', '', '', None, 'okera_public_role', None),
                (TAccessPermissionScope.ATTRIBUTE_NAMESPACE, TAccessPermissionLevel.ALL, '', '', '', None, None, test_attr_ns),
                (TAccessPermissionScope.DATABASE, TAccessPermissionLevel.SELECT, 'okera_sample', None, None, None, None, None),
            ]

            role1 = get_role(conn, test_role1).role
            assert role1 is not None
            assert len(role1.privileges) == 8
            # TEST_USER would not have any access on it's own role unless specified explicitly
            # access_levels should be an empty list.
            assert not role1.access_levels

            role2 = get_role(conn, "okera_public_role").role
            assert role2 is not None
            # TEST_USER has 'MANAGE_GROUPS' privilege on 'okera_public_role'
            assert TAccessPermissionLevel.MANAGE_GROUPS in role2.access_levels

            found_abac_priv = False
            for priv in role1.privileges:
                priv_tuple = (
                    priv.scope, priv.privilege_level, priv.db_name,
                    priv.table_name, priv.column_name, priv.crawler,
                    priv.role, priv.attribute_namespace)
                assert priv_tuple in expected_privileges

                if priv.transform_expression:
                    found_abac_priv = True
                    assert test_attr_ns in priv.transform_expression
                    assert test_attr_ns in priv.attribute_expression
                    assert 'record' in priv.filter
            assert found_abac_priv

            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                get_role(conn, test_role2)
            self.assertTrue("Role 'get_role_test_role2' does not exist" in str(ex_ctx.exception))

    def _verify_structured_exprs(self, roles):
        for r in roles:
            for p in r.privileges:
                if p.transform_expression:
                    self.assertTrue(p.transform_expressions is not None, msg=str(p))
                    for t in p.transform_expressions:
                        e = ExprUtils.convert_expr_ast_to_json(t.expr)
                        f = ExprUtils.convert_expr_ast_to_json(t.fn)
                        print(json.dumps(e, indent=2))
                        print(json.dumps(f, indent=2))
                if p.attribute_expression:
                    self.assertTrue(p.attribute_expression_tree is not None, msg=str(p))
                    tree = ExprUtils.convert_expr_ast_to_json(p.attribute_expression_tree)
                    print(json.dumps(tree, indent=2))
                if p.filter:
                    self.assertTrue(p.filter_expression_tree is not None, msg=str(p))
                    tree = ExprUtils.convert_expr_ast_to_json(p.filter_expression_tree)
                    print(json.dumps(tree, indent=2))

    def test_list_roles_non_paginated(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "list_roles_steward_role"
            test_attr_ns = "get_role_ns"
            test_attr = "%s.get_role_attr" % (test_attr_ns)
            test_role = "list_roles_role1"
            test_role2 = "manageable_test_role"
            test_role3 = "manage_groups_test_role"
            test_group = "list_roles_group1"
            test_db = "list_roles_db1"
            test_tbl = "list_roles_tbl1"

            setup_ddls = [
                # Create an attribute
                "DROP ATTRIBUTE IF EXISTS %s" % (test_attr),
                "CREATE ATTRIBUTE %s" % (test_attr),

                # Setup DBs
                "DROP DATABASE IF EXISTS %s CASCADE" % (test_db),
                "CREATE DATABASE %s" % (test_db),
                "CREATE TABLE %s.%s (c1 int)" % (test_db, test_tbl),

                # Setup role
                "DROP ROLE IF EXISTS %s" % (test_role),
                "CREATE ROLE %s" % (test_role),
                "DROP ROLE IF EXISTS %s" % (test_role2),
                "CREATE ROLE %s" % (test_role2),
                "DROP ROLE IF EXISTS %s" % (test_role3),
                "CREATE ROLE %s" % (test_role3),
                """GRANT SELECT ON TABLE %s.%s
                   HAVING ATTRIBUTE IN (%s)
                   TO ROLE %s""" % (test_db, test_tbl, test_attr, test_role),
                "GRANT ROLE %s TO GROUP %s" % (test_role, test_group),

                "DROP ROLE IF EXISTS %s" % (steward_role),
                "CREATE ROLE %s" % (steward_role),
                "GRANT ALL ON ROLE %s TO ROLE %s" % (test_role, steward_role),
                "GRANT SHOW ON ROLE %s TO ROLE %s" % (test_role2, steward_role),
                "GRANT MANAGE_GROUPS ON ROLE %s TO ROLE %s" % (test_role3, steward_role),
                "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),
            ]

            ctx.disable_auth()

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            for (user, has_access) in [(None, True), (TEST_USER, True), (TEST_USER2, False)]:
                if user:
                    print("Running list_roles tests with user: %s" % user)
                    ctx.enable_token_auth(token_str=user)
                else:
                    print("Running list_roles tests as admin")
                    ctx.disable_auth()

                # All roles
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                roles = list_roles(conn, params).roles
                if has_access:
                    assert contains_role(test_role, roles)
                else:
                    assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                # Roles with name substring match
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.role_name_substring = test_role[1:-1]
                roles = list_roles(conn, params).roles
                if has_access:
                    assert len(roles) == 1
                    assert contains_role(test_role, roles)
                else:
                    assert len(roles) == 0
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.role_name_substring = test_role[1:-1] + "not_exist"
                roles = list_roles(conn, params).roles
                assert len(roles) == 0
                self._verify_structured_exprs(roles)

                # Roles with group substring match
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.group_name_substring = test_group[1:-1]
                roles = list_roles(conn, params).roles
                if has_access:
                    assert len(roles) == 1
                    assert contains_role(test_role, roles)
                else:
                    assert len(roles) == 0
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.group_name_substring = test_group[1:-1] + "not_exist"
                roles = list_roles(conn, params).roles
                assert len(roles) == 0
                self._verify_structured_exprs(roles)

                # Roles with target user
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.target_user = test_group
                roles = list_roles(conn, params).roles
                if has_access:
                    assert contains_role(test_role, roles)
                else:
                    assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.target_user = test_group + "not_exist"
                roles = list_roles(conn, params).roles
                assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                # Roles with catalog object filter
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.catalog_object_names = ["%s.%s" % (test_db, test_tbl)]
                roles = list_roles(conn, params).roles
                if has_access:
                    assert contains_role(test_role, roles)
                else:
                    assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.catalog_object_names = ["%s.%s_not_exist" % (test_db, test_tbl)]
                roles = list_roles(conn, params).roles
                assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.catalog_object_names = ["%s" % (test_db)]
                roles = list_roles(conn, params).roles
                if has_access:
                    assert contains_role(test_role, roles)
                else:
                    assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.catalog_object_names = ["%s_not_exist" % (test_db)]
                roles = list_roles(conn, params).roles
                assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    params = _thrift_api.TListRolesParams()
                    params.catalog_object_names = ["db1", "db2"]
                    list_roles(conn, params).roles
                self.assertTrue("More than one catalog object filter is not supported" in str(ex_ctx.exception))

                # Roles with scope filter
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.scopes = [TAccessPermissionScope.TABLE]
                roles = list_roles(conn, params).roles
                if has_access:
                    assert contains_role(test_role, roles)
                else:
                    assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.scopes = [TAccessPermissionScope.DATABASE]
                roles = list_roles(conn, params).roles
                assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.scopes = [TAccessPermissionScope.DATABASE, TAccessPermissionScope.TABLE]
                roles = list_roles(conn, params).roles
                if has_access:
                    assert contains_role(test_role, roles)
                else:
                    assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                # Check scope filter + catalog object filter is not allowed
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    params = _thrift_api.TListRolesParams()
                    params.catalog_object_names = ["db1", "db2"]
                    params.scopes = [TAccessPermissionScope.DATABASE]
                    list_roles(conn, params).roles
                self.assertTrue("both an access scope filter and a catalog object filter" in str(ex_ctx.exception))

                # Check manageableOnly filter
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.manageable_only = True

                roles = list_roles(conn, params).roles
                if has_access:
                    if user:
                        # Steward should only be able to see roles
                        # that they have privilege on, ie its own roles
                        # should be filtered out
                        assert not contains_role(steward_role, roles)
                    assert contains_role(test_role, roles)
                else:
                    assert not contains_role(test_role, roles)
                self._verify_structured_exprs(roles)

                # Check levels filter
                # This filter works with effective permissions, ie
                # ALL will always be added to the specified level, since
                # ALL implies all other levels.
                params = _thrift_api.TListRolesParams()
                params.return_structured_exprs = True
                params.levels = [TAccessPermissionLevel.MANAGE_GROUPS]

                roles = list_roles(conn, params).roles
                if has_access:
                    # both steward and admin should see the role with MANAGE_GRANTS
                    assert contains_role(test_role3, roles)
                    if user:
                        # steward should not see the role with SHOW
                        assert not contains_role(test_role2, roles)
                else:
                    assert not contains_role(test_role2, roles)
                    assert not contains_role(test_role3, roles)
                self._verify_structured_exprs(roles)

    def test_list_roles_paginated(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "list_roles_steward_role"

            setup_ddls = [
                "DROP ROLE IF EXISTS %s" % (steward_role),
                "CREATE ROLE %s" % (steward_role),
                "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER)
            ]

            expected_order = []

            for idx in range(9):
                role_name = "list_roles_paginated_role_%s" % idx
                setup_ddls += [
                    "DROP ROLE IF EXISTS %s" % (role_name),
                    "CREATE ROLE %s" % (role_name),
                    "GRANT ALL ON ROLE %s TO ROLE %s" % (role_name, steward_role)
                ]

                expected_order.append(role_name)

            ctx.disable_auth()

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            ctx.enable_token_auth(token_str=TEST_USER)

            # Paginate filtered roles
            prev_tokens = []

            params = _thrift_api.TListRolesParams()
            params.role_name_substring = "roles_paginated_role"
            idx = 0
            while True:
                res = list_roles(conn, params, limit=2)
                assert len(res.roles) <= 2
                assert res.total_count == 9

                # For every non-None prev token, we will record
                # it so we can walk it backwards and ensure it works.
                if res.prev_page_token is not None:
                    prev_tokens.append(res.prev_page_token)

                for role in res.roles:
                    assert role.role_name == expected_order[idx]
                    idx += 1


                if res.next_page_token:
                    params.page_token = res.next_page_token
                else:
                    break

            # Iterate over the prev tokens to ensure we get back
            # the same values.
            idx = 0
            for prev_token in prev_tokens:
                params.page_token = prev_token
                res = list_roles(conn, params, limit=2)
                assert len(res.roles) == 2
                assert res.total_count == 9
                for role in res.roles:
                    assert role.role_name == expected_order[idx]
                    idx += 1

    def test_list_roles_access_levels(self):
        ROLE1 = "test_list_roles_access_levels_role1"
        USER1 = "test_list_roles_access_levels_user1"

        ROLE2 = "test_list_roles_access_levels_role2"
        USER2 = "test_list_roles_access_levels_user2"

        ROLE3 = "test_list_roles_access_levels_role3"
        USER3 = "test_list_roles_access_levels_user3"

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:

            ddls = [
                "DROP ROLE IF EXISTS %s" % (ROLE1),
                "CREATE ROLE %s" % (ROLE1),
                "GRANT ROLE %s TO GROUP %s" % (ROLE1, USER1),

                "DROP ROLE IF EXISTS %s" % (ROLE2),
                "CREATE ROLE %s" % (ROLE2),
                "GRANT ROLE %s TO GROUP %s" % (ROLE2, USER2),

                "DROP ROLE IF EXISTS %s" % (ROLE3),
                "CREATE ROLE %s" % (ROLE3),
                "GRANT ROLE %s TO GROUP %s" % (ROLE3, USER3),

                # Grant privileges to ROLE1 on ROLE2
                "GRANT ALL ON ROLE %s TO ROLE %s" % (ROLE2, ROLE1),
                "GRANT SHOW ON ROLE %s TO ROLE %s" % (ROLE2, ROLE1),
                "GRANT DROP ON ROLE %s TO ROLE %s" % (ROLE2, ROLE1),
                "GRANT ALTER ON ROLE %s TO ROLE %s" % (ROLE2, ROLE1),
                "GRANT MANAGE_GROUPS ON ROLE %s TO ROLE %s" % (ROLE2, ROLE1),

                # Grant privileges to ROLE1 on ROLE2
                "GRANT SHOW ON ROLE %s TO ROLE %s" % (ROLE1, ROLE2),
                "GRANT DROP ON ROLE %s TO ROLE %s" % (ROLE1, ROLE2),

                # No privileges for ROLE3
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            # -------- list roles for admin  -----------
            print("Running access_levels test : list_roles for %s" % ('admin'))
            # If authorization is disabled or if user is an admin or if it's an internal
            # request, the user will always have 'ALL' permission on any role
            ctx.disable_auth()

            params = _thrift_api.TListRolesParams()
            roles = list_roles(conn, params).roles

            # admin would have access to all the roles. we are verifying just below four.
            assert contains_role(OKERA_PUBLIC_ROLE, roles)
            assert contains_role(ROLE1, roles)
            assert contains_role(ROLE2, roles)
            assert contains_role(ROLE3, roles)

            for role in roles:
                if role.role_name in [ROLE1, ROLE2, ROLE3, OKERA_PUBLIC_ROLE]:
                    assert TAccessPermissionLevel.ALL in role.access_levels

            # -------- list roles for USER1 -----------
            print("Running access_levels test : list_roles for %s" % (USER1))
            ctx.enable_token_auth(token_str=USER1)

            params = _thrift_api.TListRolesParams()
            roles = list_roles(conn, params).roles

            assert contains_role(OKERA_PUBLIC_ROLE, roles)
            assert contains_role(ROLE1, roles)
            assert contains_role(ROLE2, roles)
            assert not contains_role(ROLE3, roles)

            for role in roles:
                if role.role_name == OKERA_PUBLIC_ROLE:
                    # USER1 does not have any explicit access on OKERA_PUBLIC_ROLE
                    # access_levels should be an empty list
                    assert not role.access_levels
                if role.role_name == ROLE1:
                    # USER1 would not have any access on it's own role unless specified explicitly
                    # access_levels should be an empty list
                    assert not role.access_levels
                if role.role_name == ROLE2:
                    # privileges that USER1 has on ROLE2
                    assert TAccessPermissionLevel.ALL in role.access_levels
                    assert TAccessPermissionLevel.SHOW in role.access_levels
                    assert TAccessPermissionLevel.DROP in role.access_levels
                    assert TAccessPermissionLevel.ALTER in role.access_levels
                    assert TAccessPermissionLevel.MANAGE_GROUPS in role.access_levels

            # -------- list roles for USER2 -----------
            print("Running access_levels test : list_roles for %s" % (USER2))
            ctx.enable_token_auth(token_str=USER2)

            params = _thrift_api.TListRolesParams()
            roles = list_roles(conn, params).roles

            assert contains_role(OKERA_PUBLIC_ROLE, roles)
            assert contains_role(ROLE1, roles)
            assert contains_role(ROLE2, roles)
            assert not contains_role(ROLE3, roles)

            for role in roles:
                if role.role_name == OKERA_PUBLIC_ROLE:
                    # USER2 does not have any explicit access on OKERA_PUBLIC_ROLE
                    # access_levels should be an empty list
                    assert not role.access_levels
                if role.role_name == ROLE1:
                    # privileges that USER2 has on ROLE1
                    assert TAccessPermissionLevel.ALL not in role.access_levels
                    assert TAccessPermissionLevel.SHOW in role.access_levels
                    assert TAccessPermissionLevel.DROP in role.access_levels
                    assert TAccessPermissionLevel.ALTER not in role.access_levels
                    assert TAccessPermissionLevel.MANAGE_GROUPS not in role.access_levels
                if role.role_name == ROLE2:
                    # USER2 would not have any access on it's own role unless specified explicitly
                    # access_levels should be an empty list
                    assert not role.access_levels

            # -------- list roles for USER3 -----------
            print("Running access_levels test : list_roles for %s" % (USER3))
            ctx.enable_token_auth(token_str=USER3)

            params = _thrift_api.TListRolesParams()
            roles = list_roles(conn, params).roles

            assert contains_role(OKERA_PUBLIC_ROLE, roles)
            assert not contains_role(ROLE1, roles)
            assert not contains_role(ROLE2, roles)
            assert contains_role(ROLE3, roles)

            for role in roles:
                if role.role_name == OKERA_PUBLIC_ROLE:
                    # USER3 does not have any explicit access on OKERA_PUBLIC_ROLE
                    # access_levels should be an empty list
                    assert not role.access_levels
                if role.role_name == ROLE3:
                    # USER3 would not have any access on it's own role unless specified explicitly
                    # access_levels should be an empty list
                    assert not role.access_levels

    def test_role_list_roles_user_role(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            steward_role = "role_priv_steward_user_role"
            as_owner_role = "_okera_internal_role_%s" % (TEST_USER)
            test_db = "user_role_test_db"

            ctx.disable_auth()
            setup_ddls = [
                "DROP DATABASE IF EXISTS %s" % (test_db),

                # Setup steward role
                "DROP ROLE IF EXISTS %s" % (as_owner_role),
                "DROP ROLE IF EXISTS %s" % (steward_role),
                "CREATE ROLE %s" % (steward_role),
                "GRANT ROLE %s TO GROUP %s" % (steward_role, TEST_USER),

                # Grant specific privilege on specified object to the
                # steward role
                "GRANT CREATE_AS_OWNER ON CATALOG TO ROLE %s" % (steward_role),
            ]

            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            # Switch to the user
            ctx.enable_token_auth(token_str=TEST_USER)

            params = _thrift_api.TListRolesParams()
            roles = list_roles(conn, params).roles
            assert len(roles) >= 2
            assert contains_role(OKERA_PUBLIC_ROLE, roles)
            assert contains_role(steward_role, roles)
            assert not contains_role(as_owner_role, roles)

            conn.execute_ddl("CREATE DATABASE %s" % test_db)

            params = _thrift_api.TListRolesParams()
            roles = list_roles(conn, params).roles
            assert len(roles) >= 3
            assert contains_role(OKERA_PUBLIC_ROLE, roles)
            assert contains_role(steward_role, roles)
            assert contains_role(as_owner_role, roles)

            assert get_role_by_name(steward_role, roles).is_user_role == False
            assert get_role_by_name(as_owner_role, roles).is_user_role == True

            assert get_role(conn, as_owner_role).role.is_user_role == True
            assert get_role(conn, steward_role).role.is_user_role == False

    def test_expr_ast(self):
        role = "ast_test_role"
        test_attr_ns = "get_role_ns"
        test_attr = "%s.get_role_attr" % (test_attr_ns)

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            self._recreate_test_role(conn, role, [])

            setup_ddls = [
                "DROP ATTRIBUTE IF EXISTS %s" % (test_attr),
                "CREATE ATTRIBUTE %s" % (test_attr),
            ]
            for ddl in setup_ddls:
                conn.execute_ddl(ddl)

            ddl = """GRANT SELECT ON DATABASE okera_sample
                HAVING ATTRIBUTE IN (%s)
                TRANSFORM %s WITH mask()
                WHERE record = 'abc' AND record IS NOT NULL
                TO ROLE %s""" % (test_attr, test_attr, role)
            conn.execute_ddl(ddl)

            result = get_role(conn, role, True)
            self.assertEqual(1, len(result.role.privileges))
            priv = result.role.privileges[0]

            self.assertTrue(priv.attribute_expression_tree is not None)
            self.assertTrue(priv.filter_expression_tree is not None)
            self.assertTrue(priv.transform_expressions is not None)

            self.assertEqual(1, len(priv.transform_expressions))
            transform = priv.transform_expressions[0]
            e = ExprUtils.convert_expr_ast_to_json(transform.expr)
            f = ExprUtils.convert_expr_ast_to_json(transform.fn)
            expected_e = json.loads('''
              {
                "sql": "get_role_ns.get_role_attr",
                "type": "ATTRIBUTE"
              }''')
            print(json.dumps(e, indent=2))
            self.assertEqual(expected_e, e)

            expected_f = json.loads('''
              {
                "type": "FUNCTION",
                "children": [
                  {
                    "type": "ATTRIBUTE",
                    "sql": "`__column__`"
                  }
                ],
                "sql": "mask"
              }''')
            print(json.dumps(f, indent=2))
            self.assertEqual(expected_f, f)

            f = ExprUtils.convert_expr_ast_to_json(priv.filter_expression_tree)
            expected = json.loads('''
              {
                "type": "FUNCTION",
                "children": [
                  {
                    "type": "OPERATOR",
                    "children": [
                      {
                        "type": "COLUMN",
                        "sql": "record"
                      },
                      {
                        "type": "LITERAL",
                        "sql": "abc"
                      }
                    ],
                    "sql": "="
                  },
                  {
                    "type": "FUNCTION",
                    "children": [
                      {
                        "sql": "record",
                        "type": "COLUMN"
                      }
                    ],
                    "sql": "IS NOT NULL"
                  }
                ],
                "sql": "all_of"
              }''')
            print(json.dumps(f, indent=2))
            self.assertEqual(expected, f)

            f = ExprUtils.convert_expr_ast_to_json(priv.attribute_expression_tree)
            expected = json.loads('''
            {
              "sql": "IN",
              "type": "FUNCTION",
              "children": [
                {
                  "sql": "NULL",
                  "type": "LITERAL"
                },
                {
                  "sql": "get_role_ns.get_role_attr",
                  "type": "ATTRIBUTE"
                }
              ]
            }
            ''')
            print(json.dumps(f, indent=2))
            self.assertEqual(expected, f)

if __name__ == "__main__":
    unittest.main()
