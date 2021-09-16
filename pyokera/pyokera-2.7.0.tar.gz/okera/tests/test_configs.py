# Copyright 2019 Okera Inc. All Rights Reserved.

#
# Tests for config CRUD APIs.
#
# pylint: disable=unused-argument

import unittest

from okera.tests import pycerebro_test_common as common
from okera._thrift_api import TConfigType, TRecordServiceException

upsert_config = common.upsert_config
list_configs = common.list_configs
delete_config = common.delete_config

def list_of_map_to_map(l, key_field):
    result = {}
    for v in l:
        key = v[key_field]
        result[key] = v
    return result

TEST_CONFIG_KEY1 = "test_configs_key1"
TEST_CONFIG_KEY2 = "test_configs_key2"

class ConfigsTest(unittest.TestCase):
    def test_basic(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Get and verify a system config
            configs = list_of_map_to_map(
                list_configs(conn, TConfigType.SYSTEM_CONFIG), 'key')
            self.assertTrue('audit.directory' in configs)
            self.assertEqual('/opt/okera/audit_logs', configs['audit.directory']['value'])

            # Upsert a new config and check the value
            # TODO: check return value
            upsert_config(conn, TConfigType.SYSTEM_CONFIG, [TEST_CONFIG_KEY1], "val1")
            configs = list_of_map_to_map(
                list_configs(conn, TConfigType.SYSTEM_CONFIG), 'key')
            self.assertEqual('val1', configs[TEST_CONFIG_KEY1]['value'])

            # Change the value
            upsert_config(conn, TConfigType.SYSTEM_CONFIG, [TEST_CONFIG_KEY1], "val2")
            configs = list_of_map_to_map(
                list_configs(conn, TConfigType.SYSTEM_CONFIG), 'key')
            self.assertEqual('val2', configs[TEST_CONFIG_KEY1]['value'])

            # Set to empty
            upsert_config(conn, TConfigType.SYSTEM_CONFIG, [TEST_CONFIG_KEY1], "")
            configs = list_of_map_to_map(
                list_configs(conn, TConfigType.SYSTEM_CONFIG), 'key')
            self.assertEqual('', configs[TEST_CONFIG_KEY1]['value'])

            # Add new config and check both
            upsert_config(conn, TConfigType.SYSTEM_CONFIG, [TEST_CONFIG_KEY2], "new_val1")
            configs = list_of_map_to_map(
                list_configs(conn, TConfigType.SYSTEM_CONFIG), 'key')
            self.assertEqual('', configs[TEST_CONFIG_KEY1]['value'])
            self.assertEqual('new_val1', configs[TEST_CONFIG_KEY2]['value'])

            # Delete first config
            delete_config(conn, TConfigType.SYSTEM_CONFIG, [TEST_CONFIG_KEY2])

            # Verify it is gone but other one is there
            configs = list_of_map_to_map(
                list_configs(conn, TConfigType.SYSTEM_CONFIG), 'key')
            self.assertEqual('', configs[TEST_CONFIG_KEY1]['value'])
            self.assertTrue(TEST_CONFIG_KEY2 not in  configs)

            # Delete the second config, verify both are gone
            delete_config(conn, TConfigType.SYSTEM_CONFIG, [TEST_CONFIG_KEY1])
            configs = list_of_map_to_map(
                list_configs(conn, TConfigType.SYSTEM_CONFIG), 'key')
            self.assertTrue(TEST_CONFIG_KEY1 not in  configs)
            self.assertTrue(TEST_CONFIG_KEY2 not in  configs)

    def test_abac(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            upsert_config(
                conn, TConfigType.SYSTEM_CONFIG, ['feature.ui.test_feature'], "true")
            upsert_config(
                conn, TConfigType.SYSTEM_CONFIG, ['test_feature'], "yes")
            query = 'SELECT * FROM okera_system.configs WHERE key = "test_feature"'
            superuser_list = conn.scan_as_json(query)
            anyuser_list = conn.scan_as_json(query, requesting_user='anyuser')

            self.assertEqual(1, len(superuser_list))
            self.assertEqual('test_feature', superuser_list[0].get('key'))
            self.assertEqual([], anyuser_list)

    def test_upsert_regex_autotagger(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Clean up tagging rules from  previous tests
            for c in list_configs(conn, TConfigType.AUTOTAGGER_REGEX):
                if c['namespace'] == 'test_ns' and c['tag'] == 'rule1':
                    delete_config(conn, TConfigType.AUTOTAGGER_REGEX, str(c['id']))

            params = {}
            params['name'] = 'great_rule'
            params['namespace'] = 'test_ns'
            params['description'] = 'a great regex'
            params['min_rows'] = '1'
            params['max_rows'] = '10'
            params['match_rate'] = '.4'
            params['match_column_name'] = 'true'
            params['match_column_comment'] = 'true'

            params['tag'] = 'rule1'
            params['expression'] = '*'
            with self.assertRaises(TRecordServiceException):
                upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, None, params)
            params['expression'] = '.*'
            upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, None, params)

            rule = None
            for c in list_configs(conn, TConfigType.AUTOTAGGER_REGEX):
                if c['namespace'] == 'test_ns' and c['tag'] == 'rule1':
                    rule = c
                    break
            self.assertTrue(rule is not None)
            self.assertEqual('test_ns', rule['namespace'])
            self.assertEqual('.*', rule['expression'])
            self.assertEqual('a great regex', rule['description'])
            self.assertTrue(rule['match_column_name'])
            self.assertTrue(rule['match_column_comment'])
            self.assertEqual('great_rule', rule['name'])

            # Update the expression
            params['expression'] = 'a.*'
            old_id = rule['id']
            upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, [str(old_id)], params)

            rule = None
            for c in list_configs(conn, TConfigType.AUTOTAGGER_REGEX):
                if c['namespace'] == 'test_ns' and c['tag'] == 'rule1':
                    rule = c
                    break
            self.assertTrue(rule is not None)
            self.assertEqual('test_ns', rule['namespace'])
            self.assertEqual('a.*', rule['expression'])
            self.assertEqual('great_rule', rule['name'])
            self.assertEqual(old_id, rule['id'])

            # Ensure we cannot update an expression removing the name
            del params['name']
            with self.assertRaises(TRecordServiceException):
                upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, [str(old_id)], params)

            # Add another expression to the same tag
            params = {}
            params['name'] = 'greater_rule'
            params['namespace'] = 'test_ns'
            params['description'] = 'another great regex'
            params['min_rows'] = '3'
            params['max_rows'] = '55'
            params['match_rate'] = '.2'

            params['tag'] = 'rule1'
            params['expression'] = 'foo*'

            old_name = params['name']

            upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, None, params)

            rules = []
            for c in list_configs(conn, TConfigType.AUTOTAGGER_REGEX):
                if c['namespace'] == 'test_ns' and c['tag'] == 'rule1':
                    rules.append(c)
            self.assertEqual(2, len(rules))
            self.assertTrue(old_id in (rules[0]['id'], rules[1]['id']))

            # Try to add a rule without a name
            params = {}
            params['namespace'] = 'test_ns'
            params['description'] = 'another great regex'
            params['min_rows'] = '3'
            params['max_rows'] = '55'
            params['match_rate'] = '.2'

            params['tag'] = 'rule1'
            params['expression'] = 'foo*'
            with self.assertRaises(TRecordServiceException):
                upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, None, params)

            # Set the name to the empty string: this also should fail
            params['name'] = ''
            with self.assertRaises(TRecordServiceException):
                upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, None, params)

            # Set the name to an existing name: this should fail
            params['name'] = old_name
            with self.assertRaises(TRecordServiceException):
                upsert_config(conn, TConfigType.AUTOTAGGER_REGEX, None, params)

if __name__ == "__main__":
    unittest.main()
