#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from enum import Enum


class _AIBModelType(Enum):
    """ML Model type to be used to select the template"""
    generic_prediction = "generic_prediction"
    object_detection = "object_detection"


class ModelClientResponseStatus(Enum):
    """Model host operation output status type"""
    success = "success"
    failure = "failure"


class OpenAPISpecificationConstants(Enum):
    """Open API Specification constants"""
    schemes = "schemes"
    host = "host"
    base_path = "basePath"
    paths = "paths"
    post = "post"
    parameters = "parameters"

    definitions = "definitions"
    service_input = "ServiceInput"
    service_output = "ServiceOutput"
    properties = "properties"
    data = "data"
    items = "items"


class _AIBExecutionContextConstants(Enum):
    """Constants used to create BYOM Execution Context"""
    predict_url = "predictUrl"
    method = "method"
    post = "POST"
    request_headers = "requestHeaders"
    request_body_key = "requestBodyKey"
    content_type = "Content-Type"
    application_json = "application/json"
    policy = "policy"
    batch_size = "batchSize"
    name = "name"
    byom_execution_details = "byomExecutionDetails"
    display_name = "displayName"
    description = "description"
    default_value = "defaultValue"
    type = "type"
    string = "Edm.String"
    use_connectors = "useConnectors"
    model_run_data_specification = "ModelRunDataSpecification"
    prediction_policy = "policy"
    prediction_timeout = "predictionTimeout"


class AIBBindingConstants(Enum):
    specification_name = "specificationName"
    schema_name = "schemaName"
    display_name = "displayName"
    data_type = "dataType"
    schema_version_key = "schemaVersion"
    schema_version = 2
    schema_input = "input"
    schema_output = "output"
    attributes = "attributes"


class _AIBModelClientConstants(Enum):
    batch_size = "batch_size"
    prediction_timeout_args = "prediction_timeout"
    default_prediction_timeout_in_seconds = 5
    max_prediction_timeout_in_seconds = 20
    connector_name_random_hex_length = 4
    connector_name_max_length = 30
