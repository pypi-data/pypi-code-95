# -*- coding: utf-8 -*-
import os

import pytest
from pip_services3_commons.config import ConfigParams

from pip_client_data_python.version1.EntitiesLambdaClientV1 import EntitiesLambdaClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture

AWS_LAMDBA_ARN = os.environ.get("AWS_LAMDBA_ARN") or ""
AWS_ACCESS_ID = os.environ.get("AWS_ACCESS_ID") or ""
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY") or ""


@pytest.mark.skipif(not AWS_LAMDBA_ARN and not AWS_ACCESS_ID and not AWS_ACCESS_KEY,
                    reason="Lambda credentials is not set")
class TestEntitiesLambdaClientV1:
    client: EntitiesLambdaClientV1
    fixture: EntitiesClientV1Fixture

    def setup_method(self):
        self.client = EntitiesLambdaClientV1()

        lambda_config = ConfigParams.from_tuples(
            "connection.protocol", "aws",
            "connection.arn", AWS_LAMDBA_ARN,
            "credential.access_id", AWS_ACCESS_ID,
            "credential.access_key", AWS_ACCESS_KEY,
            "options.connection_timeout", 30000
        )

        self.client.configure(lambda_config)

        self.fixture = EntitiesClientV1Fixture(self.client)

        self.client.open(None)

    def teardown_method(self):
        self.client.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
