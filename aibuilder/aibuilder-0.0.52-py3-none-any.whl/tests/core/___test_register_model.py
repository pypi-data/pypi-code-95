import os
from datetime import datetime

import pytest
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.webservice import Webservice

from aibuilder.common.utils import Credentials
from aibuilder.core.environment import Environment

_ENVIRONMENT_NAME = 'byomcrew07'

interactive_auth = InteractiveLoginAuthentication(force=True)

ws = Workspace.get(name="byom-test-pme", subscription_id="2b1fe663-ced0-489b-93be-c0e0bc560d74",
                   resource_group="BYOM-Test-PME", auth=interactive_auth)

print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')

service = Webservice(ws, name="pneumonia-secure-pme-3")


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")


@pytest.fixture
def sample_api_spec(test_data_dir):
    return os.path.join(test_data_dir, "test_api_spec_heart_disease.json")


@pytest.fixture
def username_password():
    return Credentials(username="aibbyomtestuser@perapptest1.onmicrosoft.com", password="byomTesting@123")


def test_register_model(username_password):
    env = Environment.get(environment_name=_ENVIRONMENT_NAME, credentials=username_password)

    response = env.register_model(model_name=f"test-connection-pneumonia-3-18",
                                  connection=service,
                                  override=True)

    assert response
