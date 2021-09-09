"""
Contains Osiris common IO functions
"""
from datetime import datetime
from typing import Any, Optional, Union, AnyStr, Iterable, IO, Dict

from azure.storage.blob import ContentSettings, StorageStreamDownloader
from azure.storage.blob.aio import StorageStreamDownloader as StorageStreamDownloaderAsync
from azure.storage.filedatalake.aio import DataLakeFileClient as DataLakeFileClientAsync
from azure.storage.filedatalake import DataLakeFileClient
from prometheus_client import CollectorRegistry, Counter, push_to_gateway

import pandas as pd

from .enums import TimeResolution


def get_directory_path_with_respect_to_time_resolution(date: datetime, time_resolution: TimeResolution):
    """
    Returns the directory path which corresponds to the given time resolution. The GUID directory is not included!
    """
    if time_resolution == TimeResolution.NONE:
        return ''
    if time_resolution == TimeResolution.YEAR:
        return f'year={date.year}/'
    if time_resolution == TimeResolution.MONTH:
        return f'year={date.year}/month={date.month:02d}/'
    if time_resolution == TimeResolution.DAY:
        return f'year={date.year}/month={date.month:02d}/day={date.day:02d}/'
    if time_resolution == TimeResolution.HOUR:
        return f'year={date.year}/month={date.month:02d}/day={date.day:02d}/' + \
               f'hour={date.hour:02d}/'
    if time_resolution == TimeResolution.MINUTE:
        return f'year={date.year}/month={date.month:02d}/day={date.day:02d}/' + \
               f'hour={date.hour:02d}/minute={date.minute:02d}/'

    message = '(ValueError) Unknown time resolution giving.'
    raise ValueError(message)


def get_file_path_with_respect_to_time_resolution(date: datetime, time_resolution: TimeResolution, filename: str):
    """
    Returns the file path which corresponds to the given time resolution. The GUID directory is not included!
    """
    return f'{get_directory_path_with_respect_to_time_resolution(date, time_resolution)}{filename}'


def parse_date_str(date_str):
    """
    Returns the datetime and time resolution of the given date_str.
    """
    try:
        if len(date_str) == 0:
            return None, TimeResolution.NONE
        if len(date_str) == 4:
            return pd.to_datetime(date_str, format='%Y'), TimeResolution.YEAR
        if len(date_str) == 7:
            return pd.to_datetime(date_str, format='%Y-%m'), TimeResolution.MONTH
        if len(date_str) == 10:
            return pd.to_datetime(date_str, format='%Y-%m-%d'), TimeResolution.DAY
        if len(date_str) == 13:
            return pd.to_datetime(date_str, format='%Y-%m-%dT%H'), TimeResolution.HOUR
        if len(date_str) == 16:
            return pd.to_datetime(date_str, format='%Y-%m-%dT%H:%M'), TimeResolution.MINUTE

        raise ValueError('Wrong string format for date')
    except ValueError as error:
        raise ValueError('Wrong string format for date: ', error) from error


class PrometheusClient:
    """
    A singleton class to ensure one instance of the class variables.
    """
    def __init__(self, environment: str, name: str, hostname: str, job_name: Optional[str] = None):
        self.environment = environment
        self.name = name
        self.hostname = hostname
        if job_name:
            self.job_name = job_name
        else:
            self.job_name = 'empty/job/name'

        self.registry = None
        self.counter = None

    def get_configuration(self):
        """
        Get the configuration
        """
        return self.environment, self.name, self.hostname, self.job_name

    def get_registry(self):
        """
        Get registry
        """
        if self.registry is None:
            self.registry = CollectorRegistry()
        return self.registry

    def get_counter(self):
        """
        Get counter
        """
        if self.counter is None:
            self.counter = Counter('transform_method',
                                   'Transformation Pipeline',
                                   ['method', 'environment', 'transformation'],
                                   registry=self.get_registry())
        return self.counter


class OsirisFileClient(DataLakeFileClient):
    """
    OsirisFileClient is a synchronous file client wrapping the DataLakeFileClient.
    This is to have metrics of Azure Storage transparent for the user.
    """
    # pylint: disable=too-many-arguments
    def __init__(self,
                 account_url: str,
                 file_system_name: str,
                 file_path: str,
                 credential: Optional[Any] = None,
                 prometheus_client: Optional[PrometheusClient] = None,
                 **kwargs: Any
                 ):
        super().__init__(account_url, file_system_name, file_path, credential, **kwargs)

        self.prometheus_client = prometheus_client

        if prometheus_client:
            environment, name, hostname, job_name = prometheus_client.get_configuration()
            self.environment = environment
            self.name = name
            self.hostname = hostname
            self.job_name = job_name

            self.counter = prometheus_client.get_counter()
            self.registry = prometheus_client.get_registry()

    def __del__(self):
        if self.prometheus_client and self.environment in ['prod', 'test']:
            push_to_gateway(self.hostname, job=self.job_name, registry=self.registry)

    def create_file(self,
                    content_settings: Optional[ContentSettings] = None,
                    metadata: Optional[Dict[str, str]] = None,
                    **kwargs: Any):
        if self.prometheus_client:
            self.counter.labels('create_file', self.environment, self.name).inc()
        return super().create_file(content_settings, metadata, **kwargs)

    def delete_file(self, **kwargs: Any):
        if self.prometheus_client:
            self.counter.labels('delete_file', self.environment, self.name).inc()
        return super().delete_file(**kwargs)

    def upload_data(self, data: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]],
                    length: Optional[int] = None,
                    overwrite: Optional[bool] = False,
                    **kwargs):
        if self.prometheus_client:
            self.counter.labels('upload_data', self.environment, self.name).inc()
        return super().upload_data(data, length, overwrite, **kwargs)

    def download_file(self,
                      offset: Optional[int] = None,
                      length: Optional[int] = None,
                      **kwargs: Any) -> StorageStreamDownloader:
        if self.prometheus_client:
            self.counter.labels('download_file', self.environment, self.name).inc()
        return super().download_file(offset, length, **kwargs)

    def rename_file(self, new_name: str, **kwargs: Any):
        if self.prometheus_client:
            self.counter.labels('rename_file', self.environment, self.name).inc()
        return super().rename_file(new_name, **kwargs)


class OsirisFileClientAsync(DataLakeFileClientAsync):
    """
    OsirisFileClientAsync is a asynchronous file client wrapping the DataLakeFileClientAsync.
    This is to have metrics of Azure Storage transparent for the user.
    """
    # pylint: disable=too-many-arguments
    def __init__(self,
                 account_url: str,
                 file_system_name: str,
                 file_path: str,
                 credential: Optional[Any] = None,
                 prometheus_client: Optional[PrometheusClient] = None,
                 **kwargs: Any
                 ):
        super().__init__(account_url, file_system_name, file_path, credential, **kwargs)

        self.prometheus_client = prometheus_client

        if prometheus_client:
            environment, name, hostname, job_name = prometheus_client.get_configuration()
            self.environment = environment
            self.name = name
            self.hostname = hostname
            self.job_name = job_name

            self.counter = prometheus_client.get_counter()
            self.registry = prometheus_client.get_registry()

    def __del__(self):
        if self.prometheus_client and self.environment in ['prod', 'test']:
            push_to_gateway(self.hostname, job='transform/dmi_weather', registry=self.registry)

    async def create_file(self,
                          content_settings: Optional[ContentSettings] = None,
                          metadata: Optional[Dict[str, str]] = None,
                          **kwargs: Any):
        if self.prometheus_client:
            self.counter.labels('create_file', self.environment, self.name).inc()
        return await super().create_file(content_settings, metadata, **kwargs)

    async def delete_file(self, **kwargs: Any):
        if self.prometheus_client:
            self.counter.labels('delete_file', self.environment, self.name).inc()
        return await super().delete_file(**kwargs)

    async def upload_data(self,
                          data: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]],
                          length: Optional[int] = None,
                          overwrite: Optional[bool] = False,
                          **kwargs: Any):
        if self.prometheus_client:
            self.counter.labels('upload_data', self.environment, self.name).inc()
        return await super().upload_data(data, length, overwrite, **kwargs)

    async def download_file(self,
                            offset: Optional[int] = None,
                            length: Optional[int] = None,
                            **kwargs: Any) -> StorageStreamDownloaderAsync:
        if self.prometheus_client:
            self.counter.labels('download_file', self.environment, self.name).inc()
        return await super().download_file(offset, length, **kwargs)

    async def rename_file(self,
                          new_name: str,
                          **kwargs: Any):
        if self.prometheus_client:
            self.counter.labels('rename_file', self.environment, self.name).inc()
        return await super().rename_file(new_name, **kwargs)
