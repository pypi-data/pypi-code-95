#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import logging
import random
import string
from typing import Optional, Union

import polling2
from azureml.core.webservice import Webservice

from aibuilder.common.paconnector.connector.powerapps_custom_connector import PowerAppsCustomConnector
from aibuilder.core.model_connection import ModelConnection
from aibuilder.models.aib_binding import AIBBinding
from aibuilder.models.constants import _AIBModelClientConstants, _AIBModelType
from aibuilder.models.helpers.ai_model import AiModel
from aibuilder.models.helpers.constants import _AIModelConstants
from aibuilder.models.helpers.data_specification import DataSpecification
from aibuilder.models.helpers.exceptions import ModelNotFoundException
from aibuilder.models.helpers.exceptions import RegistrationException
from aibuilder.models.helpers.run_configuration import RunConfiguration
from aibuilder.models.helpers.train_configuration import TrainConfiguration
from aibuilder.models.helpers.utils import get_template_id
from aibuilder.models.model_client_response import ModelClientResponse, ModelClientResponseStatus
from aibuilder.models.model_management_client import ModelManagementClient
from aibuilder.models.open_api_specification import _OpenAPISpecification

logger = logging.getLogger(__name__)


class AIBModelClient(ModelManagementClient):
    @classmethod
    def create(cls,
               model_name: str,
               org_url: str,
               model_connection: [ModelConnection, Webservice],
               data_binding: Optional[AIBBinding],
               token: str,
               environment_name: str,
               override: bool,
               model_type: _AIBModelType = _AIBModelType.generic_prediction,
               **kwargs) -> ModelClientResponse:
        """
        Create a model with using the model name

        :param model_name: Name of the model to be created on the hosting service
        :param org_url: Model host URL
        :param model_connection: Model connection object to retrieve open API swagger
        :param data_binding: Data Binding
        :param token: Bearer token
        :param environment_name: PowerApps environment id
        :param override: Update a registered model
        :param model_type: AI Builder model type
        :param kwargs: Additional key value parameters required to create a model
        :return: Returns a model host response object indicating the status of the operation
        """

        batch_size = kwargs.get(_AIBModelClientConstants.batch_size.value)

        api_specification = _OpenAPISpecification(model_connection=model_connection)

        prediction_timeout = AIBModelClient._validate_prediction_timeout(
            prediction_timeout=kwargs.get(_AIBModelClientConstants.prediction_timeout_args.value))

        scoring_config = api_specification.get_scoring_config(prediction_timeout=prediction_timeout,
                                                              batch_size=batch_size)
        model_template_id = get_template_id(model_type)

        ai_model = AiModel(url=org_url, token=token)
        train_config = TrainConfiguration(url=org_url, token=token)



        try:
            aib_data_specification = DataSpecification. \
                create_data_specification(inputs=api_specification.get_api_input_attributes(),
                                          outputs=api_specification.get_api_output_attributes())

            if data_binding:
                # Setting data binding output column types from open api swagger
                output_column_types = DataSpecification.get_column_types(
                    data=api_specification.get_api_output_attributes())
                data_binding.set_output_column_types(output_column_types=output_column_types)
                data_binding._validate(aib_data_specification=aib_data_specification)

            # Get or Create AI Model
            model_id = ai_model.retrieve(model_name=model_name)
            if model_id and override is False:  # AI Model with this name already exists
                raise ModelNotFoundException(f"Model already exists {model_name}. "
                                             f"Set override=True to update the model or use a different model name.")
            elif model_id is None:  # create a new AI Model
                model_id = ai_model.create(model_name=model_name, template_id=model_template_id)

            # Create Train Configuration
            train_config_id = train_config.create(model_name=model_name, model_id=model_id, model_type=model_type,
                                                  scoring_config=scoring_config, data_binding=data_binding,
                                                  batch_size=batch_size)

            response = train_config.update(train_config_id=train_config_id)

            # construct connector name
            connector_name = AIBModelClient._construct_connector_name(model_name=model_name,
                                                                      train_config=train_config,
                                                                      train_config_id=train_config_id)

            # Create connection
            pa_connection_response = PowerAppsCustomConnector.create_connection(
                environment_name=environment_name,
                open_api_specification=api_specification,
                model_name=connector_name,
                connection_name=model_id,
                override=override,
                org_url=org_url,
                cds_token=token
            )

            # Add connection and connector details to scoring config dictionary
            # Scoring url will also be updated to use connection url
            scoring_config.update(pa_connection_response)

            # Unschedule AI Builder model before publishing an updated model
            if override:
                ai_model.unschedule(model_id=model_id)

            # Publish model
            publish_response = AIBModelClient.publish(org_url=org_url, model_name=model_name, model_type=model_type,
                                                      model_id=model_id, train_config_id=train_config_id, token=token,
                                                      scoring_config=scoring_config, data_binding=data_binding,
                                                      data_specification=aib_data_specification, batch_size=batch_size)

            if publish_response.status != ModelClientResponseStatus.success:
                raise RegistrationException(f"Model publishing failed: {publish_response}")

            # Set schedule to never
            schedule_response = ai_model.schedule(model_id=model_id)
            if schedule_response.status_code != 200:
                raise RegistrationException(f"Model scheduling failed: {schedule_response}")

            return ModelClientResponse(model_name=model_name,
                                       model_id=model_id,
                                       status=ModelClientResponseStatus.success,
                                       kwargs={"response": response})
        except Exception as e:
            logger.error(f"Failed to register {model_name} model")
            raise RegistrationException(f"Registration failed due to the following error: {e}")

    @classmethod
    def delete(cls, model_name: str) -> ModelClientResponse:
        pass

    @classmethod
    def publish(cls, org_url: str, model_name: str, model_type: _AIBModelType, model_id: str, train_config_id: str,
                token: str, scoring_config: dict, data_binding: Optional[AIBBinding],
                data_specification: str, batch_size: int) -> ModelClientResponse:
        """
        Publish the model created

        :param org_url: Model host URL
        :param model_name: Name of the model to be created on the hosting service
        :param model_type: AI Builder model type
        :param model_id: AI Builder Model ID
        :param train_config_id: Train configuration id linked to AI Model
        :param token: Bearer token to authorize with CDS
        :param scoring_config: Scoring configuration containing model information
        :param data_binding: Data Binding used to create run configuration
        :param data_specification: Data Specification used to create run configuration
        :param batch_size: Number of prediction rows model endpoint can handle in one call
        :return:
        """

        run_config = RunConfiguration(url=org_url, token=token)
        run_config_id = run_config.create(model_type=model_type, model_name=model_name, model_id=model_id,
                                          train_config_id=train_config_id, scoring_config=scoring_config,
                                          data_binding=data_binding, data_specification=data_specification,
                                          batch_size=batch_size)
        response = run_config.update(run_config_id=run_config_id)

        publish_status = ModelClientResponseStatus.failure
        if response.status_code == 200:
            # Poll for the publish status
            publish_action_status = polling2.poll(
                lambda: AIBModelClient._check_publish_status(run_config=run_config,
                                                             run_config_id=run_config_id),
                check_success=lambda status: status is True,
                step=0.5,
                timeout=30)
            publish_status = ModelClientResponseStatus.success
            if not publish_action_status:
                publish_status = ModelClientResponseStatus.failure
                logger.error("Publish action didn't succeed in time")

        return ModelClientResponse(model_name=model_name,
                                   model_id=model_id,
                                   status=publish_status,
                                   kwargs={"response": response})

    @classmethod
    def _check_publish_status(cls, run_config: RunConfiguration, run_config_id: str) -> bool:
        """
        Check if the publish action call was successful
        :param run_config_id: Run AI Configuration id
        :return: True if run config is in published state, else return False
        """
        run_config_dict = run_config.retrieve(run_config_id=run_config_id)
        return run_config_dict[_AIModelConstants.STATUS_CODE.value] == _AIModelConstants.PUBLISHED_STATE.value or \
               run_config_dict[_AIModelConstants.STATUS_CODE.value] == _AIModelConstants.SCHEDULED_STATE.value

    @classmethod
    def _construct_connector_name(cls, model_name: str, train_config: TrainConfiguration,
                                  train_config_id: str) -> str:
        """
        Construct a unique connector name based on model name
        :param model_name: AI Builder model name
        :param train_config: TrainConfiguration class object
        :param train_config_id: Train configuration id
        :return: Constructed connector name
        """
        random_hex = AIBModelClient._get_random_characters()

        train_config_body = train_config.retrieve(train_config_id=train_config_id)
        train_config_major_iteration_number = train_config_body[_AIModelConstants.MSDYN_MAJOR_ITERATION_NUMBER.value]

        connector_suffix = f"-{random_hex}-v{train_config_major_iteration_number}"

        model_name_substring_length = _AIBModelClientConstants.connector_name_max_length.value - len(connector_suffix)
        connector_name = model_name[:model_name_substring_length] + connector_suffix

        return connector_name

    @classmethod
    def unpublish(cls, model_name: str, **kwargs: dict) -> ModelClientResponse:
        pass

    @classmethod
    def predict(cls, model_name: str, **kwargs: dict) -> ModelClientResponse:
        pass

    @classmethod
    def test(cls, model_name: str, payload: object) -> ModelClientResponse:
        pass

    @staticmethod
    def _validate_prediction_timeout(prediction_timeout: Optional[int]) -> Union[int, float]:
        """Validates prediction timeout value and returns a valid prediction timeout value.
        If prediction timeout is None, then returns a default value of 5 seconds

        :param prediction_timeout: Prediction time out in seconds for each prediction call
        :return: A validated prediction timeout value
        """
        if prediction_timeout is None:
            prediction_timeout = _AIBModelClientConstants.default_prediction_timeout_in_seconds.value

        # Validating prediction timeout value
        if not (isinstance(prediction_timeout, int) or isinstance(prediction_timeout, float)) or \
                prediction_timeout <= 0 \
                or prediction_timeout > _AIBModelClientConstants.max_prediction_timeout_in_seconds.value:
            raise ValueError(f"Prediction timeout should be an integer or a float "
                             f"with value greater than 0 and less than 20 (in seconds). Got: {prediction_timeout}")

        return prediction_timeout

    @staticmethod
    def _get_random_characters() -> str:
        """Generating 6 random characters using uppercase ascii alphabets and digits"""
        allowed_characters = "ABCDEF" + string.digits
        random_hex = ''.join(random.choices(allowed_characters, k=6))
        return random_hex
