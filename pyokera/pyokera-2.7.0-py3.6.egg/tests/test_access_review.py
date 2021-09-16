# Copyright 2017 Okera Inc. All Rights Reserved.
#
# Tests that should run on any configuration. The server auth can be specified
# as an environment variables before running this test.

# pylint: disable=no-member
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=bad-continuation
# pylint: disable=bad-indentation
import time
import unittest
import string
import random

from okera.tests import pycerebro_test_common as common

TEST_DB = 'access_review_test_db'

def generate_random_users(num):
    users = []
    for _ in range(num):
        res = ''.join(random.choice(string.ascii_lowercase)  for i in range(5))
        user = 'user_' + res
        users.append(user)
    return users

def generate_random_tables(conn, num):
    tables = []
    for _ in range(num):
        res = ''.join(random.choice(string.ascii_lowercase)  for i in range(5))
        table_name = '%s.table_%s' % (TEST_DB, res)
        tables.append(table_name)
        conn.execute_ddl('CREATE TABLE %s (col1 int)' % table_name)
    return tables

def get_users_and_groups(ctx, conn, expected_users=None, tries=5):
    attempt = 0
    expected_users = expected_users or []
    while attempt < tries:
        ctx.enable_token_auth(token_str='root')
        results = conn.scan_as_json('select * from okera_system.groups_by_user')
        users_to_groups = {}
        for result in results:
            groups = users_to_groups.get(result['user_name'], set())
            groups.add(result['group_name'])
            users_to_groups[result['user_name']] = groups

        found_users = 0
        for expected_user in expected_users:
            if expected_user in users_to_groups:
                found_users += 1
        if found_users == len(expected_users):
            return users_to_groups

        time.sleep(2)
        attempt += 1

    raise Exception("Couldn't find users '%s' after %s tries" % (expected_users, tries))

def get_access(ctx, conn, expected_accesses=None, tries=5):
    attempt = 0
    expected_accesses = expected_accesses or []
    while attempt < tries:
        ctx.enable_token_auth(token_str='root')
        results = conn.scan_as_json(
            'select * from okera_system.catalog_identity_mappings')
        access_mappings = {}
        for result in results:
            objects = access_mappings.get(result['identity_object_name'], set())
            objects.add(result['catalog_object_name'])
            access_mappings[result['identity_object_name']] = objects

        found_accesses = 0
        for expected_access in expected_accesses:
            if expected_access['user'] in access_mappings:
                found_tables = 0
                for obj in expected_access['objects']:
                    if obj not in access_mappings[expected_access['user']]:
                        continue
                    found_tables += 1

                if found_tables == len(expected_access['objects']):
                    found_accesses += 1

        if found_accesses == len(expected_accesses):
            return access_mappings

        time.sleep(2)
        attempt += 1

    raise Exception(
        "Couldn't find mappings '%s' after %s tries" % (expected_accesses, tries))


class AccessReviewTest(unittest.TestCase):

    def test_basic_access_review(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % TEST_DB)
            conn.execute_ddl('CREATE DATABASE %s' % TEST_DB)

            random_users = generate_random_users(3)
            random_tables = generate_random_tables(conn, 3)
            random_accesses = [dict(user=u, objects=random_tables) for u in random_users]

            for access in random_accesses:
                role_name = 'access_review_test_role_%s' % access['user']
                conn.execute_ddl('CREATE ROLE IF NOT EXISTS %s' % role_name)
                conn.execute_ddl(
                    'GRANT ROLE %s TO GROUP %s' % (role_name, access['user']))
                for table in access['objects']:
                    conn.execute_ddl(
                        'GRANT SELECT ON TABLE %s TO ROLE %s' % (table, role_name))

            for user in random_users:
                ctx.enable_token_auth(token_str=user)
                for table in random_tables:
                    conn.scan_as_json('select * from %s' % table)

            users_and_groups = get_users_and_groups(
                ctx, conn, expected_users=random_users, tries=16)
            self.assertTrue(users_and_groups is not None)
            accesses = get_access(
                ctx, conn, expected_accesses=random_accesses, tries=16)
            self.assertTrue(accesses is not None)

if __name__ == "__main__":
    unittest.main()
