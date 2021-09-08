#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import os
import string
from unittest import mock

import pytest
import requests

from aibuilder.common.paconnector.connector.powerapps_custom_connector import PowerAppsCustomConnector
from aibuilder.core.model_connection import LocalFileConnection
from aibuilder.models.aib_model_client import AIBModelClient
from aibuilder.models.constants import _AIBModelType
from aibuilder.models.helpers.ai_model import AiModel
from aibuilder.models.helpers.data_specification import DataSpecification
from aibuilder.models.helpers.run_configuration import RunConfiguration
from aibuilder.models.helpers.train_configuration import TrainConfiguration
from aibuilder.models.model_client_response import ModelClientResponse, ModelClientResponseStatus
from aibuilder.models.open_api_specification import _OpenAPISpecification


@pytest.fixture
def sample_api_spec(test_data_dir):
    return os.path.join(test_data_dir, "sample_api_specification.json")


@mock.patch.object(RunConfiguration, "update", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(RunConfiguration, "create", return_value="run_config_create")
@mock.patch.object(TrainConfiguration, "update", return_value="train_update")
@mock.patch.object(TrainConfiguration, "create", return_value="train_create")
@mock.patch.object(TrainConfiguration, "retrieve", return_value={"msdyn_majoriterationnumber": 1})
@mock.patch.object(PowerAppsCustomConnector, "create_connection", return_value={"foo": "bar"})
@mock.patch.object(AIBModelClient, "_check_publish_status", return_value=True)
@mock.patch.object(AiModel, "schedule", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(AiModel, "unschedule", return_value=True)
@mock.patch.object(AiModel, "create", return_value="aimodel_create")
@mock.patch.object(AiModel, "retrieve", return_value=None)
@mock.patch.object(DataSpecification, "create_data_specification", return_value="data_spec")
@mock.patch.object(_OpenAPISpecification, "get_scoring_config", return_value={"test": "value"})
@mock.patch.object(_OpenAPISpecification, "get_api_specification_and_version", return_value=({}, ""))
@mock.patch.object(_OpenAPISpecification, "get_scoring_url", return_value="foobar.com")
@pytest.mark.parametrize("override", [True, False])
def test_model_create_method(mock_scoring_url, mock_api_spec, mock_scoring_config, mock_data_spec,
                             mock_ai_model_retrieve, mock_ai_model_create, mock_ai_model_unschedule,
                             mock_ai_model_schedule, mock_publish_status, mock_create_connection, mock_train_retrieve,
                             mock_train_create, mock_train_update, mock_run_create, mock_run_update, dummy_swagger_file,
                             override):
    """Validates create model method calls"""
    mock_run_update.return_value.status_code = 200
    mock_ai_model_schedule.return_value.status_code = 200

    response = AIBModelClient.create(model_name="test", org_url="http://foobar.com", token="token",
                                     model_connection=LocalFileConnection(dummy_swagger_file), data_binding=None,
                                     override=override,
                                     environment_name="env_1")

    assert isinstance(response, ModelClientResponse)
    assert response.status == ModelClientResponseStatus.success

    assert mock_scoring_url.call_count == 1
    assert mock_api_spec.call_count == 1
    assert mock_scoring_config.call_count == 1
    assert mock_data_spec.call_count == 1
    assert mock_ai_model_retrieve.call_count == 1  # AI model retrieve will be called first and then AI model create
    assert mock_ai_model_create.call_count == 1
    assert mock_ai_model_unschedule.call_count == override
    assert mock_ai_model_schedule.call_count == 1
    assert mock_publish_status.call_count == 1
    assert mock_create_connection.call_count == 1
    assert mock_train_retrieve.call_count == 1
    assert mock_train_create.call_count == 1
    assert mock_train_update.call_count == 1
    assert mock_run_create.call_count == 1
    assert mock_run_update.call_count == 1


@mock.patch.object(RunConfiguration, "update", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(RunConfiguration, "create", return_value="run_config_create")
@mock.patch.object(TrainConfiguration, "update", return_value="train_update")
@mock.patch.object(TrainConfiguration, "create", return_value="train_create")
@mock.patch.object(TrainConfiguration, "retrieve", return_value={"msdyn_majoriterationnumber": 1})
@mock.patch.object(PowerAppsCustomConnector, "create_connection", return_value={"foo": "bar"})
@mock.patch.object(AIBModelClient, "_check_publish_status", return_value=True)
@mock.patch.object(AiModel, "schedule", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(AiModel, "unschedule", return_value=True)
@mock.patch.object(AiModel, "create", return_value="aimodel_create")
@mock.patch.object(AiModel, "retrieve", return_value="aimodel_retrieve")
@mock.patch.object(DataSpecification, "create_data_specification", return_value="data_spec")
@mock.patch.object(_OpenAPISpecification, "get_scoring_config", return_value={"test": "value"})
@mock.patch.object(_OpenAPISpecification, "get_api_specification_and_version", return_value=({}, ""))
@mock.patch.object(_OpenAPISpecification, "get_scoring_url", return_value="foobar.com")
@pytest.mark.parametrize("override", [True])
def test_model_update_method(mock_scoring_url, mock_api_spec, mock_scoring_config, mock_data_spec,
                             mock_ai_model_retrieve, mock_ai_model_create, mock_ai_model_unschedule,
                             mock_ai_model_schedule, mock_publish_status, mock_create_connection, mock_train_retrieve,
                             mock_train_create, mock_train_update, mock_run_create, mock_run_update, dummy_swagger_file,
                             override):
    """Validates that AI Model create is not called"""
    mock_run_update.return_value.status_code = 200
    mock_ai_model_schedule.return_value.status_code = 200

    response = AIBModelClient.create(model_name="test", org_url="http://foobar.com", token="token",
                                     model_connection=LocalFileConnection(dummy_swagger_file), data_binding=None,
                                     override=override,
                                     environment_name="env_1")

    assert isinstance(response, ModelClientResponse)
    assert response.status == ModelClientResponseStatus.success

    assert mock_scoring_url.call_count == 1
    assert mock_api_spec.call_count == 1
    assert mock_scoring_config.call_count == 1
    assert mock_data_spec.call_count == 1
    assert mock_ai_model_retrieve.call_count == 1  # AI model retrieve will be called
    assert mock_ai_model_create.call_count == 0  # AI model create is not called
    assert mock_ai_model_unschedule.call_count == override
    assert mock_ai_model_schedule.call_count == 1
    assert mock_publish_status.call_count == 1
    assert mock_create_connection.call_count == 1
    assert mock_train_retrieve.call_count == 1
    assert mock_train_create.call_count == 1
    assert mock_train_update.call_count == 1
    assert mock_run_create.call_count == 1
    assert mock_run_update.call_count == 1


@mock.patch.object(RunConfiguration, "update", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(RunConfiguration, "create", return_value="run_config_create")
@mock.patch.object(TrainConfiguration, "update", return_value="train_update")
@mock.patch.object(TrainConfiguration, "create", return_value="train_create")
@mock.patch.object(TrainConfiguration, "retrieve", return_value={"msdyn_majoriterationnumber": 1})
@mock.patch.object(PowerAppsCustomConnector, "create_connection", return_value={"foo": "bar"})
@mock.patch.object(AIBModelClient, "_check_publish_status", return_value=True)
@mock.patch.object(AiModel, "schedule", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(AiModel, "unschedule", return_value=True)
@mock.patch.object(AiModel, "create", return_value="aimodel_create")
@mock.patch.object(AiModel, "retrieve", return_value=None)
@pytest.mark.parametrize("override", [True, False])
def test_model_create_method_using_spec(mock_ai_model_retrieve, mock_ai_model_create, mock_ai_model_unschedule,
                                        mock_ai_model_schedule, mock_publish_status, mock_create_connection,
                                        mock_train_retrieve, mock_train_create, mock_train_update, mock_run_create,
                                        mock_run_update, sample_api_spec, override):
    """Validates the method calls by validating method parameters"""
    mock_run_update.return_value.status_code = 200
    mock_ai_model_schedule.return_value.status_code = 200

    response = AIBModelClient.create(model_name="test", org_url="http://foobar.com", token="token",
                                     model_connection=LocalFileConnection(sample_api_spec), data_binding=None,
                                     override=override,
                                     environment_name="env_1")

    assert isinstance(response, ModelClientResponse)
    assert response.status == ModelClientResponseStatus.success

    assert mock_ai_model_retrieve.call_count == 1  # AI model retrieve will be called first and then AI model create
    assert mock_ai_model_create.call_count == 1
    assert mock_ai_model_unschedule.call_count == override
    assert mock_ai_model_schedule.call_count == 1
    assert mock_publish_status.call_count == 1
    assert mock_create_connection.call_count == 1
    assert mock_train_retrieve.call_count == 1
    assert mock_train_create.call_count == 1
    assert mock_train_update.call_count == 1
    assert mock_run_create.call_count == 1
    assert mock_run_update.call_count == 1

    assert mock_train_create.call_args[1].get("model_name") == "test"
    assert mock_train_create.call_args[1].get("model_id") == "aimodel_create"
    assert mock_train_create.call_args[1].get("model_type") == _AIBModelType.generic_prediction
    assert mock_train_create.call_args[1].get("scoring_config") == {
        'predictUrl': 'https://foobar.com/score',
        'requestBodyKey': 'data',
        'method': 'POST',
        'requestHeaders': {'Content-Type': 'application/json'},
        'foo': 'bar',
        'policy': {'predictionTimeout': 5}  # from create connection
    }

    assert mock_train_create.call_args[1].get("data_binding") is None

    assert mock_train_update.call_args[1] == {'train_config_id': 'train_create'}


@mock.patch.object(RunConfiguration, "update", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(RunConfiguration, "create", return_value="run_config_create")
@mock.patch.object(TrainConfiguration, "update", return_value="train_update")
@mock.patch.object(TrainConfiguration, "create", return_value="train_create")
@mock.patch.object(TrainConfiguration, "retrieve", return_value={"msdyn_majoriterationnumber": 1})
@mock.patch.object(PowerAppsCustomConnector, "create_connection", return_value={"foo": "bar"})
@mock.patch.object(AIBModelClient, "_check_publish_status", return_value=True)
@mock.patch.object(AiModel, "schedule", return_value=mock.MagicMock(requests.Response))
@mock.patch.object(AiModel, "unschedule", return_value=True)
@mock.patch.object(AiModel, "create", return_value="aimodel_create")
@mock.patch.object(AiModel, "retrieve", return_value=None)
@pytest.mark.parametrize("override", [True, False])
@pytest.mark.parametrize("prediction_timeout, is_valid_timeout", [(None, True), (1, True), (0.5, True), (10, True),
                                                                  (20, True), (21, False), (20.5, False), (30, False),
                                                                  ("foo", False)])
def test_prediction_timeout_parameter(mock_ai_model_retrieve, mock_ai_model_create, mock_ai_model_unschedule,
                                      mock_ai_model_schedule, mock_publish_status, mock_create_connection,
                                      mock_train_retrieve, mock_train_create, mock_train_update, mock_run_create,
                                      mock_run_update, sample_api_spec, override, prediction_timeout, is_valid_timeout):
    """Validates the method calls by validating method parameters"""
    mock_run_update.return_value.status_code = 200
    mock_ai_model_schedule.return_value.status_code = 200
    if is_valid_timeout:
        response = AIBModelClient.create(model_name="test", org_url="http://foobar.com", token="token",
                                         model_connection=LocalFileConnection(sample_api_spec), data_binding=None,
                                         override=override,
                                         environment_name="env_1", prediction_timeout=prediction_timeout)

        assert isinstance(response, ModelClientResponse)
        assert response.status == ModelClientResponseStatus.success

        assert mock_train_create.call_args[1].get("scoring_config") == {
            'predictUrl': 'https://foobar.com/score',
            'requestBodyKey': 'data',
            'method': 'POST',
            'requestHeaders': {'Content-Type': 'application/json'},
            'foo': 'bar',
            'policy': {'predictionTimeout': prediction_timeout if prediction_timeout else 5}
        }
    else:
        with pytest.raises(ValueError):
            AIBModelClient.create(model_name="test", org_url="http://foobar.com", token="token",
                                  model_connection=LocalFileConnection(sample_api_spec), data_binding=None,
                                  override=override,
                                  environment_name="env_1", prediction_timeout=prediction_timeout)


@pytest.mark.parametrize("prediction_timeout, is_valid_timeout", [(None, True), ("", False), ("foo", False),
                                                                  ("1", False), (0.5, True), (1.5, True), (15, True),
                                                                  (5, True), (20, True), (20.1, False), (25, False)])
def test_validate_prediction_timeout(prediction_timeout, is_valid_timeout):
    if is_valid_timeout:
        validated_prediction_timeout = AIBModelClient. \
            _validate_prediction_timeout(prediction_timeout=prediction_timeout)

        assert validated_prediction_timeout == prediction_timeout if prediction_timeout else 5
    else:
        with pytest.raises(ValueError):
            AIBModelClient._validate_prediction_timeout(prediction_timeout=prediction_timeout)


@mock.patch.object(TrainConfiguration, "retrieve", return_value={"msdyn_majoriterationnumber": 1})
@mock.patch.object(AIBModelClient, "_get_random_characters", return_value="0A1B2C")
@pytest.mark.parametrize("model_name, expected_connector_name", [
    ("test_model", "test_model-0A1B2C-v1"),
    ("test_model_name_with_lengthy_one", "test_model_name_with-0A1B2C-v1"),
    ("test_model_name_with", "test_model_name_with-0A1B2C-v1"),
    ("test_model_name_wit", "test_model_name_wit-0A1B2C-v1"),
    ("test_model_name_with-", "test_model_name_with-0A1B2C-v1")
])
def test_construct_connector_name_mocking_random_hex(mock_random_char, mock_train_config_retrieve, model_name,
                                                     expected_connector_name):
    train_config = TrainConfiguration(url="https://foobar.com", token="token")
    connector_name = AIBModelClient._construct_connector_name(model_name=model_name, train_config=train_config,
                                                              train_config_id="123")

    assert connector_name == expected_connector_name
    assert mock_random_char.call_count == 1
    assert mock_train_config_retrieve.call_count == 1


@mock.patch.object(TrainConfiguration, "retrieve", return_value={"msdyn_majoriterationnumber": 12})
@pytest.mark.parametrize("model_name, expected_connector_name_prefix, expected_connector_name_suffix, expected_length",
                         [
                             ("test_model", "test_model-", "-v12", 21),
                             ("test_model_name_with_lengthy_one", "test_model_name_wit-", "-v12", 30),
                             ("test_model_name_with", "test_model_name_wit-", "-v12", 30),
                             ("test_model_name_wit", "test_model_name_wit-", "-v12", 30),
                             ("test_model_name_with-", "test_model_name_wit-", "-v12", 30)
                         ])
def test_construct_connector_name(mock_train_config_retrieve, model_name,
                                  expected_connector_name_prefix, expected_connector_name_suffix, expected_length):
    train_config = TrainConfiguration(url="https://foobar.com", token="token")
    connector_name = AIBModelClient._construct_connector_name(model_name=model_name, train_config=train_config,
                                                              train_config_id="123")

    assert connector_name.startswith(expected_connector_name_prefix)
    assert connector_name.endswith(expected_connector_name_suffix)
    assert len(connector_name) == expected_length
    assert mock_train_config_retrieve.call_count == 1


def test_get_random_8_char_hex():
    allowed_characters = "ABCDEF" + string.digits

    def _is_valid_hex(s):
        return all(map(lambda x: x in allowed_characters, s))

    random_hex_list = [AIBModelClient._get_random_characters() for _ in range(10)]
    assert len(random_hex_list) == 10
    assert all(map(lambda x: len(x) == 6, random_hex_list))  # All 10 random hex are of length 6
    assert len(set(random_hex_list)) == 10  # All 10 random hex values are unique
    assert all(map(lambda x: _is_valid_hex(x), random_hex_list))


@pytest.mark.parametrize("status_code, expected_result", [(0, False), (1, False), (6, False), (7, True), (8, True)])
def test_check_publish_status(status_code, expected_result):
    with mock.patch.object(RunConfiguration, "retrieve", return_value={"statuscode": status_code}):
        run_config = RunConfiguration(url="https://foobar.com", token="token")

        publish_status = AIBModelClient._check_publish_status(run_config=run_config, run_config_id="123")

        assert publish_status is expected_result
