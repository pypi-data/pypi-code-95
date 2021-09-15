#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/


# Standard library
from typing import Union, List, Optional
import json
import os

# Third party
import pandas as pd
import requests
import yaml

# Oracle
from .common import utils
from .common.utils import OCIClientManager, State
from oci.signer import Signer
import oci
import oci.data_science.models as data_science_models

from .model_deployment import ModelDeployment, DEFAULT_WAIT_TIME, DEFAULT_POLL_INTERVAL
from .model_deployment_properties import ModelDeploymentProperties

"""
APIs to interact with Oracle's Model Deployment service.

There are three main classes: ModelDeployment, ModelDeploymentDetails, ModelDeployer

One creates a ModelDeployment and deploys it under the umbrella of the ModelDeployer class. This way
multiple ModelDeployments can be unified with one ModelDeployer. The ModelDeployer class also serves
as the interface to all the deployments. ModelDeploymentDetails holds information about the particular
details of a particular deployment, such as how many instances, etc. In this way multiple, independent
ModelDeployments with the same details can be created using the ModelDeployer class.

Usage:
    >> from model_deploy.model_deployer import ModelDeployer, ModelDeploymentDetails
    >> deployer = ModelDeployer("model_dep_conf.yaml")
    >> deployment_properties = ModelDeploymentProperties('ocid1.datasciencemodel.ocn.reg.xxxxxxxxxxxxxxxxxxxxxxxxx')\
                            .with_prop('display_name', "My model display name")\
                            .with_prop("project_id", project_id)\
                            .with_prop("compartment_id", compartment_id)\
                            .with_instance_configuration(config={"INSTANCE_SHAPE":"VM.Standard2.1", "INSTANCE_COUNT":"1", 'bandwidth_mbps':10}).build()
    >> deployment_info = deployer.deploy(deployment_properties, max_wait_time=600, poll_interval=15)
    >> print(deployment_info.model_deployment_id)
    >> print(deployment_info.workflow_req_id)
    >> print(deployment_info.url)
    >> deployer.list_deployments() # Optionally pass in a status
"""

class ModelDeployer:
    """ModelDeployer is the class responsible for deploying the ModelDeployment

    Attributes
    ----------
    config (dict): deployment configuration
    ds_client (DataScienceClient): data science client
    ds_composite_client (DataScienceCompositeClient): composite data science client

    Methods
    -------
    load_config(config_file)
        Load configuration file for deployment.
    deploy(model_deployment_details, **kwargs)
        Deploy the model specified by `model_deployment_details`.
    get_model_deployment(model_deployment_id:str)
        Get the ModelDeployment specified by `model_deployment_id`.
    get_model_deployment_state(model_deployment_id)
        Get the state of the current deployment specified by id.
    delete(model_deployment_id, **kwargs)
        Remove the model deployment specified by the id or Model Deployment Object
    list_deployments(status)
        lists the model deployments associated with current compartment and data 
        science client
    show_deployments(status)
        shows the deployments filterd by `status` in a Dataframe

    """

    def __init__(self, config=None):
        # self.config contains contents of yml file/dict passed in by user
        self.config = utils.load_config(config)
        self.service_endpoint = self.config.get("OCI_ODSC_SERVICE_ENDPOINT")
        self.ds_client = OCIClientManager.oci_ds_client(self.config)
        self.ds_composite_client = OCIClientManager.oci_ds_composite_client(self.ds_client)

    def deploy(self, properties=None, wait_for_completion:bool = True,
            max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL, 
            **kwargs) -> ModelDeployment:
        """Deploys a model.

        Args:
            properties (ModelDeploymentProperties or dict): properties to deploy the model.
                properties can be None when kwargs are used for specifying properties.
            wait_for_completion (bool, optional): Flag set for whether to wait for deployment to complete before
                proceeding. Defaults to True
            max_wait_time (int, optional): Maximum amount of time to wait in seconds (Defaults to 1200). Negative implies infinite wait time.
            poll_interval (int, optional): Poll interval in seconds (Defaults to 30).
            kwargs: Keyword arguments for initializing ModelDeploymentProperties

        Returns:
            ModelDeployment: ModelDeployment objects that was deployed
        """
        model_deployment = ModelDeployment(properties, config=self.config,
                                            ds_client=self.ds_client, 
                                            ds_composite_client=self.ds_composite_client, **kwargs)
        return model_deployment.deploy(wait_for_completion, max_wait_time, poll_interval)

    def update(self, model_deployment_id: str, properties: ModelDeploymentProperties = None, wait_for_completion:bool = True,
            max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL,
            **kwargs) -> ModelDeployment:
        """Updates an existing model deployment.

        Args:
            model_deployment_id (str): Model deployment OCID
            properties (ModelDeploymentProperties, optional): An instance of ModelDeploymentProperties or 
                dict to initialize the ModelDeploymentProperties. Defaults to None.
            wait_for_completion (bool, optional): Flag set for whether to wait for deployment to complete before
                proceeding. Defaults to True
            max_wait_time (int, optional): Maximum amount of time to wait in seconds (Defaults to 1200).
            poll_interval (int, optional): Poll interval in seconds (Defaults to 30).
            kwargs: Updates can also be specified in keyword arguments.

        Returns:
            ModelDeployment: a ModelDeployment object

        """
        try:
            model_deployment = self.get_model_deployment(model_deployment_id)
            # Deployment properties will be refreshed within model_deployment.update() when update is done.
            return model_deployment.update(
                properties,
                wait_for_completion,
                max_wait_time=max_wait_time,
                poll_interval=poll_interval,
                **kwargs
            )
        except Exception as e:
            utils.get_logger().error("Updating model deployment failed with error: %s", format(e))
            raise e
    
    def get_model_deployment(self, model_deployment_id:str) -> ModelDeployment:
        """get_model_deployment returns the ModelDeployment specified by `model_deployment_id`.

        Args:
            model_deployment_id (str): the model deployment ocid

        Returns:
            [ModelDeployment]: a ModelDeployment object
        """

        try:
            oci_model_deployment_object = self.ds_client.get_model_deployment(model_deployment_id).data
            model_deployment_object = ModelDeployment(
                oci_model_deployment_object,
                config=self.config,
                ds_client=self.ds_client,
                ds_composite_client=self.ds_composite_client
            )
            return model_deployment_object
        except Exception as e:
            utils.get_logger().error("Getting model deployment failed with error: %s", e)
            raise e

    def get_model_deployment_state(self, model_deployment_id:str) -> State:
        """get_model_deployment_state returns the state of the current deployment specified by id

        Args:
            model_deployment_id (str): the model deployment ocid

        Returns:
            [str]: current state of the deployment specified by model_deployment_id
        """

        model_deployment = self.get_model_deployment(model_deployment_id)
        return model_deployment.state

    def delete(self, model_deployment_id, wait_for_completion:bool = True, 
            max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL) -> ModelDeployment:
        """delete removes the model deployment specified by the id or Model Deployment Object

        Args:
            model_deployment (str): the model deployment ocid
            wait_for_completion (bool, optional): Wait for deletion to complete. Defaults to True.
            max_wait_time (int, optional): Maximum amount of time to wait in seconds (Defaults to 600). 
                Negative implies infinite wait time.
            poll_interval (int, optional): Poll interval in seconds (Defaults to 60).

        Returns:
            ModelDeployment object that was deleted
        """
        try:
            model_deployment_object = self.get_model_deployment(model_deployment_id)
            return model_deployment_object.delete(wait_for_completion, max_wait_time, poll_interval)
        except Exception as e:
            utils.get_logger().error("Deleting model deployment failed with error: %s", format(e))
            raise e

    def list_deployments(self, status=None, compartment_id=None, **kwargs) -> list:
        """ Lists the model deployments associated with current compartment and data science client

        Args:
            status (str, optional): Status of deployment. Defaults to None.
            compartment_id (str, optional): Target compartment to list deployments from.
                Defaults to the compartment set in the environment variable "NB_SESSION_COMPARTMENT_OCID".
                If "NB_SESSION_COMPARTMENT_OCID" is not set, the root compartment ID will be used.
                An ValueError will be raised if root compartment ID cannot be determined.
            kwargs: The values are passed to oci.data_science.DataScienceClient.list_model_deployments.

        Returns:
            list: A list of ModelDeployment objects.

        Raises:
            ValueError: If compartment_id is not specified and cannot be determined from the environment.

        """
        if not compartment_id:
            compartment_id = OCIClientManager.default_compartment_id()
        if not compartment_id:
            raise ValueError("Unable to determine compartment ID from environment. Please specify compartment_id.")

        if isinstance(status, State):
            status = status.name

        if status is not None:
            kwargs["lifecycle_state"] = status
        
        # https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/pagination.html#module-oci.pagination
        deployments = oci.pagination.list_call_get_all_results(
            self.ds_client.list_model_deployments,
            compartment_id, 
            **kwargs
        ).data
        return [ModelDeployment(deployment) for deployment in deployments]

    def show_deployments(self, status = None, compartment_id=os.environ.get('NB_SESSION_COMPARTMENT_OCID', None)) -> pd.DataFrame:
        """ Returns the model deployments associated with current compartment and data science client
            as a Dataframe that can be easily visualized

        Args:
            status ([str], optional): Status of deployment. Defaults to None.
            compartment_id ([str], optional): Target compartment from which to list deployments. 
                                              Defaults to compartment set in the environment.

        Returns:
            [pd.DataFrame]: Dataframe containing information about the ModelDeployments
        """
        if type(status) == str or status == None:
            status = State._from_str(status)
        model_deployments = self.ds_client.list_model_deployments(compartment_id).data
        display = pd.DataFrame()
        ids, urls, status_list = [], [], []
        for oci_model_deployment_object in model_deployments:
            state_of_model = State._from_str(oci_model_deployment_object.lifecycle_state)
            if status == State.UNKNOWN or status.name == state_of_model.name:
                model_dep_id = oci_model_deployment_object.id
                model_dep_url = oci_model_deployment_object._model_deployment_url
                model_dep_state = oci_model_deployment_object.lifecycle_state
                ids.append(model_dep_id)
                urls.append(model_dep_url)
                status_list.append(model_dep_state)
        display['model_id'] = ids
        display['deployment_url'] = urls
        display['current_state'] = status_list
        return display