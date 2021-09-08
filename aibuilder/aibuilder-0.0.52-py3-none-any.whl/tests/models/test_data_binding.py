#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
import os

import pytest

from aibuilder.models.aib_binding import AIBBinding, AIBTableBinding, AIBDataType
from aibuilder.models.exceptions import DataBindingValidationException


@pytest.fixture
def sample_data_binding(test_data_dir):
    with open(os.path.join(test_data_dir, "sample_binding.json"), "r") as f:
        return json.loads(f.read())


@pytest.fixture
def output_column_types():
    return {
        "model_output_1": AIBDataType.boolean,
        "model_output_2": AIBDataType.decimal,
        "model_output_3": AIBDataType.string
    }


def sample_input_binding():
    return AIBTableBinding(table_name="input_table", column_bindings={
        "model_param_1": "input_column_1",
        "model_param_2": "input_column_2",
        "model_param_3": "input_column_3"
    })


def sample_output_binding():
    return AIBTableBinding(table_name="output_table", column_bindings={
        "model_output_1": "output_column_1",
        "model_output_2": "output_column_2",
        "model_output_3": "output_column_2"
    })


def sample_spec_attribute(name, aib_data_type):
    return {"specificationName": name, "displayName": name,
            "requiredLevel": "Recommended", "dataType": aib_data_type}


@pytest.mark.parametrize("table_name, column_bindings, raises_exception", {
    (None, None, True),
    ("table_name", None, True),
    (None, '{"model_output_1": "data_verse_column_1"}', True),
    ("data_verse_table", '{"model_output_1": "data_verse_column_1"}', False),
    ("data_verse_table_1", '{"model_output_1": "data_verse_column_1", "model_output_2": "data_verse_column_2"}', False)
})
def test_table_binding_initialization(table_name, column_bindings, raises_exception):
    if raises_exception:
        with pytest.raises(TypeError):
            AIBTableBinding(table_name=table_name, column_bindings=json.loads(column_bindings))
    else:
        table_binding = AIBTableBinding(table_name=table_name, column_bindings=json.loads(column_bindings))

        assert isinstance(table_binding, AIBTableBinding)
        assert table_binding.table_name == table_name
        assert table_binding.column_bindings == json.loads(column_bindings)


@pytest.mark.parametrize("input_binding, output_binding, raises_exception", [
    (None, None, True),
    (sample_input_binding(), None, True),
    (None, sample_output_binding(), True),
    (sample_input_binding(), sample_output_binding(), False)
])
def test_data_binding_initialization(input_binding, output_binding, raises_exception, output_column_types,
                                     sample_data_binding):
    if raises_exception:
        with pytest.raises(ValueError):
            AIBBinding(input_binding=input_binding, output_binding=output_binding)
    else:
        aib_binding = AIBBinding(input_binding=input_binding, output_binding=output_binding)

        assert isinstance(aib_binding, AIBBinding)
        assert aib_binding._input_binding == input_binding
        assert aib_binding._output_binding == output_binding
        assert aib_binding._specification == {}
        assert aib_binding._binding is None

        assert aib_binding.set_output_column_types(output_column_types) is None  # Doesn't raise exception

        assert isinstance(aib_binding.binding, str)
        assert json.loads(aib_binding.binding) == sample_data_binding


@pytest.mark.parametrize("input_specification, expected_result", [
    ({"schemaVersion": 2, "input": {"attributes": []}, "output": {"attributes": []}}, True),
    ({"schemaVersion": 2, "input": {"attributes": [sample_spec_attribute("test", "Double")]},
      "output": {"attributes": [sample_spec_attribute("image", "Image")]}}, True),
    ({"schemaVersion": 2, "input": {"attributes": [sample_spec_attribute("image", "Image")]},
      "output": {"attributes": [sample_spec_attribute("test", "Double")]}}, False),
    ({"schemaVersion": 2, "input": {"attributes": [sample_spec_attribute("image", "Image"),
                                                   sample_spec_attribute("test_image", "Image")]},
      "output": {"attributes": [sample_spec_attribute("test", "Double")]}}, False),
])
def test_data_binding_validate(input_specification, expected_result):
    aib_binding = AIBBinding(input_binding=sample_input_binding(), output_binding=sample_output_binding())

    assert isinstance(aib_binding, AIBBinding)
    if expected_result:
        assert aib_binding._validate(aib_data_specification=json.dumps(input_specification)) is expected_result
    else:
        with pytest.raises(DataBindingValidationException):
            aib_binding._validate(aib_data_specification=json.dumps(input_specification))
