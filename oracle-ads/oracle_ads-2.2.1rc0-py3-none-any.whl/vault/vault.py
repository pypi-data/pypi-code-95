#!/usr/bin/env python
# -*- coding: utf-8 -*--

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import ast
import base64
import json
import oci
import uuid

from oci.vault import VaultsClientCompositeOperations
from oci.vault.models import Base64SecretContentDetails
from oci.vault.models import CreateSecretDetails
from oci.vault.models import UpdateSecretDetails

from ads.common import oci_client, auth
from ads.config import NB_SESSION_COMPARTMENT_OCID


class Vault:

    def __init__(self,
                 vault_id: str,
                 key_id: str,
                 compartment_id=None,
                 secret_client_auth=None,
                 vault_client_auth=None):
        self.id = vault_id
        self.key_id = key_id
        self.secret_client_auth = secret_client_auth if secret_client_auth else auth.default_signer()
        self.vault_client_auth = vault_client_auth if vault_client_auth else auth.default_signer()

        self.compartment_id = (
            NB_SESSION_COMPARTMENT_OCID if compartment_id is None else compartment_id
        )
        if not isinstance(self.compartment_id, str):
            raise ValueError("compartment_id needs to be a string.")

        if self.compartment_id is None:
            raise ValueError("compartment_id needs to be specified.")

        self.secret_client = oci_client.OCIClientFactory(**self.secret_client_auth).secret
        self.vaults_client_composite = VaultsClientCompositeOperations(oci_client.OCIClientFactory(**self.vault_client_auth).vault)

    def create_secret(self, value: dict, secret_name: str = None, description: str = None) -> str:
        """
        Saves value into vault as a secret.

        Parameters
        ----------
        value: dict
            The value to store as a secret.
        secret_name: str, optional
            The name of the secret.
        description: str, optional
            The description of the secret.

        Returns
        -------
        The secret ocid that correspond to the value saved as a secret into vault.
        """
        # Encode the secret.
        secret_content_details = self._encode_secret(value)

        # Bundle the secret and metadata about it.
        secrets_details = CreateSecretDetails(
            compartment_id=self.compartment_id,
            description=description if description is not None else "Data Science service secret",
            secret_content=secret_content_details,
            secret_name=secret_name if secret_name is not None else "DataScienceSecret_{}".format(str(uuid.uuid4())[-6:]),
            vault_id=self.id,
            key_id=self.key_id)

        # Store secret and wait for the secret to become active.
        secret = self.vaults_client_composite.create_secret_and_wait_for_state(
            create_secret_details=secrets_details,
            wait_for_states=[oci.vault.models.Secret.LIFECYCLE_STATE_ACTIVE]).data
        return secret.id

    def update_secret(self, secret_id: str, secret_content: dict) -> str:
        """
        Updates content of a secret.

        Parameters
        ----------
        secret_id: str
            The secret id where the stored secret will be updated.
        secret_content: dict,
            The updated content.

        Returns
        -------
        The secret ocid with updated content.
        """

        # Encode the secret.
        secret_content_details = self._encode_secret(secret_content)

        # Store the details to update.
        secrets_details = UpdateSecretDetails(secret_content=secret_content_details)

        # Create new secret version and wait for the new version to become active.
        secret_update = self.vaults_client_composite.update_secret_and_wait_for_state(
            secret_id,
            secrets_details,
            wait_for_states=[oci.vault.models.Secret.LIFECYCLE_STATE_ACTIVE]).data

        return secret_update.id

    def get_secret(self, secret_id: str) -> dict:
        """
        Retrieve secret content based on the secret ocid provided

        Parameters
        ----------
        secret_id: str
            The secret ocid.

        Returns
        -------
        The secret content as a dictionary.
        """
        secret_bundle = self.secret_client.get_secret_bundle(secret_id)
        secret_content = self._secret_to_dict(secret_bundle.data.secret_bundle_content.content)
        return ast.literal_eval(secret_content)

    def _encode_secret(self, secret_content):
        secret_content_details = Base64SecretContentDetails(
            content_type=oci.vault.models.SecretContentDetails.CONTENT_TYPE_BASE64,
            stage=oci.vault.models.SecretContentDetails.STAGE_CURRENT,
            content=self._dict_to_secret(secret_content))
        return secret_content_details

    @staticmethod
    def _dict_to_secret(values):
        return base64.b64encode(json.dumps(values).encode('ascii')).decode("ascii")

    @staticmethod
    def _secret_to_dict(secret_content):
        return base64.b64decode(secret_content.encode('ascii')).decode('ascii')
