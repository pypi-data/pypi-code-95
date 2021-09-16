# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for user attributes
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

from okera._thrift_api import (
    TGetUserAttributesParams, TRecordServiceException)

from okera import _thrift_api

class UserAttributesTest(common.TestBase):
    def test_all_users(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Generate some users and fetch user attributes for them so we
            # can get the values when we fetch it all.
            users = [common.random_string(10), common.random_string(10)]
            for user in users:
                ctx.enable_token_auth(token_str=user)
                conn.scan_as_json("select user_attribute('whoami')", dialect='okera')

            ctx.disable_auth()

            print("Checking user attributes for:", users)

            params = TGetUserAttributesParams()
            params.all_users = True
            results = conn.service.client.GetUserAttributes(params)
            all_attributes = results.attributes
            assert len(all_attributes) >= len(users)
            for user in users:
                assert user in all_attributes
                assert 'whoami' in all_attributes[user]
                assert all_attributes[user]['whoami'].value == user
                assert all_attributes[user]['whoami'].source == 'static'

            # Ensure we can't access this as a non-admin user
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                params = TGetUserAttributesParams()
                params.requesting_user = users[0]
                params.all_users = True
                conn.service.client.GetUserAttributes(params)
            self.assertTrue('Only admins can request user attributes for all users' in str(ex_ctx.exception))

    def test_specific_user(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Generate some users and fetch user attributes for them so we
            # can get the values when we fetch it all.
            user = common.random_string(10)
            ctx.enable_token_auth(token_str=user)
            conn.scan_as_json("select user_attribute('whoami')", dialect='okera')

            ctx.disable_auth()

            print("Checking user attributes for:", user)

            params = TGetUserAttributesParams()
            params.user = user
            results = conn.service.client.GetUserAttributes(params)
            all_attributes = results.attributes
            assert len(all_attributes) >= 1
            assert user in all_attributes
            assert 'whoami' in all_attributes[user]
            assert all_attributes[user]['whoami'].value == user
            assert all_attributes[user]['whoami'].source == 'static'

            # Ensure we can access it as the same user
            params = TGetUserAttributesParams()
            params.requesting_user = user
            params.user = user
            results = conn.service.client.GetUserAttributes(params)
            all_attributes = results.attributes
            assert len(all_attributes) >= 1
            assert user in all_attributes
            assert 'whoami' in all_attributes[user]
            assert all_attributes[user]['whoami'].value == user
            assert all_attributes[user]['whoami'].source == 'static'

            # Ensure we can't access this as a non-admin user
            with self.assertRaises(TRecordServiceException) as ex_ctx:
                params = TGetUserAttributesParams()
                params.requesting_user = common.random_string(10)
                params.user = user
                conn.service.client.GetUserAttributes(params)
            self.assertTrue('user attributes for a user other than themselves' in str(ex_ctx.exception))

    def test_current_user(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Generate some users and fetch user attributes for them so we
            # can get the values when we fetch it all.
            users = [common.random_string(10), common.random_string(10)]
            for user in users:
                ctx.enable_token_auth(token_str=user)
                conn.scan_as_json("select user_attribute('whoami')", dialect='okera')

            print("Checking user attributes for:", users)

            for user in users:
                ctx.enable_token_auth(token_str=user)
                params = TGetUserAttributesParams()
                params.requesting_user = user
                results = conn.service.client.GetUserAttributes(params)
                all_attributes = results.attributes
                assert len(all_attributes) == 1
                assert user in all_attributes
                assert 'whoami' in all_attributes[user]
                assert all_attributes[user]['whoami'].value == user
                assert all_attributes[user]['whoami'].source == 'static'