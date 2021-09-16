# Copyright 2017 Okera Inc. All Rights Reserved.
#
# Tests that should run on any configuration. The server auth can be specified
# as an environment variables before running this test.

# pylint: disable=no-member
# pylint: disable=no-self-use
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=bad-continuation
# pylint: disable=bad-indentation

import os
import pytest
import random
import string
import unittest

from okera import _thrift_api
from okera.tests import pycerebro_test_common as common

from okera._thrift_api import (
    TListFilesOp, TListFilesParams
)

import okera_cli.plugin.boto as okera_boto

import botocore
import boto3

def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

BUILD_TAG = os.environ.get('BUILD_TAG', random_string(10))

REST_SERVER_URL = common.get_rest_server_url()
ACCESS_PROXY_URL = common.get_access_proxy_url()
TOKEN_CONFIG_SOURCE='config'

BOTO_ROOT_BUCKET = "cerebrodata-test"
BOTO_ROOT_PREFIX = "fs_test/"
BOTO_ROOT_WRITE_PREFIX = "fs_test_write/%s/" % BUILD_TAG
BOTO_ROOT_URL = "s3://%s/%s" % (BOTO_ROOT_BUCKET, BOTO_ROOT_PREFIX)
BOTO_ROOT_WRITE_URL = "s3://%s/%s" % (BOTO_ROOT_BUCKET, BOTO_ROOT_WRITE_PREFIX)
BOTO_FS_ROLE = 'test_boto_role'
BOTO_FS_USER = 'testbotouser1'
BOTO_FS_USER_NO_ACCESS = 'testbotouser2'
BOTO_FS_USER_ROOT = 'root'

USER_SESSION = okera_boto.okera_session(boto3.session.Session(), BOTO_FS_USER, TOKEN_CONFIG_SOURCE, REST_SERVER_URL, ACCESS_PROXY_URL)
USER_S3_CLIENT = USER_SESSION.client('s3', verify=False, region_name='us-west-2')

USER_NO_ACCESS_SESSION = okera_boto.okera_session(boto3.session.Session(), BOTO_FS_USER_NO_ACCESS, TOKEN_CONFIG_SOURCE, REST_SERVER_URL, ACCESS_PROXY_URL)
USER_NO_ACCESS_S3_CLIENT = USER_NO_ACCESS_SESSION.client('s3', verify=False, region_name='us-west-2')

USER_ROOT_SESSION = okera_boto.okera_session(boto3.session.Session(), BOTO_FS_USER_ROOT, TOKEN_CONFIG_SOURCE, REST_SERVER_URL, ACCESS_PROXY_URL)
USER_ROOT_S3_CLIENT = USER_ROOT_SESSION.client('s3', verify=False, region_name='us-west-2')

def authorize_uri(planner, user, action, uri):
    params = TListFilesParams()
    params.op = action
    params.object = uri
    params.requesting_user = user
    params.authorize_only = True
    return planner.service.client.ListFiles(params)

class FsTest(unittest.TestCase):
    def test_grant(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)

        URI_BASE = 's3://cerebrodata-test/nytaxi-data'
        TEST_USER = 'fs_test_user'

        grant_ddls = [
            "GRANT SELECT ON URI '%s/csv' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT SHOW ON URI '%s/parquet' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT ALL ON URI '%s/orc' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT SELECT ON URI '%s/uber' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT SHOW ON URI '%s/uber' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT INSERT ON URI '%s/uber' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT DELETE ON URI '%s/uber' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT INSERT ON URI '%s/parquet' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT DELETE ON URI '%s/parquet' TO ROLE %s_role" % (URI_BASE, TEST_USER),
            "GRANT SELECT ON URI '%s/whatever' TO ROLE %s_role WITH GRANT OPTION" % (URI_BASE, TEST_USER),
            "GRANT ALL ON URI '%s/whatever' TO ROLE %s_role WITH GRANT OPTION" % (URI_BASE, TEST_USER),
        ]

        role_ddls = [
            "DROP ROLE IF EXISTS %s_role" % (TEST_USER),
            "CREATE ROLE %s_role" % (TEST_USER),
            "GRANT ROLE %s_role TO GROUP %s" % (TEST_USER, TEST_USER),
        ]
        # the order is important here we want role ones to be executed first
        ddls = role_ddls + grant_ddls
        for ddl in ddls:
            planner.execute_ddl(ddl)

        result = planner.execute_ddl("SHOW GRANT ROLE %s_role" % TEST_USER)
        # all grants have been applied
        self.assertEqual(len(result), len(grant_ddls))

        # For list, check that we only have access if we granted SHOW or ALL
        authorize_uri(planner, TEST_USER, TListFilesOp.LIST, '%s/parquet' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.LIST, '%s/orc' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.LIST, '%s/uber' % URI_BASE)
        with self.assertRaisesRegex(_thrift_api.TRecordServiceException,
                                    'does not have access'):
            authorize_uri(planner, TEST_USER, TListFilesOp.LIST, '%s/csv' % URI_BASE)

        # For read, check that we only have access if we granted SELECT or ALL
        authorize_uri(planner, TEST_USER, TListFilesOp.READ, '%s/orc/000067_0' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.READ,
                      '%s/uber/10mb_chunksfk' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.READ,
                      '%s/csv/trips_xcp.csv.gz' % URI_BASE)
        with self.assertRaisesRegex(_thrift_api.TRecordServiceException,
                                    'does not have access'):
            authorize_uri(planner, TEST_USER, TListFilesOp.READ,
                          '%s/parquet/000067_0' % URI_BASE)

        # For write, check that we only have access if we granted INSERT or ALL
        authorize_uri(planner, TEST_USER, TListFilesOp.WRITE, '%s/parquet' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.WRITE, '%s/orc' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.WRITE, '%s/uber' % URI_BASE)
        with self.assertRaisesRegex(_thrift_api.TRecordServiceException,
                                    'does not have access'):
            authorize_uri(planner, TEST_USER, TListFilesOp.WRITE, '%s/csv' % URI_BASE)

        # For delete, check that we only have access if we granted DELETE or ALL
        authorize_uri(planner, TEST_USER, TListFilesOp.DELETE, '%s/parquet' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.DELETE, '%s/orc' % URI_BASE)
        authorize_uri(planner, TEST_USER, TListFilesOp.DELETE, '%s/uber' % URI_BASE)
        with self.assertRaisesRegex(_thrift_api.TRecordServiceException,
                                    'does not have access'):
            authorize_uri(planner, TEST_USER, TListFilesOp.DELETE, '%s/csv' % URI_BASE)

        revoke_ddls = [
            "REVOKE SELECT ON URI '%s/csv' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE SHOW ON URI '%s/parquet' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE ALL ON URI '%s/orc' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE SELECT ON URI '%s/uber' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE SHOW ON URI '%s/uber' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE INSERT ON URI '%s/uber' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE DELETE ON URI '%s/uber' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE INSERT ON URI '%s/parquet' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE DELETE ON URI '%s/parquet' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE SELECT ON URI '%s/whatever' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
            "REVOKE ALL ON URI '%s/whatever' FROM ROLE %s_role" % (URI_BASE, TEST_USER),
        ]
        for ddl in revoke_ddls:
            planner.execute_ddl(ddl)

        result = planner.execute_ddl("SHOW GRANT ROLE %s_role" % TEST_USER)
        print(result)
        # all grants have been deleted
        self.assertEqual(len(result), 0)

    # This test assumes the following files exist on S3:
    # s3://cerebrodata-test/fs_test/file1 --> has attribute abac_uri.attr1
    # s3://cerebrodata-test/fs_test/file2 --> does not have attribute abac_uri.attr1
    def test_abac_uri_grant(self):
        URI_BASE = 's3://cerebrodata-test/fs_test/'
        USER = 'fstestuser'
        ROLE = 'abac_uri_test_role'
        ATTR = 'abac_uri.attr1'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ctx.disable_auth()

            ddls = [
                "DROP ROLE IF EXISTS %s" % (ROLE),
                "DROP ATTRIBUTE IF EXISTS %s" % (ATTR),

                "CREATE ATTRIBUTE %s" % (ATTR),

                # Create the role and grant it to the user
                "CREATE ROLE %s" % (ROLE),
                "GRANT ROLE %s TO GROUP %s" % (ROLE, USER),

                # Grant the user the right permissions
                "GRANT ALL ON URI '%s' HAVING ATTRIBUTE IN (%s) TO ROLE %s" % (URI_BASE, ATTR, ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            authorize_uri(conn, USER, TListFilesOp.READ, '%sfile1' % URI_BASE)
            with self.assertRaisesRegex(_thrift_api.TRecordServiceException,
                                        'does not have access'):
                authorize_uri(conn, USER, TListFilesOp.READ, '%sfile2' % URI_BASE)

    def test_ls(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        result = planner.ls('s3://cerebrodata-test/fs_test_do_not_add_files_here/sample/')
        self.assertEqual(
                ['s3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt'],
                result)
        result = planner.ls(
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample')
        self.assertEqual(
                ['s3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt'],
                result)
        result = planner.ls(
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt')
        self.assertEqual(
                ['s3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt'],
                result)
        result = planner.ls(
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt2')
        self.assertEqual([], result)
        planner.close()

    def test_cat(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        result = planner.cat(
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt')
        self.assertEqual('This is a sample test file.\nIt should consist of two lines.',
                         result)
        planner.close()

    def test_errors(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        with self.assertRaises(ValueError):
            planner.cat(
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample/not-a-file')
        planner.close()

    def test_as_testuser(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='testuser')
        planner = common.get_planner(ctx)

        # Test user has access to this directory by URI
        result = planner.ls('s3://cerebrodata-test/fs_test_do_not_add_files_here/sample/')
        self.assertEqual([
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt'],
                result)
        result = planner.ls(
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt')
        self.assertEqual(
                ['s3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt'],
                result)
        result = planner.ls(
                's3://cerebrodata-test/fs_test_do_not_add_files_here/sample/sample.txt2')
        self.assertEqual([], result)

        # Test user does not have access to this directory
        with self.assertRaisesRegex(_thrift_api.TRecordServiceException,
                                    'does not have access'):
            result = planner.ls('s3://cerebro-datasets/nytaxi-data/')

class RegisteredTest(unittest.TestCase):
    def test_basic(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        result = planner.get_catalog_objects_at('file:/opt/okera/data/users')
        self.assertTrue('file:/opt/okera/data/users' in result)
        self.assertTrue('okera_sample.users' in result['file:/opt/okera/data/users'])
        self.assertTrue('cerebro_sample.users' in result['file:/opt/okera/data/users'])

        result = planner.get_catalog_objects_at('file:/opt/okera/data/')
        self.assertTrue('file:/opt/okera/data/sample' in result)
        self.assertTrue('file:/opt/okera/data/users' in result)

        result = planner.get_catalog_objects_at('s3://cerebrodata-test/users')
        self.assertEqual(0, len(result))

        # Two datasets registered here
        result = planner.get_catalog_objects_at('s3://cerebro-datasets/transactions')
        self.assertEqual(1, len(result))
        datasets = result['s3://cerebro-datasets/transactions']
        self.assertEqual(2, len(datasets), msg=str(datasets))

        # Should not capture results from '/decimal-test1'
        result = planner.get_catalog_objects_at('s3://cerebrodata-test/decimal-test')
        self.assertEqual(1, len(result), msg=str(result))
        result = result['s3://cerebrodata-test/decimal-test']
        self.assertEqual(2, len(result), msg=str(result))

        result = planner.cat('s3://cerebrodata-test/alltypes')
        self.assertEqual('true|0|1|2|3|4.0|5.0|hello|vchar1|char1|2015-01-01|3.141592',
                         result.split('\n')[0])

        planner.close()

    def test_as_testuser(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='testuser')
        planner = common.get_planner(ctx)

        result = planner.get_catalog_objects_at('file:/opt/okera/data/')
        self.assertTrue('file:/opt/okera/data/sample' in result)
        self.assertTrue('file:/opt/okera/data/users' in result)

        result = planner.get_catalog_objects_at('s3://cerebrodata-test/users')
        self.assertEqual(0, len(result))

        result1 = planner.get_catalog_objects_at('s3://cerebro-datasets/transactions')
        self.assertEqual(1, len(result1))

        result2 = planner.get_catalog_objects_at('s3://cerebro-datasets/transactions///')
        self.assertEqual(1, len(result2))

        result3 = planner.get_catalog_objects_at('s3://cerebro-datasets/transactions/')
        self.assertEqual(1, len(result3))

        # Two datasets registered here, but this user only has one. Make sure it is
        # ACLed correctly.
        result = planner.get_catalog_objects_at('s3://cerebro-datasets/transactions')
        self.assertEqual(1, len(result))
        datasets = result['s3://cerebro-datasets/transactions']
        self.assertEqual(1, len(datasets))
        self.assertTrue('demo_test.transactions' in datasets)

        # Test user does not have access to this directory
        with self.assertRaisesRegex(_thrift_api.TRecordServiceException,
                                    'does not have access'):
            planner.get_catalog_objects_at('s3://cerebrodata-test/decimal-test')

        # Reading a path but this user only has column level permissions so only
        # a subset of the columns come back.
        result = planner.cat('s3://cerebrodata-test/alltypes')
        self.assertEqual('2,4.0,hello', result.split('\n')[0])
        planner.close()

    def test_masking(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        planner = common.get_planner(ctx)
        result = planner.cat('s3://cerebrodata-test/ccn').split('\n')[0]
        self.assertEqual('user1,4539797705756008', result)
        planner.close()

        ctx.enable_token_auth(token_str='testuser')
        planner = common.get_planner(ctx)
        result = planner.cat('s3://cerebrodata-test/ccn').split('\n')[0]
        self.assertEqual('user1,XXXXXXXXXXXX6008', result)
        planner.close()

    def test_dropping(self):
        ctx = common.get_test_context()
        planner = common.get_planner(ctx)
        planner.execute_ddl("DROP DATABASE IF EXISTS ofs CASCADE")
        planner.execute_ddl("CREATE DATABASE ofs")
        planner.execute_ddl(
            "CREATE EXTERNAL TABLE ofs.t1(s string) " +
            "LOCATION 's3://cerebrodata-test/empty-path-test'")

        result = planner.get_catalog_objects_at('s3://cerebrodata-test/empty-path-test')
        self.assertEqual(1, len(result))
        datasets = result['s3://cerebrodata-test/empty-path-test']
        self.assertEqual(1, len(datasets))
        self.assertEqual('ofs.t1', datasets[0])

        # Create T2
        planner.execute_ddl(
            "CREATE EXTERNAL TABLE ofs.t2(s string) " +
            "LOCATION 's3://cerebrodata-test/empty-path-test'")
        result = planner.get_catalog_objects_at('s3://cerebrodata-test/empty-path-test')
        datasets = result['s3://cerebrodata-test/empty-path-test']
        self.assertEqual(2, len(datasets))
        self.assertTrue('ofs.t1' in datasets)
        self.assertTrue('ofs.t2' in datasets)

        # Drop t2, path should be gone
        planner.execute_ddl("DROP TABLE ofs.t2")
        result = planner.get_catalog_objects_at('s3://cerebrodata-test/empty-path-test')
        self.assertEqual(1, len(result))
        datasets = result['s3://cerebrodata-test/empty-path-test']
        self.assertEqual(1, len(datasets))
        self.assertEqual('ofs.t1', datasets[0])

        # Drop t1, path should be gone
        planner.execute_ddl("DROP TABLE ofs.t1")
        result = planner.get_catalog_objects_at('s3://cerebrodata-test/empty-path-test')
        self.assertEqual(0, len(result))

class AccessProxyTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        # For some reason these disables need to be done when the class is instantiated
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        super().__init__(*args, **kwargs)

    def test_boto_list(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP ROLE IF EXISTS %s" % (BOTO_FS_ROLE),
                "CREATE ROLE %s" % (BOTO_FS_ROLE),
                "GRANT ROLE %s TO GROUP %s" % (BOTO_FS_ROLE, BOTO_FS_USER),

                "GRANT SHOW ON URI '%s' TO ROLE %s" % (BOTO_ROOT_URL, BOTO_FS_ROLE)
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = USER_S3_CLIENT.list_objects_v2(Bucket=BOTO_ROOT_BUCKET, Prefix=BOTO_ROOT_PREFIX)
            assert len(res["Contents"]) == 2
            filenames = [f["Key"].split("/")[-1] for f in res["Contents"]]
            assert "file1" in filenames
            assert "file2" in filenames

            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                USER_NO_ACCESS_S3_CLIENT.list_objects_v2(Bucket=BOTO_ROOT_BUCKET, Prefix=BOTO_ROOT_PREFIX)
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

    def test_boto_read(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP ROLE IF EXISTS %s" % (BOTO_FS_ROLE),
                "CREATE ROLE %s" % (BOTO_FS_ROLE),
                "GRANT ROLE %s TO GROUP %s" % (BOTO_FS_ROLE, BOTO_FS_USER),

                "GRANT SELECT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_URL, BOTO_FS_ROLE)
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = USER_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%sfile1" % (BOTO_ROOT_PREFIX))
            body = res['Body'].read().strip().decode('utf-8')
            assert body == '12345'

            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                USER_NO_ACCESS_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%sfile1" % (BOTO_ROOT_PREFIX))
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

    def test_boto_write(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP ROLE IF EXISTS %s" % (BOTO_FS_ROLE),
                "CREATE ROLE %s" % (BOTO_FS_ROLE),
                "GRANT ROLE %s TO GROUP %s" % (BOTO_FS_ROLE, BOTO_FS_USER),

                "GRANT SELECT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_URL, BOTO_FS_ROLE),
                "GRANT INSERT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_WRITE_URL, BOTO_FS_ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            orig_body = random_string(5)
            USER_S3_CLIENT.put_object(Body=orig_body, Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)

            # Ensure the file is good (as root)
            res = USER_ROOT_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            body = res['Body'].read().strip().decode('utf-8')
            assert body == orig_body

            # Ensure that our writing user can't read it (shouldn't have permissions)
            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                res = USER_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                USER_NO_ACCESS_S3_CLIENT.put_object(Body=orig_body, Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

    def test_boto_copy(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP ROLE IF EXISTS %s" % (BOTO_FS_ROLE),
                "CREATE ROLE %s" % (BOTO_FS_ROLE),
                "GRANT ROLE %s TO GROUP %s" % (BOTO_FS_ROLE, BOTO_FS_USER),

                "GRANT SELECT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_URL, BOTO_FS_ROLE),
                "GRANT INSERT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_WRITE_URL, BOTO_FS_ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            USER_S3_CLIENT.copy_object(
                Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX,
                CopySource="%s/%sfile1" % (BOTO_ROOT_BUCKET, BOTO_ROOT_PREFIX))

            res = USER_ROOT_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            body = res['Body'].read().strip().decode('utf-8')
            assert body == '12345'

            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                USER_NO_ACCESS_S3_CLIENT.copy_object(
                    Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX,
                    CopySource="%s/%sfile1" % (BOTO_ROOT_BUCKET, BOTO_ROOT_PREFIX))
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

    def test_boto_delete(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP ROLE IF EXISTS %s" % (BOTO_FS_ROLE),
                "CREATE ROLE %s" % (BOTO_FS_ROLE),
                "GRANT ROLE %s TO GROUP %s" % (BOTO_FS_ROLE, BOTO_FS_USER),

                "GRANT DELETE ON URI '%s' TO ROLE %s" % (BOTO_ROOT_WRITE_URL, BOTO_FS_ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            USER_ROOT_S3_CLIENT.copy_object(
                Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX,
                CopySource="%s/%sfile1" % (BOTO_ROOT_BUCKET, BOTO_ROOT_PREFIX))

            res = USER_S3_CLIENT.delete_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            assert res['ResponseMetadata']['HTTPStatusCode'] == 204

            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                USER_NO_ACCESS_S3_CLIENT.delete_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

    def test_boto_metadata(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP ROLE IF EXISTS %s" % (BOTO_FS_ROLE),
                "CREATE ROLE %s" % (BOTO_FS_ROLE),
                "GRANT ROLE %s TO GROUP %s" % (BOTO_FS_ROLE, BOTO_FS_USER),

                "GRANT SELECT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_URL, BOTO_FS_ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            res = USER_S3_CLIENT.head_object(Bucket=BOTO_ROOT_BUCKET, Key="%sfile1" % (BOTO_ROOT_PREFIX))
            assert res['ContentLength'] == 6

            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                USER_NO_ACCESS_S3_CLIENT.head_object(Bucket=BOTO_ROOT_BUCKET, Key="%sfile1" % (BOTO_ROOT_PREFIX))
            self.assertTrue('HeadObject operation: Forbidden' in str(ex_ctx.exception))

    def test_boto_abac_grant(self):
        ATTR = 'abac_uri.attr1'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            ddls = [
                "DROP ROLE IF EXISTS %s" % (BOTO_FS_ROLE),
                "DROP ATTRIBUTE IF EXISTS %s" % (ATTR),
                "CREATE ATTRIBUTE %s" % (ATTR),
                "CREATE ROLE %s" % (BOTO_FS_ROLE),
                "GRANT ROLE %s TO GROUP %s" % (BOTO_FS_ROLE, BOTO_FS_USER),

                "GRANT SELECT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_URL, BOTO_FS_ROLE),
                "GRANT INSERT ON URI '%s' TO ROLE %s" % (BOTO_ROOT_WRITE_URL, BOTO_FS_ROLE),
                "GRANT SELECT ON URI '%s' HAVING ATTRIBUTE IN (%s) TO ROLE %s" % (BOTO_ROOT_WRITE_URL, ATTR, BOTO_FS_ROLE),
            ]

            for ddl in ddls:
                conn.execute_ddl(ddl)

            orig_body = random_string(5)
            USER_S3_CLIENT.put_object(Body=orig_body, Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)

            # After the copy, we still can't read it as it does not have the tag
            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                USER_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

            # Add the tag
            USER_ROOT_S3_CLIENT.put_object_tagging(
               Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX,
               Tagging={
                   'TagSet': [{"Key": ATTR, "Value": ""}]},
            )

            # Now we should be able to access it
            res = USER_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            body = res['Body'].read().strip().decode('utf-8')
            assert body == orig_body

            # Ensure the no access user can't access it
            with self.assertRaises(botocore.exceptions.ClientError) as ex_ctx:
                res = USER_NO_ACCESS_S3_CLIENT.get_object(Bucket=BOTO_ROOT_BUCKET, Key="%swrite_file1" % BOTO_ROOT_WRITE_PREFIX)
            self.assertTrue('Access Denied' in str(ex_ctx.exception))

if __name__ == "__main__":
    unittest.main()
