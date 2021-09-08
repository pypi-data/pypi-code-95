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
from aibuilder.common.paconnector.connector.create_custom_connector import create_custom_connector


@pytest.fixture
def d365_connector():
    return D365Connector()


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../test_data")


@pytest.fixture
def payload(test_data_dir):
    filepath = os.path.join(test_data_dir, "connectors_payload.json")
    with open(filepath, "r") as f:
        swagger = json.loads(f.read())
    return swagger


@mock.patch("aibuilder.common.paconnector.connector.create_custom_connector._create_get_connector")
@mock.patch("aibuilder.common.paconnector.connector.resource_provider.PowerAppsRP.get_from_settings",
            return_value="Powerapps_rp")
@mock.patch("aibuilder.common.auth.d365_connector.D365Connector.credentials_manager.get_token")
@mock.patch.object(D365Connector, "credentials_manager", return_value={})
def test_create_custom_connector(mocked_d365connector, token, mock_powerapps_rp, mock_connector, payload,
                                 d365_connector):
    token.return_value = {'accessToken': "sample_arm_token_foobar"}
    mock_connector.return_value = {
        'name': "new_connector",
        'id': "new_id",
        'type': 'Microsoft.PowerApps/apis',
        'properties': {
            'foo': 'bar',
            'baz': 'abc'
        }
    }
    response = create_custom_connector(payload=payload, powerapps_url=None, powerapps_basepath=None,
                                       powerapps_api_version=None)
    assert response['name'] == "new_connector"
    assert list(response.keys()) == ["name", "id", "type", "properties"]
