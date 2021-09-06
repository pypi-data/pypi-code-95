# -*- coding: utf-8 -*-
import os

import pytest
from pip_services3_commons.config import ConfigParams

from pip_client_data_python.version1.EntitiesCommandableLambdaClientV1 import EntitiesCommandableLambdaClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture

# os.environ['AWS_LAMDBA_ARN'] = 'arn:aws:lambda:us-east-2:863271733649:function:pip-service-data-python-1-0-0-function'
# os.environ['AWS_ACCESS_ID'] = 'AKIA4R7YBJGIY5BYLMMB'
# os.environ['AWS_ACCESS_KEY'] = 'oq56KDGlEo1mS5veSTuVbTTjtjj7bD/Tf1p+qLiX'

AWS_LAMDBA_ARN = os.environ.get("AWS_LAMDBA_ARN") or ""
AWS_ACCESS_ID = os.environ.get("AWS_ACCESS_ID") or ""
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY") or ""


@pytest.mark.skipif(not AWS_LAMDBA_ARN and not AWS_ACCESS_ID and not AWS_ACCESS_KEY,
                    reason="Lambda credentials is not set")
class TestEntitiesCommandableLambdaClientV1:
    client: EntitiesCommandableLambdaClientV1
    fixture: EntitiesClientV1Fixture

    def setup_method(self):
        self.client = EntitiesCommandableLambdaClientV1()

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
