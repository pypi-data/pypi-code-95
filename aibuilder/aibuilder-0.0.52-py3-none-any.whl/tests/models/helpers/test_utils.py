#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
from unittest import mock

import pytest

from aibuilder.models.aib_binding import AIBBinding
from aibuilder.models.constants import _AIBModelType
from aibuilder.models.helpers.constants import _AIBuilderTemplateIds
from aibuilder.models.helpers.utils import get_object_id, get_model_config_and_data_binding, get_template_id


@pytest.mark.parametrize("input_str, output", [
    ("(test)", "test"),
    ("(123)", "123"),
    ("()", ""),
])
def test_get_object_id(input_str, output):
    assert get_object_id(input_str) == output


@pytest.mark.parametrize("model_type, data_binding, expected_data_binding", [
    (_AIBModelType.generic_prediction, None, ""),
    (_AIBModelType.generic_prediction, "test_binding", "test_binding"),
    (_AIBModelType.object_detection, None, ""),
    (_AIBModelType.object_detection, "sample binding", "sample binding"),
])
@pytest.mark.parametrize("data_specification", ["", {"foobar": "foobar"}])
@pytest.mark.parametrize("batch_size", [None, 10, -1, 0])
def test_get_model_config(model_type, data_binding, expected_data_binding, batch_size, data_specification):
    scoring_config = {"foo": "bar"}

    if data_binding is not None:
        mock_binding = mock.MagicMock(AIBBinding)
        mock_binding.binding = data_binding
    else:
        mock_binding = None

    data_binding, custom_config = get_model_config_and_data_binding(model_type=model_type,
                                                                    scoring_config=scoring_config,
                                                                    data_binding=mock_binding,
                                                                    data_specification=json.dumps(data_specification),
                                                                    batch_size=batch_size)

    assert data_binding == expected_data_binding
    if model_type == _AIBModelType.generic_prediction:
        expected_policy = {}
        if batch_size and batch_size > 0:
            expected_policy = {"batchSize": batch_size}
        assert len(custom_config) > 0
        config = json.loads(custom_config)
        assert config[0]["name"] == "byomExecutionDetails"
        if data_specification:
            scoring_config.update({"ModelRunDataSpecification": data_specification})
        assert json.loads(config[0]["defaultValue"]) == scoring_config
        assert config[0]["policy"] == expected_policy
    else:
        assert custom_config == ""


@pytest.mark.parametrize("model_type, raises_exception", [
    (_AIBModelType.generic_prediction, False),
    (_AIBModelType.object_detection, True)
])
def test_get_template_id(model_type, raises_exception):
    if raises_exception:
        with pytest.raises(TypeError):
            get_template_id(model_type=model_type)
    else:
        assert get_template_id(model_type=model_type) == _AIBuilderTemplateIds.BYOM_TEMPLATE_ID.value
