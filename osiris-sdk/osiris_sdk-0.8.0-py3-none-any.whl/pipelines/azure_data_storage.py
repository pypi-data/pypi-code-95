"""
Module to handle datasets IO
"""
import logging
from io import BytesIO
from typing import Tuple, Optional

from azure.core.exceptions import HttpResponseError

from ..core.azure_client_authorization import ClientAuthorization
from ..core.io import OsirisFileClient, OsirisFileClientAsync, PrometheusClient

logger = logging.getLogger(__name__)


class Dataset:
    """
    Generic Dataset class to represent a file GUID, with generic read and upload file.
    """
    # pylint: disable=too-many-arguments
    def __init__(self,
                 client_auth: ClientAuthorization,
                 account_url: str,
                 filesystem_name: str,
                 guid: str,
                 prometheus_client: Optional[PrometheusClient] = None):

        self.client_auth = client_auth
        self.account_url = account_url
        self.filesystem_name = filesystem_name
        self.guid = guid
        self.prometheus_client = prometheus_client

    def get_configuration(self) -> Tuple[ClientAuthorization, str, str, str]:
        """
        Get the configuration of a Datsset.
        """
        return self.client_auth, self.account_url, self.filesystem_name, self.guid

    def read_file(self, file_path: str) -> bytes:
        """
        Read events from destination corresponding a given date
        """
        file_path = f'{self.guid}/{file_path}'

        with OsirisFileClient(self.account_url,
                              self.filesystem_name, file_path,
                              credential=self.client_auth.get_credential_sync(),
                              prometheus_client=self.prometheus_client) as file_client:

            download_file = file_client.download_file()
            return download_file.readall()

    async def read_file_async(self, file_path: str) -> bytes:
        """
        Read events from destination corresponding a given date
        """
        file_path = f'{self.guid}/{file_path}'

        async with self.client_auth.get_credential_async() as credentials:
            async with OsirisFileClientAsync(self.account_url,
                                             self.filesystem_name, file_path,
                                             credential=credentials,
                                             prometheus_client=self.prometheus_client) as file_client:

                downloaded_file = await file_client.download_file()
                data = await downloaded_file.readall()
                return data

    def upload_file(self, file_path: str, data: BytesIO):
        """
        Uploads a io.BytesIO stream to storage
        """
        file_path = f'{self.guid}/{file_path}'

        with OsirisFileClient(self.account_url,
                              self.filesystem_name,
                              file_path,
                              credential=self.client_auth.get_credential_sync(),
                              prometheus_client=self.prometheus_client) as file_client:
            try:
                file_client.upload_data(data, overwrite=True)
            except HttpResponseError as error:
                message = f'({type(error).__name__}) Problems uploading data file({file_path}): {error}'
                logger.error(message)
                raise Exception(message) from error

    async def upload_file_async(self, file_path: str, data: BytesIO):
        """
        Uploads a io.BytesIO stream to storage
        """
        file_path = f'{self.guid}/{file_path}'

        async with self.client_auth.get_credential_async() as credentials:
            async with OsirisFileClientAsync(self.account_url,
                                             self.filesystem_name,
                                             file_path,
                                             credential=credentials,
                                             prometheus_client=self.prometheus_client) as file_client:
                try:
                    await file_client.upload_data(data, overwrite=True)
                except HttpResponseError as error:
                    message = f'({type(error).__name__}) Problems uploading data file({file_path}): {error}'
                    logger.error(message)
                    raise Exception(message) from error
