#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
from unittest import mock

import pytest

from aibuilder.common.paconnector.request_builder import _RequestBuilder
from aibuilder.models.aib_binding import AIBBinding
from aibuilder.models.constants import _AIBModelType
from aibuilder.models.helpers.exceptions import TrainConfigException
from aibuilder.models.helpers.train_configuration import TrainConfiguration


def test_train_config_init():
    train_config = TrainConfiguration(url="https://foobar.com", token="token")

    assert isinstance(train_config, TrainConfiguration)
    assert train_config._url == "https://foobar.com"
    assert isinstance(train_config._request_builder, _RequestBuilder)


@pytest.mark.parametrize("model_type", [_AIBModelType.generic_prediction, _AIBModelType.object_detection])
@pytest.mark.parametrize("batch_size", [None, 10, -1, 0])
def test_create_train_config(model_type, batch_size):
    mock_binding = mock.MagicMock(AIBBinding)
    mock_binding.binding = "sample binding"

    with mock.patch('requests.request') as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.headers = {"OData-EntityId": "Entity(config_id)"}

        train_config = TrainConfiguration(url="https://foobar.com", token="token")

        config_id = train_config.create(model_type=model_type, model_name="test", model_id="123", scoring_config={},
                                        data_binding=mock_binding, batch_size=batch_size)

        assert config_id == "config_id"
        assert mock_request.call_args[0][0] == "POST"
        assert mock_request.call_args[0][1] == "https://foobar.com/api/data/v9.0/msdyn_aiconfigurations"

        request_body = mock_request.call_args[1]["json"]
        assert request_body["msdyn_name"] == "test Train Config"
        if model_type == _AIBModelType.generic_prediction:
            custom_config = json.loads(request_body["msdyn_customconfiguration"])
            assert isinstance(custom_config, list)
            assert len(custom_config) == 1
            expected_custom_config = {"name": "byomExecutionDetails", "displayName": "Model execution details",
                                      "description": "Execution Details for Bring Your Own Mode",
                                      "defaultValue": "{}", "type": "Edm.String", "policy": {}}
            if batch_size and batch_size > 0:
                expected_custom_config["policy"]["batchSize"] = batch_size
            assert custom_config[0] == expected_custom_config


@pytest.mark.parametrize("model_name, model_id, model_type, scoring_config, data_specification", [
    ("test_model", "123", _AIBModelType.generic_prediction, {"test": "config"}, "sample_spec")
])
def test_create_payload(model_name, model_id, model_type, scoring_config, data_specification):
    mock_binding = mock.MagicMock(AIBBinding)
    mock_binding.binding = "sample binding"

    train_config = TrainConfiguration(url="https://foobar.com", token="token")

    payload = train_config._create_payload(model_name=model_name, model_id=model_id,
                                           model_type=model_type,
                                           scoring_config=scoring_config,
                                           data_binding=mock_binding)

    assert isinstance(payload, dict)
    assert payload.get("msdyn_name") == f"{model_name} Train Config"
    assert payload.get("msdyn_AIModelId@odata.bind") == f"/msdyn_aimodels({model_id})"
    assert payload.get("msdyn_type") == 190690000

    custom_config = json.loads(payload.get("msdyn_customconfiguration", ""))
    assert len(custom_config) == 1
    assert custom_config[0]["name"] == "byomExecutionDetails"
    result_scoring_config = json.loads(custom_config[0]["defaultValue"])
    assert list(result_scoring_config.keys()) == list(scoring_config.keys())
    assert list(result_scoring_config.values()) == list(scoring_config.values())


def test_update_payload():
    train_config = TrainConfiguration(url="https://foobar.com", token="token")

    with mock.patch('requests.request') as mock_request:
        mock_request.return_value.status_code = 200

        response = train_config.update(train_config_id="123")

        assert response.status_code == 200
        assert mock_request.call_args[0][0] == "POST"
        assert mock_request.call_args[0][1] == \
            "https://foobar.com/api/data/v9.0/msdyn_aiconfigurations(123)/Microsoft.Dynamics.CRM.Train"
        assert mock_request.call_args[1]["json"] == {"version": "2.0"}


@pytest.mark.parametrize("expected_status_code", [200, 500])
def test_retrieve(expected_status_code):
    train_config = TrainConfiguration(url="https://foobar.com", token="token")

    with mock.patch('requests.request') as mock_request:
        mock_request.return_value.status_code = expected_status_code
        mock_request.return_value.json.return_value = {"msdyn_aiconfigurationid": "123"}
        if expected_status_code != 200:
            with pytest.raises(TrainConfigException):
                train_config.retrieve(train_config_id="123")
        else:
            train_config_body = train_config.retrieve(train_config_id="123")

            assert train_config_body == {"msdyn_aiconfigurationid": "123"}
            assert mock_request.call_args[0][0] == "GET"
            assert mock_request.call_args[0][1] == "https://foobar.com/api/data/v9.0/msdyn_aiconfigurations(123)"
