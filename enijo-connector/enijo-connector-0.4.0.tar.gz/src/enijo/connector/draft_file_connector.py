# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
The main class in this module is the FileConnector, with other
members auxilliary to it. See docstring of class FileConnector.
"""

# Note: not used, as long as the file upload mode used by InvenioRDM is not
# yet supported by openapi-python-client
from .rest_api_client.api.draft_files import records_id_draft_files_filename_commit_post
from .rest_api_client.client import Client
from .rest_api_client.models.record_read import RecordRead

# Note: as replacement for not-yet openapi-python-client support
from .rest_api_client_extras import draft_file_content_upload

# optional dependencies:
try:
    import pandas
except:
    pandas = None


class DraftFileConnector:
    """
    Instances of this class are a means to interact with a file stored
    or to-be-stored on the (remote) data repository.
    """

    def __init__(self, *, client: Client, record: RecordRead, filename: str, file):
        self._client = client
        self._record = record
        self._filename = filename
        self._file = file
        for entry in file.entries:
            if entry.key == filename:
                self._entry = entry

    def upload_content(self, data):
        """
        Specify some data to upload as content to this draft file.
        Previous content will be replaced.

        The data can have different formats:

          * bytes ... the content is uploaded unaltered
          * str ... the str is utf-8 encoded into bytes and then processed
            as if bytes where given (see there).
          * pandas.DataFrame ... the data frame is converted into
            CSV (see xyz) and then processed as if str was given
            (see there).

        """
        if pandas and isinstance(data, pandas.DataFrame):
            data = data.to_csv()
        if isinstance(data, str):
            data = data.encode("UTF-8")
        if isinstance(data, bytes):
            content = data

        r = draft_file_content_upload(
            client=self._client,
            id=self._record.id,
            filename=self._filename,
            data=content,
        )
        if 200 != r.status_code:
            raise "FIXME"

        r = records_id_draft_files_filename_commit_post.sync_detailed(
            client=self._client, id=self._record.id, filename=self._filename
        )
