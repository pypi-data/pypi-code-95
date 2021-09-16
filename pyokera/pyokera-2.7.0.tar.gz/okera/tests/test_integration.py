# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for auth in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=protected-access

import os
import tempfile

import unittest
import pytest

from okera.integration import domino
from okera.tests import pycerebro_test_common as common

class AuthTest(unittest.TestCase):
    def test_domino_basic(self):
        with pytest.raises(Exception) as excinfo:
            ctx = domino.context()
        assert 'Could not find Domino token environment variable' in str(excinfo.value)

        with pytest.raises(Exception) as excinfo:
            os.environ['DOMINO_TOKEN_FILE'] = '/does/not/exist'
            ctx = domino.context()
        assert 'Could not find Domino token file at' in str(excinfo.value)

        os.environ['DOMINO_TOKEN_FILE'] = os.path.join(
            os.environ.get('OKERA_HOME'),
            'integration', 'tokens', 'testuser_with_custom_claim.token'
        )
        ctx = domino.context()
        assert ctx._get_user() == 'testuser_preferred'

        with tempfile.NamedTemporaryFile() as fp:
            token_path = fp.name
            fp.write(b'customuser')
            fp.flush()

            os.environ['DOMINO_TOKEN_FILE'] = token_path
            ctx = domino.context()
            with common.get_planner(ctx) as conn:
                res = conn.scan_as_json('select * from okera_sample.whoami')
                assert len(res) == 1
                assert res[0]['user'] == 'customuser'

            fp.close()
