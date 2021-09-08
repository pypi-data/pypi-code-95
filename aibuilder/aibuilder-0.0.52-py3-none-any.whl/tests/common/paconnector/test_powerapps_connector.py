#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from unittest import mock

import pytest

from aibuilder.common.auth.d365_connector import D365Connector
from aibuilder.common.paconnector.constants import PowerAppsSettings
from aibuilder.common.paconnector.powerapps_connector import PowerAppsConnector
from aibuilder.common.paconnector.request_builder import _RequestBuilder
from aibuilder.common.utils import Credentials


@pytest.fixture
def username_password():
    return Credentials(username="user", password="placeholder_password")


class MockResponse:
    @staticmethod
    def json():
        test_json = {"value": [
            {
                "name": "123456789",
                "properties": {
                    "linkedEnvironmentMetadata": {
                        "friendlyName": "test_environment",
                        "instanceUrl": "https://testenv.crm10.dynamics.com/"
                    }
                }
            }
        ]}
        return test_json


@pytest.fixture
@mock.patch.object(D365Connector, "get_arm_token_with_username_and_password", return_value="foobar_token")
def pa_connector(mock_connector, username_password):
    return PowerAppsConnector(credentials=username_password)


@mock.patch.object(D365Connector, "get_arm_token_with_username_and_password", return_value="foobar_token")
def test_powerapps_connector_init(username_password):
    pa_connector = PowerAppsConnector(credentials=username_password)

    assert isinstance(pa_connector, PowerAppsConnector)
    assert pa_connector._endpoint == PowerAppsSettings.PROD_URL.value
    assert isinstance(pa_connector._d365connector, D365Connector)
    assert isinstance(pa_connector.d365connector, D365Connector)
    assert pa_connector._credentials.username == username_password.username
    assert pa_connector._credentials.password == username_password.password
    assert isinstance(pa_connector._request_builder, _RequestBuilder)


@mock.patch.object(D365Connector, "authenticate_with_device_code", return_value="foobar_token")
def test_powerapps_connector_init_with_device_token(d365_connector):
    pa_connector = PowerAppsConnector()

    assert isinstance(pa_connector, PowerAppsConnector)
    assert pa_connector._endpoint == PowerAppsSettings.PROD_URL.value
    assert isinstance(pa_connector._d365connector, D365Connector)
    assert isinstance(pa_connector.d365connector, D365Connector)
    assert pa_connector._credentials is None
    assert isinstance(pa_connector._request_builder, _RequestBuilder)


@mock.patch.object(_RequestBuilder, "construct_url", return_value="https://foobar.com")
@mock.patch.object(_RequestBuilder, "request", return_value=MockResponse())
def test_get_environment_url(mock_request, mock_construct_url, pa_connector):
    env_name, org_url = pa_connector.get_environment_name_and_url(environment_friendly_name="test_environment")

    assert org_url == "https://testenv.crm10.dynamics.com/"
    assert env_name == "123456789"
    assert mock_request.call_count == 1
    assert mock_construct_url.call_count == 1


@mock.patch.object(_RequestBuilder, "construct_url", return_value="https://foobar.com")
@mock.patch.object(_RequestBuilder, "request", return_value=MockResponse())
def test_get_environment_url_inavlid_env_name(mock_request, mock_construct_url, pa_connector):
    with pytest.raises(ValueError):
        pa_connector.get_environment_name_and_url(environment_friendly_name="test_environment_new")

        assert mock_request.call_count == 1
        assert mock_construct_url.call_count == 1
