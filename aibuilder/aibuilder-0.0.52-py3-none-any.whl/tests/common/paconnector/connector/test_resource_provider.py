#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from unittest import mock

import pytest
import requests

from aibuilder.common.paconnector.connector.resource_provider import PowerAppsRP
from aibuilder.common.paconnector.constants import RequestBuilderConstants


@pytest.fixture
def powerapps_rp(request_builder):
    return PowerAppsRP(api_manager=request_builder)


@pytest.mark.parametrize("connector_id, connection_name, environment_id, payload", [
    ("connection_id", "connection_name1", "env", {"foo": "bar"}),
    ("test_connection_id", "test_connection", "foobar_env", {"foobar": ["test"]})
])
def test_create_connection(powerapps_rp, connector_id, connection_name, environment_id, payload):
    with mock.patch.object(powerapps_rp.api_manager, "request",
                           return_value=mock.MagicMock(requests.Response)) as mock_request:
        powerapps_rp.create_connection(connector_id=connector_id, connection_name=connection_name,
                                       environment_id=environment_id, payload=payload)

        expected_endpoint = f"http://foobar.com/base/{connector_id}/connections/{connection_name}" \
            f"?%24filter=environment%20eq%20%27{environment_id}%27&createConnectionReference=True"

        network_call = mock_request.call_args[1]
        assert network_call["method"] == RequestBuilderConstants.PUT
        assert network_call["endpoint"] == expected_endpoint
        assert network_call["payload"] == payload


@pytest.mark.parametrize("connector_id, connection_name, environment_id, is_valid", [
    ("connection_id", "connection_name1", "env", True),
    ("test_connection_id", "test_connection", "foobar_env", True),
    (None, "connection_name1", "env", False),
    ("connection_id", None, "env", False),
    ("connection_id", "connection_name1", None, False),
    (None, None, None, False)
])
@pytest.mark.parametrize("extra_path", ["", "test", "test/path"])
def test_construct_connection_endpoint(powerapps_rp, connector_id, connection_name, environment_id, is_valid,
                                       extra_path):
    if is_valid:
        endpoint = powerapps_rp._construct_connection_endpoint(connector_id=connector_id,
                                                               connection_name=connection_name,
                                                               environment_id=environment_id,
                                                               extra_path=extra_path)
        expected_endpoint = f"http://foobar.com/base/{connector_id}/connections/{connection_name}"
        if extra_path:
            expected_endpoint += f"/{extra_path}"
        expected_endpoint += f"?%24filter=environment%20eq%20%27{environment_id}%27"

        assert endpoint == expected_endpoint
    else:
        with pytest.raises(ValueError):
            powerapps_rp._construct_connection_endpoint(connector_id=connector_id, connection_name=connection_name,
                                                        environment_id=environment_id)


@pytest.mark.parametrize("connector_id", [None, "connector_id", "id_foo_bar"])
@pytest.mark.parametrize("connection_name", [None, "connection_name", "name_foo"])
@pytest.mark.parametrize("environment_id", [None, "environment_id", "foo_env"])
@pytest.mark.parametrize("is_valid", [False, True])
@pytest.mark.parametrize("service_principal_id", ["service_principal"])
def test_update_connection_permissions(powerapps_rp, connector_id, connection_name, environment_id, is_valid,
                                       service_principal_id):
    with mock.patch.object(powerapps_rp.api_manager, "request") as mock_request:
        mock_response = mock.MagicMock(requests.Response)
        mock_response.status_code = 200 if is_valid else 500

        mock_request.return_value = mock_response

        raises_exception = not (connector_id and connection_name and environment_id)

        if raises_exception:
            with pytest.raises(ValueError):
                powerapps_rp.update_connection_permissions(connector_id=connector_id,
                                                           connection_name=connection_name,
                                                           environment_id=environment_id,
                                                           service_principal_id=service_principal_id)
        else:
            update_status = powerapps_rp.update_connection_permissions(connector_id=connector_id,
                                                                       connection_name=connection_name,
                                                                       environment_id=environment_id,
                                                                       service_principal_id=service_principal_id)

            assert update_status == is_valid

            assert mock_request.call_args[1]["method"].value == "POST"
            assert mock_request.call_args[1]["endpoint"] == \
                f"http://foobar.com/base/{connector_id}/connections/{connection_name}/modifyPermissions" \
                f"?%24filter=environment%20eq%20%27{environment_id}%27&solutionId=fd140aaf-4df4-11dd-bd17-0019b9312238"
            assert mock_request.call_args[1]["payload"] == {
                'put': [
                    {
                        'properties': {
                            'roleName': 'CanViewWithShare', 'capabilities': [],
                            'principal': {'id': service_principal_id,
                                          'type': 'ServicePrincipal', 'tenantId': None}
                        }
                    }
                ],
                'delete': []
            }
