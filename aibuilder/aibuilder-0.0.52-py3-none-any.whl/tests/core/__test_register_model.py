import os

import pytest
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.webservice import Webservice

from aibuilder.common.utils import Credentials
from aibuilder.core.environment import Environment

_ENVIRONMENT_NAME = 'byomcrew07'

interactive_auth = InteractiveLoginAuthentication(force=False)

ws = Workspace.get(name="byom-test-pme", subscription_id="2b1fe663-ced0-489b-93be-c0e0bc560d74",
                   resource_group="BYOM-Test-PME", auth=interactive_auth)

print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')

service = Webservice(ws, name="pneumonia-unsecure-pme-1")


# service = Webservice(ws, name="pneumonia-secure-pme-3")


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
    return True
    from aibuilder.models.aib_binding import AIBTableBinding, AIBBinding, AIBSpecification

    model_input_columns = {'administrative': 'aib_administrative',
                           'duration': 'aib_productrelated_duration',
                           'bouncerates': 'aib_bouncerates',
                           'browser': 'aib_browser',
                           'exitrates': 'aib_exitrates',
                           'informational': 'aib_informational',
                           'month': 'aib_month',
                           'name': 'aib_name',
                           'operatingsystems': 'aib_operatingsystems',
                           'pagevalues': 'aib_pagevalues',
                           'productrelated': 'aib_productrelated',
                           'region': 'aib_region',
                           'specialday': 'aib_specialday',
                           'traffictype': 'aib_traffictype',
                           'visitortype': 'aib_visitortype'}

    model_output_columns = {"pred_batch": "new_pred_batch", "score_batch": "new_score_batch"}
    # model_output_column_types = {"pred_batch": AIBDataType.boolean, "score_batch": AIBDataType.decimal}

    specification = {"pred_batch": AIBSpecification.prediction, "score_batch": AIBSpecification.likelihood}

    input_table = AIBTableBinding(table_name="aib_onlineshopperintention", column_bindings=model_input_columns)

    output_table = AIBTableBinding(table_name="aib_onlineshopperintention", column_bindings=model_output_columns)

    aib_binding = AIBBinding(input_binding=input_table, output_binding=output_table, specification=specification)
    # aib_binding.set_output_column_types(output_column_types=model_output_column_types)

    return aib_binding


from aibuilder.models.aib_binding import AIBTableBinding, AIBBinding

model_input_mapping = {"sex": "cr611_sex",
                       "cp": "cr611_cp",
                       "trestbps": "cr611_trestbps",
                       "chol": "cr611_chol",
                       "fbs": "cr611_fbs",
                       "restecg": "cr611_restecg",
                       "thalach": "cr611_thalach",
                       "exang": "cr611_exang",
                       "oldpeak": "cr611_oldpeak",
                       "slope": "cr611_slope",
                       "ca": "cr611_ca",
                       "thal": "cr611_thal"
                       }

model_output_mapping = {"prediction": "model_prediction"}

entity_name = "cr611_heart_disease"

input_table = AIBTableBinding(table_name="aib_onlineshopperintention", column_bindings=model_input_mapping)

output_table = AIBTableBinding(table_name="aib_onlineshopperintention", column_bindings=model_output_mapping)

aib_binding = AIBBinding(input_binding=input_table, output_binding=output_table)


def test_register_model(username_password, binding):
    env = Environment.get(environment_name=_ENVIRONMENT_NAME, credentials=username_password)

    response = env.register_model(model_name=f"test-pneumonia-unsecure-4-2",
                                  connection=service,
                                  override=True)

    assert response
