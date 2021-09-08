#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from aibuilder.models.helpers.data_specification import DataSpecification
import json
import pytest
from unittest import mock


@pytest.mark.parametrize("inputs, outputs, expected_data_spec", [
    ({}, {}, {"schemaVersion": 2, "input": {"attributes": []}, "output": {"attributes": []}}),
])
def test_data_specification(inputs, outputs, expected_data_spec):
    data_spec = DataSpecification.create_data_specification(inputs=inputs, outputs=outputs)

    assert isinstance(data_spec, str)
    data_spec_dict = json.loads(data_spec)
    assert data_spec_dict == expected_data_spec

    # validates that generate data spec returned value is used in data spec object
    with mock.patch.object(DataSpecification, "generate_data_spec", return_value="foobar"):
        data_spec = DataSpecification.create_data_specification(inputs=inputs, outputs=outputs)
        assert isinstance(data_spec, str)
        data_spec_dict = json.loads(data_spec)
        assert data_spec_dict["input"]["attributes"] == "foobar"
        assert data_spec_dict["output"]["attributes"] == "foobar"


@pytest.mark.parametrize("data, default_value", [
    ({}, None),
    ({}, "String"),
    ({"test": {"format": "double", "type": "number"}}, "String"),
    ({"image": {"format": "string", "type": "string"}}, "Image"),
    ({"__image": {"format": "string", "type": "string"}}, "Image"),
    ({"IMAGE": {"format": "string", "type": "string"}}, "Image"),
    ({"predict_imagE": {"format": "double", "type": "number"}}, "Image"),
    ({"test": {"format": "double", "type": "number"}, "foo": {"format": "foo", "type": "foobar"}}, "String"),
])
def test_generate_data_spec(data, default_value):
    with mock.patch.object(DataSpecification, "get_spec_data_type", return_value="foobar"):
        attributes = DataSpecification.generate_data_spec(data=data, default_data_type=default_value)

        assert isinstance(attributes, list)
        assert len(attributes) == len(data)

        for i in range(len(attributes)):
            attr = attributes[i]
            assert "specificationName" in attr
            assert "displayName" in attr
            assert "requiredLevel" in attr
            assert "dataType" in attr

            assert attr["specificationName"] in data


@pytest.mark.parametrize("data_type, default_value, expected_result", [
    ({"format": "double", "type": "number"}, None, "Double"),
    ({"format": "double", "type": "number"}, "String", "Double"),
    ({"format": "foobar", "type": "foobar"}, "String", "String"),
    ({"format": "foobar", "type": "foobar"}, None, None),
    ({"format": "int64", "type": "int64"}, None, "Integer"),
    ({"format": "int64", "type": "number"}, None, "Double"),
    ({"type": "bool"}, None, "Boolean"),
    ({"type": "boolean"}, None, "Boolean"),
    ({"format": "string", "type": "string"}, None, "String"),
])
def test_get_spec_data_type(data_type, default_value, expected_result):
    if expected_result is None:
        with pytest.raises(ValueError):
            DataSpecification.get_spec_data_type(open_api_data_type=data_type, default_data_type=default_value)
    else:
        result = DataSpecification.get_spec_data_type(open_api_data_type=data_type, default_data_type=default_value)
        assert result == expected_result
