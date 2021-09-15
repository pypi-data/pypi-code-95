#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/


# Standard library
from typing import Union, List, Optional
import collections
import datetime
import json
import os
import time
from oci.auth import signers

# Third party
import pandas as pd
import requests
import yaml

# Oracle
from .common import utils
from .common.utils import OCIClientManager, State
from .model_deployment_properties import ModelDeploymentProperties
import oci


DEFAULT_WAIT_TIME = 1200
DEFAULT_POLL_INTERVAL = 30

class ModelDeployment:
    """
    A class used to represent a Model Deployment.

    Attributes
    ----------
    config (dict): Deployment configuration parameters
    deployment_properties (ModelDeploymentProperties): ModelDeploymentProperties object
    workflow_state_progress (str): Workflow request id
    workflow_steps (int): The number of steps in the workflow
    url (str): The model deployment url endpoint
    ds_client (DataScienceClient): The data science client used by model deployment
    ds_composite_client (DataScienceCompositeClient): The composite data science client used by the model deployment
    workflow_req_id (str): Workflow request id
    model_deployment_id (str): model deployment id
    state: Returns the deployment state of the current Model Deployment object

    Methods
    -------
    deploy(wait_for_completion, **kwargs)
        Deploy the current Model Deployment object
    delete(wait_for_completion, **kwargs)
        Deletes the current Model Deployment object
    state()
        Returns the deployment state of the current Model Deployment object
    list_workflow_logs()
        Returns a list of the steps involved in deploying a model
    wait_for_deletion(max_wait_time, poll_interval)
        Block until deletion is complete
    _wait_for_activation(max_wait_time, poll_interval)
        Block until activation is complete

    """

    def __init__(self, properties=None, config=None, 
                workflow_req_id=None, model_deployment_id=None, model_deployment_url="", 
                ds_client=None, ds_composite_client=None, **kwargs):
        """Creates a ModelDeployment object

        Args:
            properties (ModelDeploymentProperties or dict): Object containing deployment properties.
                properties can be None when kwargs are used for specifying properties.
            config (dict, optional): deployment configuration parameters. Defaults to None
            workflow_req_id (str, optional): workflow request id. Defaults to ""
            model_deployment_id (str, optional): model deployment id. Defaults to ""
            model_deployment_url (str, optional): model deployment url. Defaults to ""
            ds_client (DataScienceClient, optional): data science client. Defaults to None
            ds_composite_client (DataScienceCompositeClient, optional): composite data science client. Defaults to None.
            kwargs: Keyword arguments for initializing ModelDeploymentProperties
        """

        if config is None:
            utils.get_logger().info("Using default configuration.")
            
        if ds_client is None:
            ds_client = OCIClientManager.oci_ds_client(config)
        if ds_composite_client is None:
            ds_composite_client = OCIClientManager.oci_ds_composite_client(ds_client)

        self.properties = properties if isinstance(properties, ModelDeploymentProperties) \
            else ModelDeploymentProperties(oci_model_deployment=properties, **kwargs)

        self.current_state = State._from_str(
            self.properties.lifecycle_state
        ) if self.properties.lifecycle_state else State.UNKNOWN
        self.url = model_deployment_url if model_deployment_url else self.properties.model_deployment_url
        self.model_deployment_id = model_deployment_id if model_deployment_id else self.properties.id

        self.workflow_state_progress = []
        self.workflow_steps = 5
        
        # self.config is Model Deployment SDK config
        self.config = config
        self.ds_client = ds_client
        self.ds_composite_client = ds_composite_client
        self.workflow_req_id = workflow_req_id

        if self.ds_client:
            oci_config, signer = OCIClientManager.get_oci_config_signer(self.config)
            self.log_search_client = oci.loggingsearch.LogSearchClient(
                oci_config,
                signer=signer
            )

    def deploy(self, wait_for_completion:bool = True,
            max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL):
        """deploy deploys the current ModelDeployment object

        Args:
            wait_for_completion (bool, optional): Flag set for whether to wait for deployment to complete before
                proceeding. Defaults to True
            max_wait_time (int, optional): Maximum amount of time to wait in seconds (Defaults to 600). Negative implies infinite wait time.
            poll_interval (int, optional): Poll interval in seconds (Defaults to 60).

        Returns:
            [ModelDeployment]: ModelDeployment object

        Raises:
            Exception: raised on deployment errors during _wait_for_activation
        """

        response = self.ds_composite_client.create_model_deployment_and_wait_for_state(
            self.properties.to_create_deployment()
        )
        self.workflow_req_id = response.headers['opc-work-request-id']
        res_payload = json.loads(str(response.data))
        self.current_state = State._from_str(res_payload['lifecycle_state'])
        self.model_deployment_id = res_payload['id']
        if wait_for_completion:
            try:
                self._wait_for_activation(max_wait_time, poll_interval)
            except Exception as e:
                utils.get_logger().error(f"Error while trying to deploy: {str(e)}")
                raise e
        return self

    def delete(self, wait_for_completion:bool = True, 
            max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL):
        """" Deletes the current ModelDeployment object

        Args:
            wait_for_completion (bool, optional): Wait for deletion to complete. Defaults to True.
            max_wait_time (int, optional): Maximum amount of time to wait in seconds (Defaults to 600). 
                Negative implies infinite wait time.
            poll_interval (int, optional): Poll interval in seconds (Defaults to 60).

        Returns:
            ModelDeployment object that was deleted

        Raises:
            Exception: exception raised if wait_for_deletion fails

        """

        response = self.ds_composite_client.delete_model_deployment_and_wait_for_state(self.model_deployment_id)
        self.workflow_req_id = response.headers['opc-work-request-id']
        oci_model_deployment_object = self.ds_client.get_model_deployment(self.model_deployment_id).data
        self.current_state = State._from_str(oci_model_deployment_object.lifecycle_state)
        if wait_for_completion:
            try:
                self._wait_for_deletion(max_wait_time, poll_interval)
            except Exception as e:
                utils.get_logger().error(f"Error while trying to delete: {str(e)}")
                raise e
        return self
    
    def update(self, properties: Union[ModelDeploymentProperties, dict, None] = None, wait_for_completion:bool = True,
            max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL, **kwargs):
        """ Updates a model deployment

        You can update `model_deployment_configuration_details` and change `instance_shape` and `model_id` 
        when the model deployment is in the ACTIVE lifecycle state. 
        The `bandwidth_mbps` or `instance_count` can only be updated while the model deployment is in the `INACTIVE` state. 
        Changes to the `bandwidth_mbps` or `instance_count` will take effect the next time 
        the `ActivateModelDeployment` action is invoked on the model deployment resource.

        Args:
            properties (ModelDeploymentProperties or dict): ModelDeploymentProperties object, or dict specifying the deployment details to be updated.
            kwargs (dict, optional): additional arguments sent to data science client update method

        Returns:
            ModelDeployment: the modified model deployment object

        Raises:
            Exception: exception raised on update failure
        """
        if not isinstance(properties, ModelDeploymentProperties):
            properties = ModelDeploymentProperties(properties, **kwargs)

        if wait_for_completion:
            wait_for_states=["SUCCEEDED", "FAILED"]
        else:
            wait_for_states = []

        try:
            response = self.ds_composite_client.update_model_deployment_and_wait_for_state(
                self.model_deployment_id, 
                properties.to_update_deployment(),
                wait_for_states=wait_for_states,
                waiter_kwargs={
                    "max_interval_seconds": poll_interval,
                    "max_wait_seconds": max_wait_time
                }
            )
            if 'opc-work-request-id' in response.headers:
                self.workflow_req_id = response.headers['opc-work-request-id']
            # Refresh the properties when model is active
            if wait_for_completion:
                # # There is a small delay between update process finished and model becomes active
                # self._wait_for_activation()
                self.properties = ModelDeploymentProperties(
                    oci_model_deployment=self.ds_client.get_model_deployment(self.model_deployment_id).data
                )
            return self
        except Exception as e:
            utils.get_logger().error("Updating model deployment failed with error: %s", format(e))
            raise e
    
    @property
    def state(self) -> State:
        """ Returns the deployment state of the current Model Deployment object
        """
        # Updates and returns self.state 
        oci_state = self.ds_client.get_model_deployment(self.model_deployment_id).data.lifecycle_state
        self.current_state = State._from_str(oci_state)
        return self.current_state

    def list_workflow_logs(self) -> list:
        """ Returns a list of the steps involved in deploying a model

        Returns:
            [list]: List of dictionaries detailing the status of each step in the deployment process

        Raises:
            Exception: raised if the workflow request id is empty or None
        """

        if self.workflow_req_id == "" or self.workflow_req_id == None:
            utils.get_logger().info("Workflow req id not available")
            raise Exception
        return self.ds_client.list_work_request_logs(self.workflow_req_id).data
    
    def predict(self, json_input:json) -> json:
        """ Returns prediction of input data run against the model deployment endpoint

        Args:
            json_input (JSON): [description]
            auth (str, optional): Authentication mode. Defaults to 'api_keys'.
        
        Returns:
            dict: Prediction

        Raises:
            ValueError: raised if authentication mode is not recognized
        """
        endpoint = self.url
        _, signer = OCIClientManager().get_oci_config_signer(self.config)
        response = requests.post(f"{endpoint}/predict", json=json_input, auth=signer).json()
        return response
    
    def _wait_for_deletion(self, max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL):
        """_wait_for_deletion blocks until deletion is complete

        Args:
            max_wait_time (int, optional): Maximum amount of time to wait in seconds (Defaults to 600). Negative implies infinite wait time.
            poll_interval (int, optional): Poll interval in seconds (Defaults to 60).

        Returns:
            Nothing

        Raises:
            Exception: If during the time window when the current state is not DELETED a check on the current
                state returns FAILED or INACTIVE, raise an Exception 
        """

        start_time = time.time()
        prev_message = ""
        if (max_wait_time > 0 and utils.seconds_since(start_time) >= max_wait_time):
            utils.get_logger().error(f"Error: Max wait time exceeded")
        while (max_wait_time < 0 or utils.seconds_since(start_time) < max_wait_time) and self.current_state.name.upper() != "DELETED":
            if self.current_state.name.upper() == State.FAILED.name:
                utils.get_logger().info("Deletion Failed. Please use Deployment ID for further steps.")
                break
            if self.current_state.name.upper() == State.INACTIVE.name:
                utils.get_logger().info("Deployment Inactive")
                break
            prev_state = self.current_state.name
            model_deployment_payload = json.loads(str(self.ds_client.get_model_deployment(self.model_deployment_id).data))
            self.current_state = State._from_str(model_deployment_payload['lifecycle_state']) if 'lifecycle_state' in model_deployment_payload else State.UNKNOWN
            workflow_payload = self.ds_client.list_work_request_logs(self.workflow_req_id).data
            if isinstance(workflow_payload, list) and len(workflow_payload) > 0:
                if prev_message != workflow_payload[-1].message:
                    prev_message = workflow_payload[-1].message
            if prev_state != self.current_state.name:
                if 'model_deployment_url' in model_deployment_payload:
                    self.url = model_deployment_payload['model_deployment_url']
                utils.get_logger().info(f"Status Update: {self.current_state.name} in {utils.seconds_since(start_time)} seconds")
            time.sleep(poll_interval)

    def _wait_for_activation(self, max_wait_time: int = DEFAULT_WAIT_TIME, poll_interval: int = DEFAULT_POLL_INTERVAL):
        """_wait_for_activation blocks deployment until activation is complete

        Args:
            max_wait_time (int, optional): Maximum amount of time to wait in seconds (Defaults to 600). Negative implies infinite wait time.
            poll_interval (int, optional): Poll interval in seconds (Defaults to 60).

        Returns
            Nothing
        """

        start_time = time.time()
        prev_message = ""
        prev_workflow_stage_len = 0
        with utils.get_progress_bar(self.workflow_steps) as progress:
            if (max_wait_time > 0 and utils.seconds_since(start_time) >= max_wait_time):
                utils.get_logger().error(f"Error: Max wait time exceeded")
            while (max_wait_time < 0 or utils.seconds_since(start_time) < max_wait_time) and self.current_state.name.upper() != "ACTIVE":
                if self.current_state.name.upper() == State.FAILED.name:
                    utils.get_logger().info("Deployment Failed. Please use Deployment ID for further steps.")
                    break
                if self.current_state.name.upper() == State.INACTIVE.name:
                    utils.get_logger().info("Deployment Inactive")
                    break
                prev_state = self.current_state.name
                model_deployment_payload = json.loads(str(self.ds_client.get_model_deployment(self.model_deployment_id).data))
                self.current_state = State._from_str(model_deployment_payload['lifecycle_state']) if 'lifecycle_state' in model_deployment_payload else State.UNKNOWN
                workflow_payload = self.ds_client.list_work_request_logs(self.workflow_req_id).data
                if isinstance(workflow_payload, list) and len(workflow_payload) > 0:
                    if prev_message != workflow_payload[-1].message:
                        for _ in range(len(workflow_payload) - prev_workflow_stage_len):
                            progress.update(workflow_payload[-1].message)
                        prev_workflow_stage_len = len(workflow_payload)
                        prev_message = workflow_payload[-1].message
                        prev_workflow_stage_len = len(workflow_payload)
                if prev_state != self.current_state.name:
                    if 'model_deployment_url' in model_deployment_payload:
                        self.url = model_deployment_payload['model_deployment_url']
                    utils.get_logger().info(f"Status Update: {self.current_state.name} in {utils.seconds_since(start_time)} seconds")
                time.sleep(poll_interval)

    @staticmethod
    def format_datetime(dt: datetime.datetime) -> str:
        """Converts datetime object to RFC3339 date time format in string
        """
        return dt.isoformat()[:-3] + "Z"

    def logs(self, time_start=None, time_end=None, limit=100, log_type="access"):
        """Gets the access or predict logs.

        Args:
            time_start (str or datetime.datetime, optional): Starting date and time in RFC3339 format string or
                datetime object for retrieving logs.
                If this is set to None, the end time will default to the current time.
            time_end (str or datetime.datetime, optional): Ending date and time in RFC3339 format or
                datetime object for retrieving logs.
                If this is set to None, the start time will default to 14 days before the current time.
            limit (int, optional): The maximum number of items to return. Defaults to 100.
            log_type (str, optional): "access" or "predict". Defaults to "access".

        Returns:
            list: A list of oci.loggingsearch.models.SearchResult

        Raises:
            AttributeError: When deployment does not have logging configured.
        """
        if not self.log_search_client:
            raise AttributeError(
                "Log search is not available. "
                "It is recommended that you initialize a ModelDeployment object using a DataScienceClient instance."
            )
        if not self.properties.category_log_details or not getattr(self.properties.category_log_details, log_type):
            raise AttributeError(f"Deployment {self.model_deployment_id} has no {log_type} log configuration.")
        
        # Default time_start and time_end
        if time_start is None:
            time_start = datetime.datetime.utcnow() - datetime.timedelta(days=14)
        if time_end is None:
            time_end = datetime.datetime.utcnow()

        # Converts datetime objects to RFC3339 format
        if isinstance(time_start, datetime.datetime):
            time_start = self.format_datetime(time_start)
        if isinstance(time_end, datetime.datetime):
            time_end = self.format_datetime(time_end)

        log_details = getattr(self.properties.category_log_details, log_type)

        search_details = oci.loggingsearch.models.SearchLogsDetails(
            # time_start cannot be more than 14 days older
            time_start=time_start,
            time_end=time_end,
            # https://docs.oracle.com/en-us/iaas/Content/Logging/Reference/query_language_specification.htm
            # Double quotes must be used for "<log_stream>" after search
            # Single quotes must be used for the string in <where_expression>
            # source = <OCID> is not allowed but source = *<OCID> works
            search_query=f'SEARCH "{self.properties.compartment_id}/{log_details.log_group_id}/{log_details.log_id}" '
                f'| WHERE source = \'*{self.model_deployment_id}\'',
            # is_return_field_info=True
        )
        return self.log_search_client.search_logs(search_details, limit=limit).data.results

    def show_logs(self, time_start=None, time_end=None, limit=100, log_type="access"):
        """Shows deployment logs as a pandas dataframe

        Args:
            time_start (str, optional): Starting date and time in RFC3339 format for retrieving logs.
                Defaults to None. Logs will be retrieved 14 days from now.
            time_end (str, optional): Ending date and time in RFC3339 format for retrieving logs.
                Defaults to None. Logs will be retrieved until now.
            limit (int, optional): The maximum number of items to return. Defaults to 100.
            log_type (str, optional): "access" or "predict". Defaults to "access".

        Returns:
            a pandas DataFrame containing logs.

        """
        def prepare_log_record(log):
            """Converts a log record to ordered dict
            """
            return collections.OrderedDict([
                ("id", log.get("id")),
                ("time", log.get("time")),
                ("message", log.get("logContent", {}).get("data", {}).get("message")),
                ("subject", log.get("subject")),
                ("source", log.get("source"))
            ])

        logs = self.logs(time_start=time_start, time_end=time_end, limit=limit, log_type=log_type)
        # log data are stored in the data attribute of oci.loggingsearch.models.SearchResult
        return pd.DataFrame([prepare_log_record(log.data) for log in logs])
