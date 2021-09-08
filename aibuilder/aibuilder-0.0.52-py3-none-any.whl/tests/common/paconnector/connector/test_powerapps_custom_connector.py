#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
import os
from unittest import mock

import pytest

from aibuilder.common.auth.d365_connector import D365Connector
from aibuilder.common.graph_client import _GraphClient
from aibuilder.common.paconnector.connector.connector_request_builder import CustomConnectorRequestBuilder
from aibuilder.common.paconnector.connector.exceptions import UpdateConnectorException, UpdateConnectionException, \
    ConnectionCreationException
from aibuilder.common.paconnector.connector.powerapps_custom_connector import PowerAppsCustomConnector
from aibuilder.common.paconnector.connector.resource_provider import PowerAppsRP
from aibuilder.models.open_api_specification import _OpenAPISpecification


@pytest.fixture
def d365_connector():
    return D365Connector()


@pytest.fixture
def powerapps_custom_connector():
    return PowerAppsCustomConnector(environment_name="test_env")


def test_data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../test_data")


def connector_swagger():
    file_path = os.path.join(test_data_dir(), "connectors_payload.json")
    with open(file_path, "r") as f:
        swagger = json.loads(f.read())
    return swagger


def create_connector_response():
    file_path = os.path.join(test_data_dir(), "create_connector_response.json")
    with open(file_path, "r") as f:
        connection_response = json.loads(f.read())
    return connection_response


def create_connection_response():
    file_path = os.path.join(test_data_dir(), "create_connection_response.json")
    with open(file_path, "r") as f:
        connection_response = json.loads(f.read())
    return connection_response


def raise_exception(message):
    raise Exception(message)


@mock.patch.object(PowerAppsCustomConnector, "_setup_connection", return_value=create_connection_response())
@mock.patch.object(PowerAppsCustomConnector, "_setup_connector", return_value=create_connector_response())
@mock.patch.object(CustomConnectorRequestBuilder, "buildSwagger", return_value=connector_swagger())
@pytest.mark.parametrize("environment_name, api_spec, model_name, model_id, score_path", [
    ("env1", mock.MagicMock(_OpenAPISpecification), "test_model", "model_id", "score"),
    ("env2", mock.MagicMock(_OpenAPISpecification), "foobar_model", "model_test_1", "model/predict"),
])
@pytest.mark.parametrize("override", [True, False])
def test_create_connection(mock_connector_request_builder, mock_create_connector, mock_create_connection,
                           environment_name, api_spec, model_name, model_id, score_path, override):
    scoring_url = f"http://foobar.com/{score_path}"

    api_spec._scoring_url = scoring_url
    api_spec.get_scoring_uri_path.return_value = score_path

    scoring_config = PowerAppsCustomConnector.create_connection(
        environment_name=environment_name,
        open_api_specification=api_spec,
        model_name=model_name,
        connection_name=model_id,
        override=override
    )

    assert mock_connector_request_builder.call_count == 1
    assert mock_create_connector.call_count == 1
    assert mock_create_connection.call_count == 1

    assert scoring_config == {
        "connection_url": f"https://primaryruntimeurl.com/connection_name/{score_path}",
        "predictUrl": f"https://primaryruntimeurl.com/connection_name/{score_path}",
        "modelPredictUrl": scoring_url,
        "connector_id": "/connector_id",
        "connector_creation_time": "2021-02-24T01:27:27.0524635Z",
        "connector_changed_time": "2021-02-24T01:27:27.0524635Z",
        "connector_primary_runtime_url": "https://primaryruntimeurl.com",
        "connection_id": "/connection_id",
        "connection_name": "connection_name",
        "connection_creation_time": "2021-02-24T02:09:29.6070391Z",
        "connection_last_modified": "2021-02-24T02:09:29.6070391Z",
        "connection_reference_logical_name": "connection_reference_logical_name_value"
    }


@mock.patch.object(PowerAppsCustomConnector, "_setup_connector", return_value=lambda x: raise_exception("test"))
@mock.patch.object(CustomConnectorRequestBuilder, "buildSwagger", return_value=connector_swagger())
@pytest.mark.parametrize("environment_name, api_spec, model_name, model_id, score_path", [
    ("env1", mock.MagicMock(_OpenAPISpecification), "test_model", "model_id", "score"),
    ("env2", mock.MagicMock(_OpenAPISpecification), "foobar_model", "model_test_1", "model/predict"),
])
@pytest.mark.parametrize("override", [True, False])
def test_create_connector_exception(mock_connector_request_builder, mock_create_connector,
                                    environment_name, api_spec, model_name, model_id, score_path, override):
    scoring_url = f"http://foobar.com/{score_path}"

    api_spec._scoring_url = scoring_url
    api_spec.get_scoring_uri_path.return_value = score_path

    with pytest.raises(Exception):
        PowerAppsCustomConnector.create_connection(
            environment_name=environment_name,
            open_api_specification=api_spec,
            model_name=model_name,
            connection_name=model_id,
            override=override
        )

    assert mock_connector_request_builder.call_count == 1
    assert mock_create_connector.call_count == 1


@mock.patch.object(PowerAppsCustomConnector, "_setup_connection", return_value=lambda x: raise_exception("test"))
@mock.patch.object(PowerAppsCustomConnector, "_setup_connector", return_value=create_connector_response())
@mock.patch.object(CustomConnectorRequestBuilder, "buildSwagger", return_value=connector_swagger())
@pytest.mark.parametrize("environment_name, api_spec, model_name, model_id, score_path", [
    ("env1", mock.MagicMock(_OpenAPISpecification), "test_model", "model_id", "score"),
    ("env2", mock.MagicMock(_OpenAPISpecification), "foobar_model", "model_test_1", "model/predict"),
])
@pytest.mark.parametrize("override", [True, False])
def test_create_connection_exception(mock_connector_request_builder, mock_create_connector, mock_create_connection,
                                     environment_name, api_spec, model_name, model_id, score_path, override):
    scoring_url = f"http://foobar.com/{score_path}"

    api_spec._scoring_url = scoring_url
    api_spec.get_scoring_uri_path.return_value = score_path

    with pytest.raises(Exception):
        PowerAppsCustomConnector.create_connection(
            environment_name=environment_name,
            open_api_specification=api_spec,
            model_name=model_name,
            connection_name=model_id,
            override=override
        )

    assert mock_connector_request_builder.call_count == 1
    assert mock_create_connector.call_count == 1
    assert mock_create_connection.call_count == 1


@pytest.mark.parametrize("api_key, environment_object, expected_connection_body", [
    (None, None, {"properties": {"connectionParameters": None}}),
    (None, {"foo": "bar"}, {"properties": {"connectionParameters": None, "environment": {"foo": "bar"}}}),
    ("api_key", None, {"properties": {"connectionParameters": {"apiKey": "api_key"}}}),
    ("api_key", {"foo": "bar"}, {"properties": {"connectionParameters": {"apiKey": "api_key"},
                                                "environment": {"foo": "bar"}}})
])
def test_construct_connection_request_body(api_key, environment_object, expected_connection_body):
    request_body = PowerAppsCustomConnector._construct_connection_request_body(api_key=api_key,
                                                                               environment_object=environment_object)

    assert request_body == expected_connection_body


@mock.patch.object(PowerAppsRP, "create_connector")
@mock.patch.object(PowerAppsRP, "update_connector")
@mock.patch.object(PowerAppsRP, "get_connector")
@mock.patch.object(PowerAppsCustomConnector, "_get_connector_id")
@pytest.mark.parametrize("create_connector_return_value", [create_connector_response()])
@pytest.mark.parametrize("update_connector_response", [False, True])
@pytest.mark.parametrize("get_connector_response", [None, create_connector_response()])
@pytest.mark.parametrize("get_connector_id_response", [None, "connector_id"])
@pytest.mark.parametrize("override", [True, False])
def test_setup_connector_get_connector(
        mock_get_connector_id, mock_get_connector, mock_update_connector, mock_create_connector,
        create_connector_return_value, update_connector_response, get_connector_response, get_connector_id_response,
        override, powerapps_custom_connector):
    """
    1. Test if get connector is called.
    2. If override is False, update connector shouldn't be called
    3. If override is True and get connector returns a value, update connector should be called
    4. If get connector returns None, Create connector should be called
    """

    mock_get_connector_id.return_value = get_connector_id_response
    mock_get_connector.return_value = get_connector_response
    mock_update_connector.return_value = update_connector_response
    mock_create_connector.return_value = create_connector_return_value

    if update_connector_response is False and (get_connector_response and override):
        with pytest.raises(UpdateConnectorException) as e:
            powerapps_custom_connector._setup_connector(connector_swagger=connector_swagger(), override=override)
            assert e.value.args[0] == "Connector update failed"
    else:
        powerapps_custom_connector._setup_connector(connector_swagger=connector_swagger(), override=override)

    assert mock_get_connector_id.call_count == 1
    assert mock_get_connector.call_count == 1

    update_call_count = 0
    if get_connector_response and override:
        update_call_count = 1
    assert mock_update_connector.call_count == update_call_count

    create_call_count = 0
    if get_connector_response is None:
        create_call_count = 1
    assert mock_create_connector.call_count == create_call_count


@mock.patch.object(PowerAppsCustomConnector, "_set_connection_permissions")
@mock.patch.object(PowerAppsRP, "create_connection")
@mock.patch.object(PowerAppsRP, "update_connection")
@mock.patch.object(PowerAppsRP, "get_connection")
@pytest.mark.parametrize("set_connection_permissions_response", [True, False])
@pytest.mark.parametrize("create_connection_return_value", [create_connection_response()])
@pytest.mark.parametrize("update_connection_response", [None, create_connection_response()])
@pytest.mark.parametrize("get_connection_response", [None, create_connection_response()])
@pytest.mark.parametrize("override", [True, False])
@pytest.mark.parametrize("api_key", [None, "api_key"])
def test_setup_connector_get_connection(
        mock_get_connection, mock_update_connection, mock_create_connection, mock_set_connection_permissions,
        create_connection_return_value, update_connection_response, get_connection_response,
        override, powerapps_custom_connector, api_key, set_connection_permissions_response):
    """
    1. Test if get connection is called.
    2. If override is False, update connection shouldn't be called
    3. If override is True and get connection returns a value, update connection should be called
    4. If get connection returns None, Create connection should be called
    """

    mock_get_connection.return_value = get_connection_response
    mock_update_connection.return_value = update_connection_response
    mock_create_connection.return_value = create_connection_return_value
    mock_set_connection_permissions.return_value = set_connection_permissions_response

    connection_name = "test-connection"
    connector_id = "connector-id"
    environment_object = {"env": "value"}

    exception_type = None
    if update_connection_response is None and get_connection_response and override:
        exception_type = UpdateConnectionException
    elif not set_connection_permissions_response:
        exception_type = ConnectionCreationException

    if exception_type:
        with pytest.raises(exception_type) as e:
            powerapps_custom_connector._setup_connection(
                connection_name=connection_name, api_key=api_key, connector_id=connector_id,
                environment_object=environment_object, override=override)
            assert e.value.args[0] == "Connection update failed"
    else:
        powerapps_custom_connector._setup_connection(
            connection_name=connection_name, api_key=api_key, connector_id=connector_id,
            environment_object=environment_object, override=override)

    assert mock_get_connection.call_count == 1

    update_call_count = 0
    if get_connection_response and override:
        update_call_count = 1
    assert mock_update_connection.call_count == update_call_count

    create_call_count = 0
    if get_connection_response is None:
        create_call_count = 1
    assert mock_create_connection.call_count == create_call_count


@mock.patch.object(PowerAppsRP, "update_connection_permissions")
@mock.patch.object(_GraphClient, "get_service_principal")
@mock.patch.object(D365Connector, "get_token_using_refresh_token")
@pytest.mark.parametrize("service_principal", [{"id": "service_principal_id"}, None])
@pytest.mark.parametrize("update_connection_permissions_status", [True, False])
def test_set_connection_permissions(mock_get_token_using_refresh_token, mock_get_service_principal,
                                    mock_update_connection_permissions, service_principal,
                                    update_connection_permissions_status, powerapps_custom_connector, token_dict):
    mock_get_token_using_refresh_token.return_value = token_dict
    mock_get_service_principal.return_value = service_principal
    mock_update_connection_permissions.return_value = update_connection_permissions_status

    if not service_principal:
        with pytest.raises(ValueError):
            powerapps_custom_connector._set_connection_permissions(connector_id="foobar_connector",
                                                                   connection_name="foobar_connection")
    else:
        status = powerapps_custom_connector._set_connection_permissions(connector_id="foobar_connector",
                                                                        connection_name="foobar_connection")
        assert status == update_connection_permissions_status
        assert mock_update_connection_permissions.call_args[1]["connector_id"] == "foobar_connector"
        assert mock_update_connection_permissions.call_args[1]["connection_name"] == "foobar_connection"
        assert mock_update_connection_permissions.call_args[1]["environment_id"] == "test_env"
        assert mock_update_connection_permissions.call_args[1]["service_principal_id"] == service_principal["id"]
