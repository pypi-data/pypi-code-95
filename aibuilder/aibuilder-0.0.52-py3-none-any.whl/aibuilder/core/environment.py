#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------
import json
from typing import Optional, Union

from azureml.core.webservice import Webservice

from aibuilder.common.auth.d365_connector import D365Connector
from aibuilder.common.paconnector.constants import PowerAppsApiSettings, RequestBuilderConstants, PowerAppsSettings
from aibuilder.common.paconnector.powerapps_connector import PowerAppsConnector
from aibuilder.common.paconnector.request_builder import _RequestBuilder
from aibuilder.common.utils import Credentials
from aibuilder.core.constants import ExecutionPolicy
from aibuilder.core.model_connection import LocalFileConnection
from aibuilder.models.aib_binding import AIBBinding
from aibuilder.models.aib_model_client import AIBModelClient
from aibuilder.models.constants import ModelClientResponseStatus
from aibuilder.models.helpers.exceptions import TemplateNotFoundException


class Environment:
    """
    PowerApps environment class which can be used to connect ML models to AI Builder

    """

    def __init__(self, environment_url: str, d365_connector: D365Connector, environment_name: str):
        """
        
        :param environment_url: PowerApps organization URL
        :param d365_connector: Dynamics 365 connector object
        """
        self._environment_url = environment_url
        self._d365connector = d365_connector
        self._environment_name = environment_name
        self._isPaiEnabled = False

    @classmethod
    def get(cls, environment_name: str, credentials: Optional[Credentials] = None) -> "Environment":
        """
        Used to get the PowerApps environment

        .. code-block:: python
            :caption: **Example code to get the environment from environment name**

            from aibuilder.core.environment import Environment

            environment_name = "your_friendly_environment_name"
            env = Environment.get(environment_name=environment_name)

        :param environment_name: Friendly name of the PowerApps environment
        :param credentials: Credentials containing username and password of the service/user account used to register
        :return: Environment object
        :rtype: Environment
        """
        pa_connector = Environment._get_powerapps_connector(credentials=credentials)

        env_name, environment_url = pa_connector. \
            get_environment_name_and_url(environment_friendly_name=environment_name)
        environment = Environment(environment_url, pa_connector.d365connector, env_name)
        return environment

    def register_model(self, model_name: str, connection: [LocalFileConnection, Webservice],
                       override: bool = False, data_binding: Optional[AIBBinding] = None,
                       batch_size: Optional[int] = None,
                       prediction_timeout: Optional[Union[int, float]] = None) -> ModelClientResponseStatus:
        """
        Registers an externally hosted ML model with AI Builder using model_name and api specification swagger file

        .. code-block:: python
            :caption: **Example code to use Environment Object**

            from azureml.core import Workspace
            from azureml.core.webservice import Webservice, AciWebservice

            from aibuilder.common.auth.d365_connector import D365Connector
            from aibuilder.core.environment import Environment

            model_name = "your_powerapps_ml_model_name"
            environment_url= "https://your-organization-url-from-powerapps.com"
            d365_connector= D365Connector()
            environment_name= "non_friendly_environment_name" # Looks like 16fd2706-8baf-433b-82eb-8c7fada847da
            env = Environment(environment_url=environment_url, d365_connector=, environment_name=str)
            ws = Workspace.get(name='your_azure_ml_workspace_name', subscription_id='your_azureml_subscription_id',
                               resource_group='your_azure_ml_resource_group')
            service = AciWebservice(workspace=ws, name="your-aci-service-name")
            response = env.register_model(model_name=model_name, connection=service)

        :param model_name: Name of AI Builder model to be created
        :param connection: Model connection object to retrieve model information.
        :param override: Update a registered model
        :param data_binding: Data binding string
        :param batch_size: Number of prediction rows model endpoint can handle in one call
        :param prediction_timeout: Prediction time out in seconds for each prediction call
        :return: Model host response status object
        """
        self._isPaiEnabled = self._check_pai_enabled()
        if self._isPaiEnabled:
            token = self._d365connector.authenticate_with_dynamics_crm(organization_url=self._environment_url)
            batch_size = Environment._get_valid_batch_size(batch_size=batch_size)
            response = AIBModelClient.create(model_name=model_name, model_connection=connection,
                                             org_url=self._environment_url, data_binding=data_binding, token=token,
                                             environment_name=self._environment_name, override=override,
                                             batch_size=batch_size, prediction_timeout=prediction_timeout)

            if response.status == ModelClientResponseStatus.success:
                print(f"{model_name} Model registration is successful")
            else:
                print(f"{model_name} Model registration failed")

            return response.status
        else:
            raise TemplateNotFoundException(f"This capability is not available / enabled in this environment. Please "
                                            f"contact the Environment owner / administrator")

    def _check_pai_enabled(self) -> bool:
        """
        Checks if BYOM template is enabled in the environment

        :return: Boolean to acknowledge if BYOM template is present in the environment
        """
        org_url = self._environment_url
        base_path = PowerAppsApiSettings.BASE_URL.value
        cds_token = self._d365connector.authenticate_with_dynamics_crm(organization_url=org_url)
        request_builder = _RequestBuilder(url=org_url, base_path=base_path, token=cds_token)
        endpoint = org_url + base_path + "/" + PowerAppsSettings.IsPaiEnabled.value
        try:
            response = request_builder.request(method=RequestBuilderConstants.POST, endpoint=endpoint)
            response_json = json.loads(response.text)
            templates = json.loads(response_json[PowerAppsApiSettings.TEMPLATES.value])
            byom_template = list(filter(lambda template_name: template_name['name'] == PowerAppsApiSettings.BYOM.value,
                                        templates))
            if len(byom_template) > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Unable to authenticate to the environment {org_url}")
            raise TemplateNotFoundException(f"Unable to find BYOM template due to : {e}")

    @staticmethod
    def _get_valid_batch_size(batch_size: Optional[int]) -> Optional[int]:
        """
        Validates that batch size is in between 1 and 10000

        :param batch_size: Number of prediction rows model endpoint can handle in one call
        :return: A valid batch size number or None
        """
        if isinstance(batch_size, int) and batch_size > 0:
            if batch_size > ExecutionPolicy.max_batch_size.value:
                print(f"Maximum batch size supported is {ExecutionPolicy.max_batch_size.value}, "
                      f"using {ExecutionPolicy.max_batch_size.value} as batch size")
                batch_size = ExecutionPolicy.max_batch_size.value
            return batch_size
        return None

    @staticmethod
    def _get_powerapps_connector(credentials: Credentials) -> "PowerAppsConnector":
        """
        Creates PowerAppsConnector class object using username and password

        :param credentials: Credentials object containing username and password
        :return: Returns PowerAppsConnector object
        """
        return PowerAppsConnector(credentials=credentials)
