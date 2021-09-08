# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
The main class in this module is the DataRepositoryConnector, with other
members auxilliary to it. See docstring of class
DataRepositoryConnector.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Union

from enijo.connector.draft_record_connector import DraftRecordConnector
from enijo.connector.exceptions import InvalidServerException
from enijo.connector.record_connector import RecordConnector
from enijo.connector.rest_api_client.api.drafts import records_create
from enijo.connector.rest_api_client.api.records import records_id_get
from enijo.connector.rest_api_client.api.versions import records_id_versions_post
from enijo.connector.rest_api_client.client import AuthenticatedClient, Client
from enijo.connector.rest_api_client.models.record_new import RecordNew


class DataRepositoryConnector:
    """
    This is the main class, instances of which are interacting with an
    Invenio Data Repository.
    """

    def set_repository_url(self, url: str) -> DataRepositoryConnector:
        """
        Set base url information from the given url.

        Previously set url information is replaced.

        Args:
            url (str): The base URL of the data repository.

        Returns:
            *self*
        """
        self._repository_url = str(url)
        return self

    def set_auth_token(self, token: str) -> DataRepositoryConnector:
        """
        Set authentication information from the given api token.

        Previously set authentication information is replaced.

        Args:
            token (str): The API token (a ``Bearer`` OAuth2 token)
                specific for each user.

        Returns:
            *self*
        """
        self._auth_token = str(token)
        return self

    def get_record(self, id: str) -> RecordConnector:
        """
        Retrieve the record from the data repository.

        Returns:
            the retrieved record
        """
        c = self._get_client()
        r = records_id_get.sync_detailed(client=c, id=id)
        return RecordConnector(client=c, record=r.parsed)

    def get_record_draft(self, id: str) -> DraftRecordConnector:
        """
        Retrieve the next draft of a record from the data repository.

        Args:
            id: the record id (not the draft record id)

        Returns:
            the retrieved draft record
        """
        c = self._get_client()
        # Note: despite the strange naming, this is indeen the correct
        # operation in use:
        #
        # 1) this method is named 'get_record_draft', because its
        #    function is the retrieve the draft record of an existing
        #    record; with the record id specified by the caller.
        # 2) the used operation is called 'records_id_versions_post'
        #    due to the naming scheme, that the operation name is
        #    mindlessly derived from the URL and http-METHOD.
        #    Indeed, when reading the pre-existing InvenioRDM docu-
        #    mentation and
        r = records_id_versions_post.sync_detailed(client=c, id=id)
        return DraftRecordConnector(client=c, record=r.parsed)

    def create_draft_record(
        self, record: Union[RecordNew, Mapping] = None
    ) -> DraftRecordConnector:
        """
        Create a new stand-alone draft record in the data repository.

        Args:
            record: optionally specify the RecordNew instance to create.
                If not set, or None, will send the default RecordNew
                instance. If a dict-like object is given, it is
                converted by way of RecordNew.from_dict().

        Returns:
            the created draft record
        """
        if None == record:
            record = RecordNew()
        if not isinstance(record, RecordNew):
            record = RecordNew.from_dict(record)
        c = self._get_client()
        r = records_create.sync_detailed(client=c, json_body=record)
        if 201 != r.status_code:
            raise InvalidServerException("Server Malfunctions", record.to_dict(), r)
        return DraftRecordConnector(client=c, record=r.parsed)

    def _get_client(self) -> Client:
        """
        returns the current RestApiClient instance, with lazy
        initialization
        """
        if (
            not hasattr(self, "_client")
            or not self._client
            or self.__get_client_info[0] != (self._repository_url, self._auth_token)
        ):
            self._client = AuthenticatedClient(
                base_url=self._repository_url, token=self._auth_token
            )
            self.__get_client_info = (self._repository_url, self._auth_token)
        return self._client
