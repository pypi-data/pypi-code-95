# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
package description
"""

from __future__ import annotations

import io

from .data_repository_connector import DataRepositoryConnector
from .file_connector import FileConnector
from .rest_api_client.models.record_new import RecordNew

# optional dependencies:
try:
    import pandas
except:
    pandas = None


#: constant holding the (as of 2021) current URL of the University of
#: Technology Vienna's (TUWIEN) data repository.
AT_AC_TUWIEN_RESEARCHDATA = "https://researchdata.tuwien.ac.at/api"


#: constant holding the (as of 2021) current URL of the University of
#: Technology Vienna's (TUWIEN) data repository test system.
AT_AC_TUWIEN_RESEARCHDATA_TEST = "https://test.researchdata.tuwien.ac.at/api"


class EnijoConnector:
    """
    This class provides all-in-one methods for common use-cases, and
    does **not** strive to support all valid actions or all valid
    combination of arguments.

    See class ``DataRepositoryConnector`` for a more direct interface
    with the data repository. See method ``data_repository()`` for one
    way to aquire an instance of the data repository connector.
    """

    def __init__(self):
        self._datarepo = DataRepositoryConnector()

    def data_repository_connector(self) -> DataRepositoryConnector:
        """
        Returns:
            The internal data repository connector used. Interfacing
            directly with the data repository is more verbose.
        """
        return self._datarepo

    def set_repository_url(self, url: str) -> EnijoConnector:
        """
        Set base url information from the given url.

        Previously set url information is replaced.

        Args:
            url (str): The base URL of the data repository.

        Returns:
            *self*
        """
        self._datarepo.set_repository_url(url)
        return self

    def set_auth_token(self, token: str) -> EnijoConnector:
        """
        Set authentication information from the given api token.

        Previously set authentication information is replaced.

        Args:
            token (str): The API token (a ``Bearer`` OAuth2 token)
                specific for each user.

        Returns:
            *self*
        """
        self._datarepo.set_auth_token(token)
        return self

    def publish_data_as_record(
        self, *, record: RecordNew, data, filename: str
    ) -> RecordConnector:
        """
        Args:
            record: specify a new record or an existing record.
                If a new record is specified, using an argument of type
                RecordNew, a new record is created on the remote data
                repository. If an existing record is specified, not
                implemented yet, a new record is created on the remote
                data repository which is the next version of the
                specified record.
            data: specify the data to be converted and uploaded.
                If data is of type ``pandas.DataFrame``, it is
                converted to CSV format and then encoded with UTF-8.
                If data is of type ``str``, it is encoded with UTF-8.
                If data is of type ``bytes``, it is directly uploaded.
            filename: specify the filename to be assigned to the
                uploaded data. Note: the actual filename might be
                minimally different (e.g. disallowed characters).

        Returns:
            A RecordConnector instance, connected to the created record.
        """
        if not isinstance(record, RecordNew):
            raise NotImplementedError(
                "only record type ``RecordNew`` support at the moment"
            )
        draft_record = self._datarepo.create_draft_record(record=record)
        draft_file = draft_record.create_draft_file(filename=filename)
        draft_file.upload_content(data)
        record = draft_record.publish()
        return record

    def download_record_file(
        self, *, record_id: str, filename: str = None, data_type=None
    ):
        """
        Download the content of a previously uploaded file of a
        previously published record.

        Args:
            record_id: The id of the record to access. Note, that
                multiple versions of the same record all have a
                different record_id.
            filename: If the record has multiple files, specify the
                filename to download. If not specified, or None, then
                the first file will be downloaded -- This is
                recommended if the record only has a single file.
            data_type: If ``None``, the default, no conversion is
                performed and the file content is returned as
                ``bytes``. If ``str``, the file content is decoded with
                UTF-8 and returned. If ``pandas.DataFrame``, then the
                file content is converted from CSV format into a
                pandas.DataFrame object, and then returned.
                The csv to data frame conversion is guaranteed to
                succeed, if the previous data frame to csv conversion
                was performed by methods of the enijo.connector project,
                such as the ``publish_data_as_record()`` method in
                this class.

        Returns:
            The file-content according to parameter data_type.
        """
        file = FileConnector(
            client=self._datarepo._get_client(), record_id=record_id, filename=filename
        )
        content = file.get_content()
        if issubclass(data_type, str):
            return content.decode("utf-8")
        elif None != pandas and issubclass(data_type, pandas.DataFrame):
            content = content.decode("utf-8")
            content = io.StringIO(content)
            return pandas.read_csv(content)
        else:
            return content
