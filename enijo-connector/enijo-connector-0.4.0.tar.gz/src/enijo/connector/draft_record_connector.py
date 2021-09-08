# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
The main class in this module is the DraftRecordConnector, with other
members auxilliary to it. See docstring of class RecordConnector.
"""

import logging

logger = logging.getLogger(__name__)

from enijo.connector.draft_file_connector import DraftFileConnector
from enijo.connector.record_connector import RecordConnector
from enijo.connector.rest_api_client.api.draft_files import (
    records_id_draft_files_list,
    records_id_draft_files_post,
)
from enijo.connector.rest_api_client.api.drafts import (
    records_id_draft_actions_publish_post,
)
from enijo.connector.rest_api_client.client import Client
from enijo.connector.rest_api_client.models.draft_files_create_item import (
    DraftFilesCreateItem,
)
from enijo.connector.rest_api_client.models.record_read import RecordRead


class DraftRecordConnector:
    """
    Instances of this class are a means to interact with a record stored
    or to-be-stored on the (remote) data repository.
    """

    def __init__(self, *, client: Client, record: RecordRead):
        self._client = client
        self._record = record

    def create_draft_file(self, filename: str) -> DraftFileConnector:
        """
        adds another file to this draft record.

        Args:
            filename: specify the filename

        Returns:
            the file connector to the created draft file
        """
        body = [DraftFilesCreateItem.from_dict({"key": filename})]
        r = records_id_draft_files_post.sync_detailed(
            client=self._client, id=self._record.id, json_body=body
        )
        logger.debug("response: %s", r)
        if 201 != r.status_code:
            raise "FIXME"
        return DraftFileConnector(
            client=self._client, record=self._record, filename=filename, file=r.parsed
        )

    def list_files(self) -> DraftFileConnector:
        """
        lists all files of this record
        """
        r = records_id_draft_files_list.sync_detailed(
            client=self._client, id=self._record.id
        )
        logger.debug("response: %s", r)

    def publish(self) -> RecordConnector:
        """
        publishes this draft record and returns the record connector
        to the now published record.
        """
        r = records_id_draft_actions_publish_post.sync_detailed(
            client=self._client, id=self._record.id
        )
        logger.debug("response: %s", r)
        if 400 == r.status_code:
            raise Exception("validation errors", r.parsed)

        print(DraftFileConnector)
        print(RecordConnector)

        return RecordConnector(client=self._client, record=r.parsed)
