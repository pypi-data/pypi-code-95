#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
import os

import pytest

from aibuilder.common.paconnector.connector.connector_request_builder import CustomConnectorRequestBuilder
from aibuilder.common.paconnector.constants import CustomConnectorConstants as ccConstants


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../test_data")


@pytest.fixture
def payload(test_data_dir):
    filepath = os.path.join(test_data_dir, "sample_aci_service.json")
    with open(filepath, "r") as f:
        swagger = json.loads(f.read())
    return swagger


@pytest.mark.parametrize("environment_name, model_name, scoring_uri, primary_key", [
    ("env_name_123-4567-890", "PowerApps-Model-name", "http://foobar.com/score", "primary_key"),
    ("", "", "http://foobar.com/score", "primary_key"),
    ("env_name_123-4567-890", "PowerApps-Model-name", "http://foobar.com/score", None)
])
def test_connector_request_builder(environment_name, model_name, scoring_uri, primary_key, payload):
    assert len(payload["paths"]) == 2
    pa_connector_swagger_object = CustomConnectorRequestBuilder(api_specification=payload,
                                                                primary_key=primary_key,
                                                                scoring_uri=scoring_uri,
                                                                environment_name=environment_name,
                                                                model_name=model_name)
    assert list(pa_connector_swagger_object.description().keys()) == [ccConstants.description.value]
    assert list(pa_connector_swagger_object.openApiDefinition().keys()) == [ccConstants.openApiDefinition.value]
    assert len(pa_connector_swagger_object.openApiDefinition()[ccConstants.openApiDefinition.value]["paths"]) == 1
    assert list(pa_connector_swagger_object.policyTemplateInstances().keys()) == \
        [ccConstants.policyTemplateInstances.value]
    assert list(pa_connector_swagger_object.backendService().keys()) == [ccConstants.backendService.value]
    assert pa_connector_swagger_object.backendService()[ccConstants.backendService.value]["serviceUrl"] == \
        "http://foobar.com"
    assert list(pa_connector_swagger_object.displayName().keys()) == [ccConstants.displayName.value]
    assert pa_connector_swagger_object.displayName()[ccConstants.displayName.value] == model_name
    assert list(pa_connector_swagger_object.environment().keys()) == [ccConstants.environment.value]
    assert pa_connector_swagger_object.environment()[ccConstants.environment.value]["name"] == environment_name
    assert list(pa_connector_swagger_object.connectionParameters().keys()) == [ccConstants.connectionParameters.value]

    pa_swagger = pa_connector_swagger_object.buildSwagger()

    assert list(pa_swagger.keys()) == [ccConstants.properties.value]
    assert list(pa_swagger[ccConstants.properties.value].keys()) == [
        'description', 'openApiDefinition', 'policyTemplateInstances', 'backendService', 'environment', 'displayName',
        'connectionParameters', 'capabilities']

    if primary_key is None:
        assert pa_swagger[ccConstants.properties.value]["policyTemplateInstances"] is None
        assert pa_swagger[ccConstants.properties.value]["connectionParameters"] is None
    else:
        assert pa_swagger[ccConstants.properties.value]["policyTemplateInstances"]
        assert pa_swagger[ccConstants.properties.value]["connectionParameters"]
