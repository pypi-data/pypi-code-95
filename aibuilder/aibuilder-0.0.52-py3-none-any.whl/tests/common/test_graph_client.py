#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------


from unittest import mock

import pytest
import requests
from urllib3.exceptions import HTTPError

from aibuilder.common.graph_client import _GraphClient
from aibuilder.common.paconnector.request_builder import _RequestBuilder


@pytest.fixture
def graph_client(token_dict):
    return _GraphClient(graph_token=token_dict)


def test_graph_client_initialization(token_dict):
    graph_client = _GraphClient(graph_token=token_dict)

    assert isinstance(graph_client, _GraphClient)

    assert hasattr(graph_client, "_graph_token")
    assert graph_client._graph_token == token_dict

    assert isinstance(graph_client._request_builder, _RequestBuilder)
    assert graph_client._request_builder._base_path == "v1.0/"
    assert graph_client._request_builder._netloc == "graph.microsoft.com"


@mock.patch.object(_RequestBuilder, "request")
@pytest.mark.parametrize("response_status, json_response", [
    (200, {"value": []}),
    (200, {"value": [{"id": "service_principal"}]}),
    (200, {"value": [{"id": "service_principal"}, {"id": "service_principal_2"}]}),
    (200, {"value_": [{"id": "service_principal"}, {"id": "service_principal_2"}]}),
    (400, None),
    (500, None)
])
def test_get_service_principal(mock_request_builder, graph_client, response_status, json_response):
    response = mock.MagicMock(requests.Response)
    response.status_code = response_status
    response.json.return_value = json_response

    mock_request_builder.return_value = response

    if response_status != 200:
        with pytest.raises(HTTPError):
            graph_client.get_service_principal(application_id="test_app_id")
    else:
        if json_response.get("value") and len(json_response.get("value")):
            service_principal = graph_client.get_service_principal(application_id="test_app_id")

            assert service_principal == {"id": "service_principal"}
        else:
            with pytest.raises(ValueError):
                graph_client.get_service_principal(application_id="test_app_id")

    assert mock_request_builder.call_args[1]["method"].value == "GET"
    assert mock_request_builder.call_args[1]["endpoint"] == \
        f"https://graph.microsoft.com/v1.0/servicePrincipals?%24filter=appId%20eq%20%27test_app_id%27"


@pytest.mark.parametrize("service_principal", [
    {"id": "service_principal"},
    {"id": "service_principal_1"},
    {"id": "service_principal_2"},
    None
])
def test_get_service_principal_id(graph_client, service_principal):
    if service_principal is None:
        with pytest.raises(ValueError):
            graph_client.get_service_principal_id(service_principal=service_principal)
    else:
        service_principal_id = graph_client.get_service_principal_id(service_principal=service_principal)

        assert service_principal_id == service_principal["id"]


