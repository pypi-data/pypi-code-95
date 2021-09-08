# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
The main class in this module is the FileConnector, with other
members auxilliary to it. See docstring of class FileConnector.
"""

from .exceptions import InvalidServerException
from .rest_api_client.api.record_files import records_id_files_filename_content_get
from .rest_api_client.client import Client


class FileConnector:
    """
    Instances of this class are a means to interact with a file stored
    or to-be-stored on the (remote) data repository.
    """

    def __init__(self, *, client: Client, record_id: str, filename: str):
        self._client = client
        self._record_id = record_id
        self._filename = filename

    def get_content(self) -> bytes:
        """
        retrieve the binary content of this file.

        Returns:
            the binary content of this file
        """
        r = records_id_files_filename_content_get.sync_detailed(
            client=self._client, id=self._record_id, filename=self._filename
        )
        if 200 != r.status_code:
            raise InvalidServerException("invalid response from server", r)
        return r.content
