import logging
from typing import IO, Union

import requests

from .enums import FileType

logger = logging.getLogger(__name__)


def _raise_for_status(response: 'requests.Response'):
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error(response.text)
        raise e


def download(url: str, file: 'IO'):
    """
    Download file.

    Args:
        url:
            URL

        file:
            IO object
    """
    res = requests.get(url, stream=True)
    _raise_for_status(res)
    file.write(res.content)


def upload(file: Union[IO, str], url: str, filetype: 'FileType'):
    """
    Upload file.

    Args:
        file:
            IO object or path to file

        url:
            URL
    """
    file_object: IO
    if isinstance(file, str):
        file_object = open(file, 'rb')
    else:
        file_object = file
    headers = {
        "Content-Type": filetype.value,
    }
    res = requests.put(url, headers=headers, data=file_object)
    _raise_for_status(res)
