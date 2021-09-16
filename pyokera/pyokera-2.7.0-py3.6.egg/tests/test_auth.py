# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for auth in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=protected-access

import unittest
import pytest
import prestodb

import thriftpy2 as thriftpy
from okera import context
from okera.tests import pycerebro_test_common as common

#
# NOTE: this test suite uses the fact that enable_token_auth will treat
# a string that has a period in it as a JWT/OkeraToken, and any other string
# as if it was the username (for an unauthed server). Since the test runs
# against an unauthed server, a JWT/OkeraToken will always fail, causing
# us to go through the retry logic.
#

# {
#   "sub": "user1",
#   "claim2": "user2",
#   "claim3": "user3"
# }
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSI' + \
        'sImNsYWltMiI6InVzZXIyIiwiY2xhaW0zIjoidXNlcjMifQ.4QIs75Pm' + \
        'B_aRtTVebR97CH9EugdNGj9-UAppkxDq73U'

def jwt_token_fn():
    return TOKEN

# Global variable for attempts
attempts = 0

def bad_then_good_func():
    global attempts
    token = None
    if attempts == 0:
        token = "foo.bar"
    else:
        token = "foo"
    attempts += 1
    return token

def bad_twice_then_good_func():
    global attempts
    token = None
    if attempts < 2:
        token = "foo.bar"
    else:
        # should never be called
        raise Exception()
    attempts += 1
    return token

def good_then_bad_func():
    global attempts
    token = None
    if attempts == 0:
        token = "foo"
    else:
        # this should never be called
        raise Exception()
    attempts += 1
    return token

def always_bad():
    return "foo.bar"

class AuthTest(unittest.TestCase):
    @staticmethod
    def _reset_attempts():
        global attempts
        attempts = 0

    def setUp(self):
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        AuthTest._reset_attempts()

    def test_token_func_basic(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_func=bad_then_good_func)
        with common.get_planner(ctx) as conn:
            results = conn.scan_as_json('okera_sample.whoami')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'foo')

    def test_token_func_no_failure(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_func=bad_then_good_func)
        with common.get_planner(ctx) as conn:
            results = conn.scan_as_json('okera_sample.whoami')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'foo')

    def test_token_func_and_token_str(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_func=always_bad, token_str='foo')
        with common.get_planner(ctx) as conn:
            results = conn.scan_as_json('okera_sample.whoami')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'foo')

    def test_token_func_never_succeed(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_func=always_bad)
        with pytest.raises(thriftpy.transport.TTransportException):
            with common.get_planner(ctx):
                # we should never get here
                raise Exception()

    def test_token_func_retry_once_still_fail(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_func=bad_twice_then_good_func)
        with pytest.raises(thriftpy.transport.TTransportException):
            with common.get_planner(ctx):
                # we should never get here
                raise Exception()

    def test_token_func_non_picklable(self):
        def fn():
            return "foo"

        ctx = context()
        with pytest.raises(ValueError):
            ctx.enable_token_auth(token_func=fn)

    def test_token_user_extract(self):

        ctx = context()
        ctx.enable_token_auth(TOKEN)
        assert ctx._get_user() == 'user1'

        ctx.enable_token_auth(TOKEN, user_claims=['claim2'])
        assert ctx._get_user() == 'user2'

        ctx.enable_token_auth(TOKEN, user_claims=['nonexistent', 'claim2'])
        assert ctx._get_user() == 'user2'

        ctx.enable_token_auth(TOKEN, user_claims=['claim3', 'claim2'])
        assert ctx._get_user() == 'user3'

        ctx.enable_token_auth(TOKEN, user_claims=['nonexistent1', 'nonexistent2'])
        assert ctx._get_user() == 'user1'

        ctx.enable_token_auth(TOKEN, user_claims=[])
        assert ctx._get_user() == 'user1'

        # It's hard to test the internal logic for re-fetching
        # tokens when they are JWTs since currently Okera tests
        # run in un-authed mode. Due to that, we use the internal
        # functions to verify the logic is correct.

        ctx.enable_token_auth(token_func=jwt_token_fn, user_claims=['claim2'])
        assert ctx._get_user() == 'user2'
        ctx._generate_token()
        assert ctx._get_user() == 'user2'

    def test_presto_token_func_basic(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx, dialect='presto') as conn:
            ctx.enable_token_auth(token_func=bad_then_good_func, user='foo')
            results = conn.scan_as_json('select * from okera_sample.whoami', dialect='presto')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'foo')

    def test_presto_token_func_and_token_str(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx, dialect='presto') as conn:
            ctx.enable_token_auth(token_func=always_bad, token_str='foo')
            results = conn.scan_as_json('select * from okera_sample.whoami', dialect='presto')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['user'], 'foo')

    def test_presto_token_func_never_succeed(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx, dialect='presto') as conn:
            ctx.enable_token_auth(token_func=always_bad, user='foo')
            with pytest.raises(prestodb.exceptions.DatabaseError):
                results = conn.scan_as_json('select * from okera_sample.whoami', dialect='presto')
                # we should never get here
                raise Exception()

    def test_presto_token_func_retry_once_still_fail(self):
        ctx = common.get_test_context()
        with common.get_planner(ctx, dialect='presto') as conn:
            ctx.enable_token_auth(token_func=bad_twice_then_good_func, user='foo')
            with pytest.raises(prestodb.exceptions.DatabaseError):
                results = conn.scan_as_json('select * from okera_sample.whoami', dialect='presto')
                # we should never get here
                raise Exception()
