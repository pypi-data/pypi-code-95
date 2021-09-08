#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from enum import Enum


class _AIBuilderTemplateIds(Enum):
    """AI Builder Template ids"""
    BYOM_TEMPLATE_ID = "0063176B-ED9E-4074-8B2C-5AA5C58EB87B"
    GP_TEMPLATE_ID = "ab77e20a-208b-46e4-bc19-b8e249b9a431"


class _AIModelConstants(Enum):
    """AI Builder data model constants"""
    MSDYN_AIMODELS = "msdyn_aimodels"
    MSDYN_NAME = "msdyn_name"
    MSDYN_TEMPLATE_ID = "msdyn_TemplateId"
    MSDYN_TEMPLATES = "msdyn_aitemplates"
    MSDYN_AIMODEL_ID = "msdyn_AIModelId"
    MSDYN_AICONFIGURATIONS = "msdyn_aiconfigurations"
    MSDYN_TYPE = "msdyn_type"
    MSDYN_DATA_BINDING = "msdyn_databinding"
    MSDYN_CUSTOM_CONFIGURATION = "msdyn_customconfiguration"
    MSDYN_RUN_CONFIG_ID = "msdyn_TrainedModelAIConfigurationPareId"
    MSDYN_DATA_SPECIFICATION = "msdyn_modelrundataspecification"
    MSDYN_CONNECTION_REFERENCE_ID = "msdyn_ConnectionReferenceId"
    MSDYN_MAJOR_ITERATION_NUMBER = "msdyn_majoriterationnumber"
    CONNECTION_REFERENCES = "connectionreferences"
    CONNECTION_REFERENCE_LOGICAL_NAME = "connectionreferencelogicalname"
    CONNECTION_REFERENCE_ID = "connectionreferenceid"
    RUN_CONFIG = "run_config"
    TRAIN_CONFIG = "train_config"
    PREDICT_IMMEDIATELY = "predictImmediately"
    STATUS_CODE = "statuscode"
    PUBLISHED_STATE = 7
    SCHEDULED_STATE = 8

    ODATA_BIND = "odata.bind"
    ODATA_ENTITY_ID = "OData-EntityId"

    FILTER = "$filter"
    EQUALS = "eq"
    VERSION = "version"
    VALUE = "value"

    TRAIN_CONFIG_TYPE = 190690000
    RUN_CONFIG_TYPE = 190690001
    TRAIN_ACTION = "Microsoft.Dynamics.CRM.Train"
    PUBLISH_ACTION = "Microsoft.Dynamics.CRM.PublishAIConfiguration"
    SCHEDULE_ACTION = "Microsoft.Dynamics.CRM.SchedulePrediction"
    UNSCHEDULE_ACTION = "Microsoft.Dynamics.CRM.UnschedulePrediction"
    UPDATE_API_VERSION = "2.0"
    SCHEDULE_API_VERSION = "1.0"
