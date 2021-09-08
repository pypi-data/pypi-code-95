#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
from typing import Optional

from aibuilder.models.aib_binding import AIBBinding
from aibuilder.models.constants import _AIBModelType, _AIBExecutionContextConstants
from aibuilder.models.helpers.constants import _AIBuilderTemplateIds, _AIModelConstants


def get_object_id(odata_entity_id):
    """
    Extracts AI Model/AI Configuration id from odata response

    :param odata_entity_id: specified odata entity
    :return: Parsed object id
    """
    start = odata_entity_id.find("(")
    end = odata_entity_id.find(")")
    return odata_entity_id[start + 1:end]


def get_model_config_and_data_binding(model_type: _AIBModelType, scoring_config: dict,
                                      data_binding: Optional[AIBBinding], batch_size: Optional[int] = None,
                                      data_specification: Optional[str] = None,
                                      config_type: _AIModelConstants = _AIModelConstants.TRAIN_CONFIG_TYPE) -> tuple:
    """
    Returns data binding and custom configuration strings for AI Configuration

    :param model_type: Type of ML Model represented using _AIBModelType enum
    :param scoring_config: Scoring configuration dictionary
    :param data_binding: Data binding json string
    :param batch_size: Number of prediction rows model endpoint can handle in one call
    :param data_specification: Model run data specification to be saved in execution context
    :param config_type: Config type parameter indicating Train or Run
    :return: Tuple of AI config data binding and custom config strings
    """
    binding = data_binding.binding if isinstance(data_binding, AIBBinding) else ""
    if model_type == _AIBModelType.generic_prediction:
        if config_type == _AIModelConstants.RUN_CONFIG_TYPE and not data_specification:
            raise ValueError("Data specification cannot be empty")

        execution_policy = {}
        if isinstance(batch_size, int) and batch_size > 0:
            execution_policy[_AIBExecutionContextConstants.batch_size.value] = batch_size
        if data_specification:
            scoring_config.update({
                _AIBExecutionContextConstants.model_run_data_specification.value: json.loads(data_specification)})
        custom_config = {
            _AIBExecutionContextConstants.name.value: _AIBExecutionContextConstants.byom_execution_details.value,
            _AIBExecutionContextConstants.display_name.value: "Model execution details",
            _AIBExecutionContextConstants.description.value: "Execution Details for Bring Your Own Mode",
            _AIBExecutionContextConstants.default_value.value: json.dumps(scoring_config),
            _AIBExecutionContextConstants.type.value: _AIBExecutionContextConstants.string.value,
            _AIBExecutionContextConstants.policy.value: execution_policy
        }
        custom_config = json.dumps([custom_config])
        return binding, custom_config
    return binding, ""


def get_template_id(model_type: _AIBModelType) -> str:
    """
    Gets template id from model_type

    :param model_type: AI Builder model type
    :return: template id
    """
    if model_type == _AIBModelType.generic_prediction:
        return _AIBuilderTemplateIds.BYOM_TEMPLATE_ID.value
    else:
        raise TypeError("Only generic prediction is supported")
