# Copyright 2017 Okera Inc. All Rights Reserved.
#
# Tests some queries against nightly
import os
import unittest

from okera import context
from okera.tests import pycerebro_test_common as common

ROOT_TOKEN = os.environ['OKERA_HOME'] + '/integration/tokens/cerebro.token'
NIGHTLY_PLANNER = 'nightly.internal.okera.rocks'

class ConnectionErrorsTest(unittest.TestCase):

    @unittest.skipIf(common.TEST_LEVEL not in {'ci', 'all'}, "Skipping at not ci level.")
    def test_okera_sample_users(self):
        ctx = context()
        ctx.enable_token_auth(token_file=ROOT_TOKEN)
        with ctx.connect(NIGHTLY_PLANNER) as conn:
            json_data = conn.scan_as_json('okera_sample.users')
            self.assertEqual(38455, len(json_data))
            json_data = conn.scan_as_json('okera_sample.users', max_records=200)
            self.assertEqual(200, len(json_data))
            json_data = conn.scan_as_json('okera_sample.users', max_records=40000)
            self.assertEqual(38455, len(json_data))

            json_data = conn.scan_as_json('okera_sample.users',
                                          max_records=200,
                                          max_client_process_count=2)
            self.assertEqual(200, len(json_data))
            pd = conn.scan_as_pandas('okera_sample.users')
            self.assertEqual(38455, len(pd))
            pd = conn.scan_as_pandas('okera_sample.users', max_records=200)
            self.assertEqual(200, len(pd))
            pd = conn.scan_as_pandas('okera_sample.users', max_records=40000)
            self.assertEqual(38455, len(pd))
            pd = conn.scan_as_pandas('okera_sample.users',
                                     max_records=200,
                                     max_client_process_count=2)
            self.assertEqual(200, len(pd))

    @unittest.skipIf(common.TEST_LEVEL == 'smoke', "Skipping at unit test level.")
    def test_okera_fs_read(self):
        common.configure_botocore_patch()
        import boto3
        s3 = boto3.client('s3')
        res = s3.get_object(Bucket='cerebrodata-test', Key='large-doubles/data.txt')
        output = res['Body'].read().decode('UTF-8').strip(' \t\n\r')
        self.assertEqual(output, '901225911454.29')

if __name__ == "__main__":
    unittest.main()
