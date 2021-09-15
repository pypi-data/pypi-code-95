import logging
from typing import IO, Union
from urllib.parse import quote

import requests

from .enums import FileType

_api_base_url = "https://firebasestorage.googleapis.com/v0/b/"
logger = logging.getLogger(__name__)


def _get_download_url(uri: str) -> str:
    if not uri.startswith('gs://'):
        raise ValueError(f'{uri} is not URI for Google Cloud Storage.')
    bucket_name = uri.split('/')[2]
    path = uri.replace(f'gs://{bucket_name}/', '')
    quoted_path = quote(path, safe='')
    return f'{_api_base_url}{bucket_name}/o/{quoted_path}?alt=media'


def _get_upload_url(uri: str) -> str:
    if not uri.startswith('gs://'):
        raise ValueError(f'{uri} is not URI for Google Cloud Storage.')
    bucket_name = uri.split('/')[2]
    path = uri.replace(f'gs://{bucket_name}/', '')
    return _api_base_url + bucket_name + f'/o?name={path}'


def _raise_for_status(response: 'requests.Response') -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error(response.text)
        raise e


def download(file: 'IO', uri: str, id_token: str) -> None:
    """
    Download file.

    Args:
        file:
            IO object

        uri:
            URI for storage

        id_token:
            Firebase id-token
    """
    url = _get_download_url(uri)
    res = requests.get(
        url, stream=True, headers={'Authorization': f"Bearer {id_token}"}
    )
    _raise_for_status(res)
    file.write(res.content)


def upload(file: Union[IO, str], uri: str, filetype: 'FileType', id_token: str) -> None:
    """
    Upload file.

    Args:
        file:
            IO object or path to file

        uri:
            URI for storage

        id_token:
            Firebase id-token
    """
    file_object: IO
    if isinstance(file, str):
        file_object = open(file, 'rb')
    else:
        file_object = file
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": filetype.value,
    }
    url = _get_upload_url(uri)
    res = requests.post(url, headers=headers, data=file_object)
    _raise_for_status(res)
