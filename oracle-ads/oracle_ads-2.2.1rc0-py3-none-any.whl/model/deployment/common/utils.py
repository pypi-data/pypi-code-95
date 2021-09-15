#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/


"""Utilities used by the model deployment package
"""

# Standard lib

import logging
import os
import sys
import time
import yaml
import oci

from enum import Enum, auto
from oci.signer import Signer
from oci.util import get_signer_from_authentication_type, AUTHENTICATION_TYPE_FIELD_NAME
from .progress_bar import TqdmProgressBar, DummyProgressBar


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("ODSC-ModelDeployment")

def get_logger():
    return logger


def load_config(source=None):
    """Loads SDK config from YAML or dict

    Args:
        source (str or dict, optional): Path to config YAML or a dict containing the configurations. 
            Defaults to None. Source will be ignored if it is not str or dict.

    Returns:
        dict: Dictionary containing the configurations
    """
    # Empty config dict
    config = {}

    # source will be ignore if it is not str or dict
    if isinstance(source, dict):
        # source is dict
        config = source
    elif isinstance(source, str):
        # source is path to yaml file
        if "yaml" in source:
            with open(source) as cf:
                try:
                    config = yaml.load(cf, Loader=yaml.CLoader)
                except:
                    config = yaml.load(cf, Loader=yaml.Loader)
        else:
            logger.error("Pass in a valid config yaml file")
            raise ValueError(f"Not a valid yaml file: {source}")
    
    # Load service endpoint from environment variable if it is not specified in config
    # Default service endpoint in OCI SDK will be used if service endpoint is not in config or environment variables.
    if not config.get("OCI_ODSC_SERVICE_ENDPOINT") and os.environ.get("OCI_ODSC_SERVICE_ENDPOINT"):
        config["OCI_ODSC_SERVICE_ENDPOINT"] = os.environ["OCI_ODSC_SERVICE_ENDPOINT"]

    return config

def set_log_level(level="INFO"):
    """set_log_level sets the logger level

    Args:
        level (str, optional): The logger level. Defaults to "INFO"

    Returns:
        Nothing
    """

    level = logging.getLevelName(level)
    logger.setLevel(level)

def seconds_since(t):
    """seconds_since returns the seconds since `t`. `t` is assumed to be a time
    in epoch seconds since time.time() returns the current time in epoch seconds.

    Args:
        t (int) - a time in epoch seconds

    Returns
        int: the number of seconds since `t`
    """

    return time.time() - t

def is_notebook():
    """is_notebook returns True if the environment is a Jupyter notebook and 
    False otherwise

    Args:
        None

    Returns:
        bool: True if Jupyter notebook; False otherwise

    Raises:
        NameError: If retrieving the shell name from get_ipython() throws an error

    """

    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':  # pragma: no cover
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except ImportError:
        # IPython is not installed
        return False
    except NameError:
        return False  # Probably standard Python interpreter

def get_progress_bar(max_progress, description="Initializing"):
    """get_progress_bar return an instance of ProgressBar, sensitive to the runtime environment

    Args:
        max_progress (int): Progress bar max
        description (str, optional): Progress bar description (defaults to "Initializing")

    Returns:
        An instance of ProgressBar. Either a DummyProgressBar (non-notebook) or TqdmProgressBar 
        (notebook environement)
    """
    
    if is_notebook():  # pragma: no cover
        return TqdmProgressBar(max_progress, description=description, verbose=False)
    else:
        return DummyProgressBar()

# State Constants
class State(Enum):
    ACTIVE = auto()
    CREATING = auto()
    DELETED = auto()
    DELETING = auto()
    FAILED = auto()
    INACTIVE = auto()
    UPDATING = auto()
    UNKNOWN = auto()

    @staticmethod
    def _from_str(state):
        if state == None:
            return State.UNKNOWN
        elif state.upper() == "ACTIVE":
            return State.ACTIVE
        elif state.upper() == "CREATING":
            return State.CREATING
        elif state.upper() == "DELETED":
            return State.DELETED
        elif state.upper() == "DELETING":
            return State.DELETING
        elif state.upper() == "FAILED":
            return State.FAILED
        elif state.upper() == "INACTIVE":
            return State.INACTIVE
        elif state.upper() == "UPDATING":
            return State.UPDATING
        else:
            return State.UNKNOWN

    def __call__(self):
        # This will provide backward compatibility.
        # In previous release, ModelDeployment has state() as method instead of property
        return self

class OCIClientManager:
    """OCIClientManager is a helper class used for accessing DataScienceClient and
    DataScienceCompositeClient objects

    Attributes
    ----------
    ds_client - class attribute for data science client
    ds_composite_client - class attribute for data science composite client

    Methods
    -------
    oci_ds_client(config)
        returns the OCI DataScienceClient
    oci_ds_composite_client(ds_client)
        returns the OCI DataScienceCompositeClient
    """
    @staticmethod
    def get_oci_config_path_and_profile(sdk_config=None):
        """Determines the OCI config path and profile from SDK config

        Args:
            sdk_config (dict, optional): A dictionary containing MD SDK config. Defaults to None.

        Returns:
            dict: A dictionary containing file_path and/or profile if it is specified in the SDK config.
                This dictionary can be used as kwargs for oci.config.from_file(**kwargs)
        """
        if sdk_config is None:
            sdk_config = {}
        sdk_config = {k.lower(): v for k, v in sdk_config.items()}
        # Get API key config if signer is not obtained
        # Use default OCI config and profile when the value of oci_config_profile/oci_config_file is None or empty
        profile = sdk_config.get("oci_config_profile")
        file_path = sdk_config.get("oci_config_file")
        # Pass file_path/profile to oci.config.from_file only if there is value
        # OCI SDK will handle the default values.
        kwargs = {}
        if file_path:
            kwargs["file_path"] = file_path
        if profile:
            kwargs["profile"] = profile
        return kwargs

    @staticmethod
    def get_oci_config(sdk_config=None):
        oci_config = oci.config.from_file(**OCIClientManager.get_oci_config_path_and_profile(sdk_config))
        return oci_config

    @staticmethod
    def get_oci_config_signer(sdk_config=None):
        """Gets OCI signer from SDK config
        """
        oci_config = {}
        signer = None
        if not sdk_config:
            sdk_config = {}

        # Get resource principal signer if user specified resource principal as authentication method
        if sdk_config.get("auth") == "resource_principal":
            # EnvironmentError will be raise if resource principal is not available.
            signer = oci.auth.signers.get_resource_principals_signer()
            return oci_config, signer
        # Try to get signer from OCI config
        try:
            oci_config = OCIClientManager.get_oci_config(sdk_config)

            if AUTHENTICATION_TYPE_FIELD_NAME in oci_config:
                signer = get_signer_from_authentication_type(oci_config)
            else:
                signer = Signer.from_config(oci_config)
            return oci_config, signer
        except oci.exceptions.ConfigFileNotFound:
            if "OCI_API_KEYS" in sdk_config or sdk_config.get("auth") == "api_key":
                # If OCI_API_KEYS are specified in config,
                #   raise error to let user know config file is not found.
                raise

        # Try to get signer from resource principal only if OCI_API_KEYS are not specified in config
        try:
            signer = oci.auth.signers.get_resource_principals_signer()
        except EnvironmentError:
            raise EnvironmentError("Unable to obtain OCI credentials. Please setup API Keys.")

        return oci_config, signer

    @staticmethod
    def oci_ds_client(sdk_config=None):
        """ Returns the OCI DataScienceClient

        Returns:
            [DataScienceClient]: DataScienceClient
        """
        if not sdk_config:
            sdk_config = {}

        oci_config, signer = OCIClientManager().get_oci_config_signer(sdk_config)

        kwargs = {}
        if "OCI_ODSC_SERVICE_ENDPOINT" in sdk_config:
            kwargs["service_endpoint"] = sdk_config["OCI_ODSC_SERVICE_ENDPOINT"]

        ds_client = oci.data_science.DataScienceClient(
            oci_config,
            signer=signer,
            retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
            **kwargs
        )
        return ds_client

    @staticmethod
    def oci_ds_composite_client(ds_client):
        """oci_ds_composite_client returns the OCI DataScienceCompositeClient

        Args:
            ds_client (DataScienceClient): OCI DataScienceClient

        Returns:
            DataScienceCompositeClient: DataScienceCompositeClient
        """
        return oci.data_science.DataScienceClientCompositeOperations(ds_client)

    @staticmethod
    def default_compartment_id(config=None):
        """Determines the default compartment OCID
        This method finds the compartment OCID from environment variable, 
        API key config or resource principal signer.

        Parameters
        ----------
        config : dict, optional
            The model deployment config, which contains the following keys:
            auth: Authentication method, must be either "resource_principal" or "api_key".
            If auth is not specified:
                1. api_key will be used if available.
                2. If api_key is not available, resource_principal will be used.
            oci_config_file: OCI API key config file location. Defaults to "~/.oci/config"
            oci_config_profile: OCI API key config profile name. Defaults to "DEFAULT"

        Returns
        -------
        str or None
            The compartment OCID if found. Otherwise None.
        """
        # Try to get compartment ID from environment variable.')
        if os.environ.get('NB_SESSION_COMPARTMENT_OCID'):
            return os.environ.get('NB_SESSION_COMPARTMENT_OCID')
        # Try to get compartment ID from OCI config
        oci_config, singer = OCIClientManager.get_oci_config_signer(config)
        if oci_config.get("compartment_id"):
            return oci_config.get("compartment_id")
        if oci_config.get("tenancy"):
            return oci_config.get("tenancy")
        # Try to use tenancy OCID from RP signer
        if hasattr(singer, "tenancy_id") and getattr(singer, "tenancy_id"):
            return singer.tenancy_id
        return None

