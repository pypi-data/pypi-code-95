# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
The main class in this module is the RecordConnector, with other
members auxilliary to it. See docstring of class RecordConnector.
"""

import logging

logger = logging.getLogger(__name__)

from .rest_api_client.client import Client
from .rest_api_client.models.record_read import RecordRead


class RecordConnector:
    """
    Instances of this class are a means to interact with a record stored
    or to-be-stored on the (remote) data repository.
    """

    def __init__(self, *, client: Client, record: RecordRead):
        self._client = client
        self._record = record
