# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for deploying models to AzureML through MLFlow."""

import json
import logging
from azureml.core import Webservice, Model as AzureModel
from azureml.core.webservice import AciWebservice
from azureml.exceptions import WebserviceException
from azureml.mlflow._internal.utils import load_azure_workspace
from azureml._model_management._util import deploy_config_dict_to_obj
from azureml._restclient.clientbase import ClientBase
from mlflow.deployments import BaseDeploymentClient
from mlflow.exceptions import MlflowException
from mlflow.utils.annotations import experimental
from mlflow.utils.file_utils import TempDir
from ._util import (file_stream_to_object, handle_model_uri, create_inference_config,
                    submit_update_call, get_deployments_import_error)


_logger = logging.getLogger(__name__)


class AzureMLDeploymentClient(BaseDeploymentClient):
    """Client object used to deploy MLFlow models to AzureML."""

    def __init__(self, target_uri):
        """
        Initialize the deployment client with the MLFlow target uri.

        :param target_uri: AzureML workspace specific target uri.
        :type target_uri: str
        """
        super(AzureMLDeploymentClient, self).__init__(target_uri)
        try:
            self.workspace = load_azure_workspace()
        except Exception as e:
            raise MlflowException("Failed to retrieve AzureML Workspace") from e

    @experimental
    def create_deployment(self, name, model_uri, flavor=None, config=None):
        """
        Deploy a model to the specified target.

        Deploy a model to the specified target. By default, this method should block until
        deployment completes (i.e. until it's possible to perform inference with the deployment).
        In the case of conflicts (e.g. if it's not possible to create the specified deployment
        without due to conflict with an existing deployment), raises a
        :py:class:`mlflow.exceptions.MlflowException`. See target-specific plugin documentation
        for additional detail on support for asynchronous deployment and other configuration.

        :param name: Unique name to use for deployment. If another deployment exists with the same
                     name, raises a :py:class:`mlflow.exceptions.MlflowException`
        :param model_uri: URI of model to deploy. AzureML supports deployments of 'models', 'runs', and 'file' uris.
        :param flavor: (optional) Model flavor to deploy. If unspecified, a default flavor
                       will be chosen.
        :param config: (optional) Dict containing updated target-specific configuration for the
                       deployment
        :return: Dict corresponding to created deployment, which must contain the 'name' key.
        """
        model_name, model_version = handle_model_uri(model_uri, name)

        try:
            aml_model = AzureModel(self.workspace, id='{}:{}'.format(model_name, model_version))
        except Exception as e:
            raise MlflowException('Failed to retrieve model to deploy') from e

        # Convert passed in file to deployment config
        if config and 'deploy-config-file' in config:
            try:
                # TODO: Tags, properties, and description are not in the config file for some reason?
                with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                    deploy_config_obj = file_stream_to_object(deploy_file_stream)
                    deploy_config = deploy_config_dict_to_obj(deploy_config_obj, None, None, None)
            except Exception as e:
                raise MlflowException('Failed to parse provided deployment config file') from e
        else:
            deploy_config = AciWebservice.deploy_configuration()

        with TempDir(chdr=True) as tmp_dir:
            inference_config = create_inference_config(tmp_dir, model_name, model_version, name)

            try:
                _logger.info("Creating an AzureML deployment with name: `%s`", name)

                # Deploy
                webservice = AzureModel.deploy(
                    workspace=self.workspace,
                    name=name,
                    models=[aml_model],
                    inference_config=inference_config,
                    deployment_config=deploy_config,
                )

                if config and 'async' in config and config['async']:
                    _logger.info('AzureML deployment in progress, you can use get_deployment to check on the current '
                                 'deployment status.')
                else:
                    webservice.wait_for_deployment(show_output=True)
            except Exception as e:
                raise MlflowException('Error while creating deployment') from e

            return webservice.serialize()

    @experimental
    def update_deployment(self, name, model_uri=None, flavor=None, config=None):
        """
        Update the deployment specified by name.

        Update the deployment with the specified name. You can update the URI of the model, the
        flavor of the deployed model (in which case the model URI must also be specified), and/or
        any target-specific attributes of the deployment (via `config`). By default, this method
        should block until deployment completes (i.e. until it's possible to perform inference
        with the updated deployment). See target-specific plugin documentation for additional
        detail on support for asynchronous deployment and other configuration.

        :param name: Unique name of deployment to update
        :param model_uri: URI of a new model to deploy.
        :param flavor: (optional) new model flavor to use for deployment. If provided,
                       ``model_uri`` must also be specified. If ``flavor`` is unspecified but
                       ``model_uri`` is specified, a default flavor will be chosen and the
                       deployment will be updated using that flavor.
        :param config: (optional) dict containing updated target-specific configuration for the
                       deployment
        :return: None
        """
        try:
            service = Webservice(self.workspace, name)
        except Exception as e:
            raise MlflowException('Error retrieving deployment to update') from e

        models = None
        inference_config = None

        with TempDir(chdr=True) as tmp_dir:
            if model_uri:
                model_name, model_version = handle_model_uri(model_uri, name)
                try:
                    aml_model = AzureModel(self.workspace, id='{}:{}'.format(model_name, model_version))
                except Exception as e:
                    raise MlflowException('Failed to retrieve model to deploy') from e
                models = [aml_model]

                inference_config = create_inference_config(tmp_dir, model_name, model_version, name)

            deploy_config = None
            if 'deploy-config-file' in config:
                try:
                    # TODO: Tags, properties, and description are not in the config file for some reason?
                    with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                        deploy_config_obj = file_stream_to_object(deploy_file_stream)
                        deploy_config = deploy_config_dict_to_obj(deploy_config_obj, None, None, None)
                except Exception as e:
                    raise MlflowException('Failed to parse provided deployment config file') from e

            aks_endpoint_version_config = None  # TODO deployment or version/service? Talk to PMs
            if 'aks-endpoint-deployment-config' in config:
                aks_endpoint_version_config = config['aks-endpoint-deployment-config']

            try:
                submit_update_call(service, models, inference_config, deploy_config, aks_endpoint_version_config)

                if 'async' in config and config['async']:
                    _logger.info('AzureML deployment in progress, you can use get_deployment to check on the current '
                                 'deployment status.')
                else:
                    service.wait_for_deployment(show_output=True)
            except Exception as e:
                raise MlflowException('Error submitting deployment update') from e

    @experimental
    def delete_deployment(self, name):
        """
        Delete the deployment with name ``name``.

        :param name: Name of deployment to delete
        :return: None
        """
        try:
            service = Webservice(self.workspace, name)
            service.delete()
        except WebserviceException as e:
            if 'WebserviceNotFound' not in e.message:
                _logger.info('Deployment with name {} not found, no service to delete'.format(name))
                return
            raise MlflowException('There was an error deleting the deployment: \n{}'.format(e.message)) from e

    @experimental
    def list_deployments(self):
        """
        List deployments.

        :return: A list of dicts corresponding to deployments.
        """
        try:
            service_list = []
            services = Webservice.list(self.workspace)
            for service in services:
                service_list.append(service.serialize())
            return service_list
        except WebserviceException as e:
            raise MlflowException('There was an error listing deployments: \n{}'.format(e.message)) from e

    @experimental
    def get_deployment(self, name):
        """
        Retrieve details for the specified deployment.

        Returns a dictionary describing the specified deployment. The dict is guaranteed to contain an 'name' key
        containing the deployment name.

        :param name: Name of deployment to retrieve
        """
        try:
            service = Webservice(self.workspace, name)
            return service.serialize()
        except WebserviceException as e:
            raise MlflowException('There was an error retrieving the deployment: \n{}'.format(e.message)) from e

    @experimental
    def predict(self, deployment_name, df):
        """
        Predict on the specified deployment using the provided dataframe.

        Compute predictions on the pandas DataFrame ``df`` using the specified deployment.
        Note that the input/output types of this method matches that of `mlflow pyfunc predict`
        (we accept a pandas DataFrame as input and return either a pandas DataFrame,
        pandas Series, or numpy array as output).

        :param deployment_name: Name of deployment to predict against
        :param df: Pandas DataFrame to use for inference
        :return: A pandas DataFrame, pandas Series, or numpy array
        """
        try:
            from mlflow.pyfunc.scoring_server import parse_json_input, _get_jsonable_obj
        except ImportError as exception:
            raise get_deployments_import_error(exception)

        try:
            service = Webservice(self.workspace, deployment_name)
        except Exception as e:
            raise MlflowException('Failure retrieving deployment to predict against') from e

        # Take in DF, parse to json using split orient
        input_data = _get_jsonable_obj(df, pandas_orient='split')

        if not service.scoring_uri:
            raise MlflowException('Error attempting to call webservice, scoring_uri unavailable. '
                                  'This could be due to a failed deployment, or the service is not ready yet.\n'
                                  'Current State: {}\n'
                                  'Errors: {}'.format(service.state, service.error))

        # Pass split orient json to webservice
        # Take records orient json from webservice
        resp = ClientBase._execute_func(service._webservice_session.post, service.scoring_uri,
                                        data=json.dumps({'input_data': input_data}))

        if resp.status_code == 401:
            if service.auth_enabled:
                service_keys = service.get_keys()
                service._session.headers.update({'Authorization': 'Bearer ' + service_keys[0]})
            elif service.token_auth_enabled:
                service_token, refresh_token_time = service.get_access_token()
                service._refresh_token_time = refresh_token_time
                service._session.headers.update({'Authorization': 'Bearer ' + service_token})
            resp = ClientBase._execute_func(service._webservice_session.post, service.scoring_uri, data=input_data)

        if resp.status_code == 200:
            # Parse records orient json to df
            return parse_json_input(json.dumps(resp.json()), orient='records')
        else:
            raise MlflowException('Failure during prediction:\n'
                                  'Response Code: {}\n'
                                  'Headers: {}\n'
                                  'Content: {}'.format(resp.status_code, resp.headers, resp.content))
