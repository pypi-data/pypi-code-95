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
from aibuilder.models.helpers.exceptions import RunConfigException
from aibuilder.models.helpers.run_configuration import RunConfiguration


def test_run_config_init():
    run_config = RunConfiguration(url="https://foobar.com", token="token")

    assert isinstance(run_config, RunConfiguration)
    assert run_config._url == "https://foobar.com"
    assert isinstance(run_config._request_builder, _RequestBuilder)


@mock.patch.object(RunConfiguration, "_get_connection_reference_id", return_value="con_ref_id")
@pytest.mark.parametrize("model_type", [_AIBModelType.generic_prediction, _AIBModelType.object_detection])
@pytest.mark.parametrize("batch_size", [None, 10, -1, 0])
def test_create_run_config(mock_run_config, model_type, batch_size):
    mock_binding = mock.MagicMock(AIBBinding)
    mock_binding.binding = "sample binding"

    with mock.patch('requests.request') as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.headers = {"OData-EntityId": "Entity(config_id)"}

        run_config = RunConfiguration(url="https://foobar.com", token="token")

        data_specification = json.dumps({'foo': 'bar'})
        config_id = run_config.create(model_type=model_type, model_name="test", model_id="123", train_config_id="321",
                                      scoring_config={"connection_reference_logical_name": "conn_ref_logical_name"},
                                      data_binding=mock_binding, data_specification=data_specification,
                                      batch_size=batch_size)

        assert config_id == "config_id"
        assert mock_request.call_args[0][0] == "POST"
        assert mock_request.call_args[0][1] == "https://foobar.com/api/data/v9.0/msdyn_aiconfigurations"

        request_body = mock_request.call_args[1]["json"]
        assert request_body["msdyn_name"] == "test Run Config"
        assert request_body["msdyn_databinding"] == "sample binding"

        if model_type == _AIBModelType.generic_prediction:
            custom_config = json.loads(request_body["msdyn_customconfiguration"])
            assert isinstance(custom_config, list)
            assert len(custom_config) == 1
            expected_custom_config = {"name": "byomExecutionDetails", "displayName": "Model execution details",
                                      "description": "Execution Details for Bring Your Own Mode",
                                      "defaultValue": '{"connection_reference_logical_name": "conn_ref_logical_name", '
                                                      '"ModelRunDataSpecification": {"foo": "bar"}}',
                                      "type": "Edm.String", "policy": {}}
            if batch_size and batch_size > 0:
                expected_custom_config["policy"]["batchSize"] = batch_size
            assert custom_config[0] == expected_custom_config


@pytest.mark.parametrize("model_name, model_id, model_type, connection_reference_id, train_config_id, scoring_config, "
                         "run_spec", [
                             ("test_model", "123", _AIBModelType.generic_prediction, "conn_ref_id", "321",
                              {"test": "config"}, "run_spec"),
                             ("test_model", "123", _AIBModelType.generic_prediction, "conn_ref_id", "321",
                              {"test": "config"}, "")
                         ])
@pytest.mark.parametrize("data_binding, expected_data_binding", [(None, ""), ("sample_binding", "sample_binding")])
def test_create_payload(model_name, model_id, model_type, connection_reference_id, train_config_id, scoring_config,
                        data_binding, expected_data_binding, run_spec):
    mock_binding = None
    if data_binding:
        mock_binding = mock.MagicMock(AIBBinding)
        mock_binding.binding = data_binding

    run_config = RunConfiguration(url="https://foobar.com", token="token")

    if not run_spec:
        with pytest.raises(ValueError):
            run_config._create_payload(model_name=model_name, model_id=model_id,
                                       model_type=model_type,
                                       connection_reference_id=connection_reference_id,
                                       train_config_id=train_config_id,
                                       scoring_config=scoring_config,
                                       data_binding=mock_binding,
                                       data_specification=run_spec, batch_size=None)
    else:
        payload = run_config._create_payload(model_name=model_name, model_id=model_id,
                                             model_type=model_type,
                                             connection_reference_id=connection_reference_id,
                                             train_config_id=train_config_id,
                                             scoring_config=scoring_config,
                                             data_binding=mock_binding,
                                             data_specification=json.dumps(run_spec), batch_size=None)

        assert isinstance(payload, dict)
        assert payload.get("msdyn_name") == f"{model_name} Run Config"
        assert payload.get("msdyn_AIModelId@odata.bind") == f"/msdyn_aimodels({model_id})"
        assert payload.get("msdyn_type") == 190690001
        assert payload.get("msdyn_TrainedModelAIConfigurationPareId@odata.bind") == \
            f"/msdyn_aiconfigurations({train_config_id})"
        assert payload.get("msdyn_ConnectionReferenceId@odata.bind") == \
            f"/connectionreferences({connection_reference_id})"

        assert payload.get("msdyn_databinding") == expected_data_binding

        custom_config = json.loads(payload.get("msdyn_customconfiguration", ""))
        assert len(custom_config) == 1
        assert custom_config[0]["name"] == "byomExecutionDetails"
        result_scoring_config = json.loads(custom_config[0]["defaultValue"])
        assert result_scoring_config == scoring_config


def test_update_payload():
    run_config = RunConfiguration(url="https://foobar.com", token="token")

    with mock.patch('requests.request') as mock_request:
        mock_request.return_value.status_code = 200

        response = run_config.update(run_config_id="123")

        assert response.status_code == 200
        assert mock_request.call_args[0][0] == "POST"
        assert mock_request.call_args[0][1] == \
            "https://foobar.com/api/data/v9.0/msdyn_aiconfigurations(123)/Microsoft.Dynamics.CRM.PublishAIConfiguration"
        assert mock_request.call_args[1]["json"] == {"version": "2.0"}


@pytest.mark.parametrize("expected_status_code", [200, 500])
def test_retrieve(expected_status_code):
    run_config = RunConfiguration(url="https://foobar.com", token="token")

    with mock.patch('requests.request') as mock_request:
        mock_request.return_value.status_code = expected_status_code
        mock_request.return_value.json.return_value = {"msdyn_aiconfigurationid": "123"}
        if expected_status_code != 200:
            with pytest.raises(RunConfigException):
                run_config.retrieve(run_config_id="123")
        else:
            train_config_body = run_config.retrieve(run_config_id="123")

            assert train_config_body == {"msdyn_aiconfigurationid": "123"}
            assert mock_request.call_args[0][0] == "GET"
            assert mock_request.call_args[0][1] == "https://foobar.com/api/data/v9.0/msdyn_aiconfigurations(123)"
