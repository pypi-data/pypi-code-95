#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
import os
import tempfile
from unittest import mock

import pytest
from azureml.core.webservice import AciWebservice

from aibuilder.core.model_connection import LocalFileConnection
from aibuilder.models.constants import OpenAPISpecificationConstants as api_constants
from aibuilder.models.exceptions import SchemaValidationException
from aibuilder.models.open_api_specification import _OpenAPISpecification


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")


@pytest.fixture
def sample_api_spec(test_data_dir):
    return os.path.join(test_data_dir, "sample_api_specification.json")


@pytest.fixture
def sample_aci_webservice_spec(test_data_dir):
    return os.path.join(test_data_dir, "sample_aci_webservice_specification.json")


def patch_swagger_json_file(swagger_file_path, request_label, temp_directory):
    with open(swagger_file_path, "r") as f:
        swagger = json.load(f)

    # Set new request_label
    service_input = swagger[api_constants.definitions.value][api_constants.service_input.value]

    service_input[api_constants.properties.value][request_label] = service_input[api_constants.properties.value] \
        .pop("data")
    service_input["example"][request_label] = service_input["example"].pop("data")

    # Update swagger file with request label
    swagger[api_constants.definitions.value][api_constants.service_input.value] = service_input

    new_swagger_file_path = os.path.join(temp_directory, os.path.basename(swagger_file_path))
    with open(new_swagger_file_path, "w") as f:
        json.dump(swagger, f)

    return new_swagger_file_path


def mock_webservice(swagger_uri=None):
    mock_webservice = mock.MagicMock(AciWebservice)
    mock_webservice.swagger_uri = swagger_uri
    mock_webservice.scoring_uri = "https://foobar.com/score"
    mock_webservice.get_keys.return_value = ("foo", "bar")
    return mock_webservice


def validate_api_spec(api_spec, request_label="data"):
    assert hasattr(api_spec, "_specification")
    assert isinstance(api_spec._specification, dict)

    assert hasattr(api_spec, "_specification_version")
    assert api_spec._specification_version == "2.0.0"

    assert hasattr(api_spec, "_request_label")
    assert api_spec._request_label == request_label

    assert hasattr(api_spec, "_scoring_url")
    assert isinstance(api_spec._scoring_url, str)
    assert api_spec._scoring_url == "https://foobar.com/score"

    input_attributes = api_spec.get_api_input_attributes()
    assert isinstance(input_attributes, dict)
    assert len(input_attributes) > 0

    output_attributes = api_spec.get_api_output_attributes()
    assert isinstance(output_attributes, dict)
    assert len(output_attributes) > 0


@pytest.mark.parametrize("spec_path, raises_exception", [
    (None, True),
    ("sample_api_specification.json", False)
])
def test_open_api_local_file_spec_init(spec_path, raises_exception, test_data_dir, dummy_swagger_file):
    if raises_exception:
        model_connection = LocalFileConnection(swagger_file_path=dummy_swagger_file)
        # Random path raises schema validation exception
        with pytest.raises(SchemaValidationException):
            _OpenAPISpecification(model_connection=model_connection)
    else:
        model_connection = LocalFileConnection(swagger_file_path=os.path.join(test_data_dir, spec_path))
        api_spec = _OpenAPISpecification(model_connection=model_connection)

        assert isinstance(api_spec, _OpenAPISpecification)
        validate_api_spec(api_spec=api_spec)


@pytest.mark.parametrize("raises_exception", [True, False])
def test_open_api_azureml_webservice_spec_init(sample_aci_webservice_spec, raises_exception):
    if raises_exception:
        webservice = mock_webservice(swagger_uri=None)
        with pytest.raises(SchemaValidationException):
            _OpenAPISpecification(model_connection=webservice)
    else:
        webservice = mock_webservice(swagger_uri=sample_aci_webservice_spec)
        api_spec = _OpenAPISpecification(model_connection=webservice)

        assert isinstance(api_spec, _OpenAPISpecification)

        validate_api_spec(api_spec=api_spec)


@pytest.mark.parametrize("request_label", ["foo", "foobar", "input", "data"])
@pytest.mark.parametrize("use_mock_webservice", [True, False])
def test_request_label(sample_api_spec, use_mock_webservice, request_label, root_dir):
    with tempfile.TemporaryDirectory(dir=root_dir) as temp_dir_name:
        swagger_file_path = patch_swagger_json_file(sample_api_spec, request_label, temp_dir_name)

        if use_mock_webservice:
            connection = mock_webservice(swagger_uri=swagger_file_path)
        else:
            connection = LocalFileConnection(swagger_file_path=swagger_file_path)

        api_spec = _OpenAPISpecification(model_connection=connection)

        assert isinstance(api_spec, _OpenAPISpecification)

        validate_api_spec(api_spec=api_spec, request_label=request_label)

        assert api_spec.get_request_label() == request_label

    assert not os.path.exists(temp_dir_name)


@pytest.mark.parametrize("use_mock_webservice, expected_primary_auth_key", [(True, "foo"), (False, None)])
def test_get_primary_authentication_key(sample_api_spec, use_mock_webservice, expected_primary_auth_key, root_dir):
    with tempfile.TemporaryDirectory(dir=root_dir) as temp_dir_name:
        swagger_file_path = patch_swagger_json_file(sample_api_spec, "data", temp_dir_name)

        if use_mock_webservice:
            connection = mock_webservice(swagger_uri=swagger_file_path)
        else:
            connection = LocalFileConnection(swagger_file_path=swagger_file_path)

        api_spec = _OpenAPISpecification(model_connection=connection)

        assert api_spec.get_primary_authentication_key() == expected_primary_auth_key


@pytest.mark.parametrize("use_mock_webservice, expected_scoring_uri_path", [(True, "/score"), (False, "/score")])
def test_get_scoring_uri_path(sample_api_spec, use_mock_webservice, expected_scoring_uri_path, root_dir):
    with tempfile.TemporaryDirectory(dir=root_dir) as temp_dir_name:
        swagger_file_path = patch_swagger_json_file(sample_api_spec, "data", temp_dir_name)

        if use_mock_webservice:
            connection = mock_webservice(swagger_uri=swagger_file_path)
        else:
            connection = LocalFileConnection(swagger_file_path=swagger_file_path)

        api_spec = _OpenAPISpecification(model_connection=connection)

        assert api_spec.get_scoring_uri_path() == expected_scoring_uri_path
