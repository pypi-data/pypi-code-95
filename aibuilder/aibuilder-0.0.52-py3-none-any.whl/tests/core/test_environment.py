#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from unittest import mock

import pytest

from aibuilder.common.auth.d365_connector import D365Connector
from aibuilder.common.utils import Credentials
from aibuilder.core.environment import Environment
from aibuilder.core.model_connection import LocalFileConnection
from aibuilder.models.aib_model_client import AIBModelClient
from aibuilder.models.helpers.exceptions import TemplateNotFoundException
from aibuilder.models.model_client_response import ModelClientResponse, ModelClientResponseStatus


@pytest.fixture
def d365_connector():
    return mock.MagicMock(D365Connector)


@pytest.fixture
def environment_name():
    return "123456789"


@pytest.fixture
def username_password():
    return Credentials(username="user", password="placeholder_password")


@pytest.mark.parametrize("environment_url, environment_name", [
    ("https://foobar.com", "123456789"),
    ("foo", "456789"),
    ("bar", "123123123")
])
def test_environment_class(environment_url, d365_connector, environment_name):
    env = Environment(environment_url=environment_url, d365_connector=d365_connector, environment_name=environment_name)

    assert isinstance(env, Environment)
    assert env._environment_url == environment_url
    assert env._d365connector == d365_connector
    assert env._environment_name == environment_name


def test_environment_init(d365_connector, username_password, environment_name):
    env = Environment(environment_url="https://foobar.com", d365_connector=d365_connector,
                      environment_name=environment_name)

    assert isinstance(env, Environment)
    assert hasattr(Environment, "get")
    assert hasattr(env, "get")
    assert hasattr(env, "register_model")


class MockPowerAppsConnector:
    def __init__(self):
        self._environment_url = "https://org1.powerapps.com"
        self._environment_name = "123456789"

    @property
    def d365connector(self):
        return ""

    def get_environment_name_and_url(self, environment_friendly_name):
        return self._environment_name, self._environment_url


@mock.patch.object(Environment, "_get_powerapps_connector", return_value=MockPowerAppsConnector())
def test_get_environment(username_password):

    env = Environment.get(environment_name="test_env", credentials=username_password)
    assert isinstance(env, Environment)
    assert env._environment_url == "https://org1.powerapps.com"
    assert env._environment_name == "123456789"


@mock.patch.object(Environment, "_check_pai_enabled", return_value=True)
@mock.patch.object(AIBModelClient, "create",
                   return_value=ModelClientResponse(status=ModelClientResponseStatus.success, model_id="123",
                                                    model_name="test_model"))
@pytest.mark.parametrize("batch_size, expected_batch_size", [
    (None, None),
    (123, 123),
    (-10, None),
    (-1000, None),
    (0, None),
    (100, 100),
    (10000, 10000),
    (20000, 10000)
])
@pytest.mark.parametrize("override", [True, False])
def test_register_model(mock_model_client, d365_connector, dummy_swagger_file, batch_size, expected_batch_size,
                        environment_name, override):
    env = Environment(environment_url="https://foobar.com", d365_connector=d365_connector,
                      environment_name=environment_name)
    result = env.register_model(model_name="test_model", connection=LocalFileConnection(dummy_swagger_file),
                                data_binding="binding", override=override, batch_size=batch_size)

    assert isinstance(result, ModelClientResponseStatus)
    assert result == ModelClientResponseStatus.success

    assert mock_model_client.call_count == 1
    assert mock_model_client.call_args[1]["model_name"] == "test_model"
    assert isinstance(mock_model_client.call_args[1]["model_connection"], LocalFileConnection)
    assert mock_model_client.call_args[1]["model_connection"].swagger_file_path == dummy_swagger_file
    assert mock_model_client.call_args[1]["org_url"] == "https://foobar.com"
    assert mock_model_client.call_args[1]["data_binding"] == "binding"
    assert mock_model_client.call_args[1]["batch_size"] == expected_batch_size
    assert mock_model_client.call_args[1]["override"] == override


@mock.patch.object(Environment, "_check_pai_enabled", return_value=False)
def test_register_model_fails_with_missing_byom_template(mock_pai_enabled_check, dummy_swagger_file):
    env = Environment(environment_url="https://foobar.com", d365_connector=d365_connector,
                      environment_name=environment_name)
    with pytest.raises(TemplateNotFoundException):
        env.register_model(model_name="test_model", connection=LocalFileConnection(dummy_swagger_file),
                           data_binding="binding", override=False, batch_size=10)


@pytest.mark.parametrize("batch_size_input, expected_output", [
    (None, None),
    (-1, None),
    (0, None),
    (10, 10),
    (10000, 10000),
    (20000, 10000),
])
def test_get_valid_batch_size(batch_size_input, expected_output):
    batch_size = Environment._get_valid_batch_size(batch_size=batch_size_input)

    assert batch_size == expected_output
