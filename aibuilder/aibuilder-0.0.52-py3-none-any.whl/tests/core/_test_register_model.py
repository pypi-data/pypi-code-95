import os
from datetime import datetime

import pytest
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.webservice import Webservice
from aibuilder.core.model_connection import LocalFileConnection

from aibuilder.common.utils import Credentials
from aibuilder.core.environment import Environment

from inference_schema.schema_decorators import input_schema, output_schema

# _ENVIRONMENT_NAME = "byom-test-user-role-can1"
# _ENVIRONMENT_NAME = 'test-byom-dev-01'
_ENVIRONMENT_NAME = 'byomdemo-eus-01'

interactive_auth = InteractiveLoginAuthentication(force=False)

ws = Workspace.get(name="byom_dev", subscription_id="402d1d46-9a5b-41c7-a8b1-a7cf7bdf638b",
                   resource_group="robhoopa-byom", auth=interactive_auth)

print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')

service = Webservice(ws, name='heart-disease-endpoint')


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")


@pytest.fixture
def sample_api_spec(test_data_dir):
    return os.path.join(test_data_dir, "test_api_spec_heart_disease.json")


@pytest.fixture
def username_password():
    return Credentials(username="Testuser@perapptest1.onmicrosoft.com", password="Testing@123")


@pytest.fixture
def binding():
    from aibuilder.models.aib_binding import AIBTableBinding, AIBBinding

    model_input_mapping = {"sex": "crf00_sex",
                           "cp": "crf00_cp",
                           "trestbps": "crf00_trestbps",
                           "chol": "crf00_chol",
                           "fbs": "crf00_fbs",
                           "restecg": "crf00_restecg",
                           "thalach": "crf00_thalach",
                           "exang": "crf00_exang",
                           "oldpeak": "crf00_oldpeak",
                           "slope": "crf00_slope",
                           "ca": "crf00_ca",
                           "thal": "crf00_thal"
                           }

    model_output_mapping = {"output": "model_prediction"}

    table_name = "crf00_heart_disease"

    input_table = AIBTableBinding(table_name=table_name, column_bindings=model_input_mapping)

    output_table = AIBTableBinding(table_name=table_name, column_bindings=model_output_mapping)

    aib_binding = AIBBinding(input_binding=input_table, output_binding=output_table)

    return aib_binding


def test_register_model(username_password, sample_api_spec, binding):
    env = Environment.get(environment_name=_ENVIRONMENT_NAME, credentials=username_password)
    response = env.register_model(model_name="v51_heart_disease_1",
                                  connection=service,
                                  # data_binding=binding,
                                  override=True)

    assert response
