# SPDX-License-Identifier: MIT
# Copyright 2021 Max-Julian Pogner <max-julian@pogner.at>
# Copyright 2021 Tobias Hajszan <tobias.hajszan@outlook.com>
# This file forms part of the 'enijo-connector' project, see the
# project's readme, notes, and other documentation for further details.

"""
Because openapi-python-client does not (yet) support some features,
this module provides these missing functions in a hacky way.

As soon as openapi-python-client supports these features, the functions
in this module shall be removed.
"""

import logging
from typing import Union

import httpx

from .rest_api_client.client import Client
from .rest_api_client.models.draft_files_read_entry import DraftFilesReadEntry
from .rest_api_client.types import Response, Unset

logger = logging.getLogger(__name__)


def draft_file_content_upload(
    *,
    client: Client,
    id: str,
    filename: str,
    content_type: Union[Unset, str] = "application/octet-stream",
    data: bytes
) -> Response[DraftFilesReadEntry]:
    """
    draft file content upload as required by Invenio RDM Api.
    """

    url = "{}/records/{id}/draft/files/{filename}/content".format(
        client.base_url, id=id, filename=filename
    )
    headers = client.get_headers()
    cookies = client.get_cookies()
    httpxargs = {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "data": data,
    }
    logger.info("httpx args: %s", httpxargs)
    response = httpx.put(**httpxargs)
    parsed = DraftFilesReadEntry.from_dict(response.json())
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=parsed,
    )
