#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import oci
import os
from ads.common import utils

def api_keys(oci_config: str = os.path.join(os.path.expanduser('~'), '.oci','config'),
             profile: str = "DEFAULT",
             kwargs: dict = None
                   ) -> str:
    r"""Prepares authentication and extra arguments necessary for creating clients for different OCI services using API
    Keys.

    Parameters
    ----------
    oci_config : str
        OCI authentication config file location. Default is $HOME/.oci/config.
    profile : str
        Profile name to select from the config file. The defautl is DEFAULT
    kwargs : dict
        kwargs that are required to instantiate the Client if we need to override the defaults.

    Returns
    -------
    dict
        Contains keys - config, signer and extra_args. 
         * The config contains the config loaded from the configuration loaded from `oci_config`. 
         * The signer contains the signer object created from the api keys.
         * extra_args contains the `kwargs` that was passed in as input parameter.
    """
    configuration = oci.config.from_file(oci_config)
    return {
        "config": configuration,
        "signer": oci.signer.Signer(configuration['tenancy'], configuration['user'], configuration['fingerprint'], configuration['key_file'], configuration['pass_phrase']),
        "extra_args": kwargs
    }

def resource_principal(kwargs = None):
    r"""Prepares authentication and extra arguments necessary for creating clients for different OCI services using
    Resource Principals.

    Parameters
    ----------
    kwargs : dict
        kwargs that are required to instantiate the Client if we need to override the defaults.

    Returns
    -------
    dict
        Contains keys - config, signer and extra_args. 
         * The config contains and empty dictionary. 
         * The signer contains the signer object created from the resource principal.
         * extra_args contains the `kwargs` that was passed in as input parameter.
    """
    return {
        "config": {},
        "signer": oci.auth.signers.get_resource_principals_signer(),
        "extra_args": kwargs
    }

def default_signer(kwargs = None):
    r"""Prepares authentication and extra arguments necessary for creating clients for different OCI services based on
    the default authentication setting for the session. Refer ads.set_auth API for further reference..

    Parameters
    ----------
    kwargs : dict
        kwargs that are required to instantiate the Client if we need to override the defaults.

    Returns
    -------
    dict
        Contains keys - config, signer and extra_args. 
         * The config contains the config loaded from the configuration loaded from the default location if the default
         auth mode is API keys, otherwise it is empty dictionary. 
         * The signer contains the signer object created from default auth mode.
         * extra_args contains the `kwargs` that was passed in as input parameter.
    """
    if utils.is_resource_principal_mode():
        return resource_principal(kwargs)
    else:
        return api_keys(kwargs = kwargs)


