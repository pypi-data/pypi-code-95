from dataclasses import dataclass
from io import BytesIO
from typing import Any, Iterator, Optional, Tuple
from uuid import uuid4

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from common_client_scheduler import AwsCredentials


OBJECT_CHUNK_SIZE_BYTES = 200 * 1024 * 1024  # objects to copy are copied chunk by chunk


class ConfigS3:
    max_conns: int = 1000
    max_retries: int = 1
    connect_timeout: int = 5
    read_timeout: int = 5

    @classmethod
    def config(cls) -> Config:
        return Config(
            max_pool_connections=cls.max_conns,
            retries=dict(max_attempts=cls.max_retries),
            connect_timeout=cls.connect_timeout,
        )


class S3:
    # Authentication
    # ~~~~~~~~~~~~~~
    #
    # We use the S3 client in two configurations:
    # * local to S3 copies, or S3 to local copies (where S3 is a Terality owned bucket)
    # * S3 to S3 copies (between a user and a Terality owned bucket)
    #
    # While the user may have her own AWS credentials in her environment, we can't use them to write to
    # Terality buckets. Indeed, regardless of bucket policies, the user won't be able to perform a PutObject
    # (or CreateMultipartUpload) on a Terality bucket without a policy giving him "s3:PutObject" on said
    # bucket. Same goes for reads.
    #
    # Instead, whenever the client needs to perform a write or read operation on a Terality bucket,
    # it retrieves short-lived, temporary AWS credentials from the Terality API suitable for the operation.
    #
    # This is simpler than having the server generate pre-signed URLs, and provides the same level of
    # security.
    #
    # However, Terality-issued credentials can't be used to read or write S3 files to user buckets.
    _client: Any = None
    _client_with_credentials: Any = None
    _credentials: Optional[AwsCredentials] = None

    @classmethod
    def client(cls):
        """An S3 client using user credentials (using the default boto3 loading mecanism).

        Operations with this client will fail if the user has no AWS credentials available in their
        environment.
        """
        if cls._client is None:
            cls._client = boto3.session.Session().client(
                "s3", config=Config(max_pool_connections=200)
            )
        return cls._client

    @classmethod
    def client_from_credentials(cls, credentials: AwsCredentials):
        """An authenticated S3 client, with temporary credentials provided by Terality."""
        if cls._credentials != credentials:
            cls._client_with_credentials = boto3.session.Session().client(
                "s3",
                config=Config(max_pool_connections=200),
                aws_access_key_id=credentials.access_key_id,
                aws_secret_access_key=credentials.secret_access_key,
                aws_session_token=credentials.session_token,
            )
            cls._credentials = credentials
        return cls._client_with_credentials


_ACL = {"ACL": "bucket-owner-full-control"}


class DataTransfer:
    """
    Various functions to upload and download files to/from S3.

    These functions are defined as class methods to make writing mocks easier during testing.
    """

    @staticmethod
    def upload_bytes(upload_config, aws_credentials: AwsCredentials, data: BytesIO) -> str:
        data.seek(0)
        transfer_id = str(uuid4())
        key = f"{upload_config.key_prefix}{transfer_id}/0.data"
        S3.client_from_credentials(aws_credentials).upload_fileobj(
            Fileobj=data, Bucket=upload_config.bucket_region(), Key=key, ExtraArgs=_ACL
        )
        return transfer_id

    @staticmethod
    def upload_local_file(
        upload_config,
        aws_credentials: AwsCredentials,
        local_file: str,
        file_suffix: str,
    ) -> None:
        key = f"{upload_config.key_prefix}{file_suffix}"
        S3.client_from_credentials(aws_credentials).upload_file(
            Bucket=upload_config.bucket_region(),
            Key=key,
            Filename=local_file,
            ExtraArgs=_ACL,
        )

    @staticmethod
    def download_to_bytes(
        download_config, aws_credentials: AwsCredentials, transfer_id: str
    ) -> BytesIO:
        buf = BytesIO()
        key = f"{download_config.key_prefix}{transfer_id}/0.parquet"
        S3.client_from_credentials(aws_credentials).download_fileobj(
            Bucket=download_config.bucket_region(), Key=key, Fileobj=buf
        )
        return buf

    @staticmethod
    def download_to_local_files(
        download_config,
        aws_credentials: AwsCredentials,
        transfer_id: str,
        path: str,
        is_folder: bool,
    ) -> None:
        bucket = download_config.bucket_region()
        key_prefix = f"{download_config.key_prefix}{transfer_id}/"
        client = S3.client_from_credentials(aws_credentials)
        keys = [o[0] for o in list_all_objects_under_prefix(client, bucket, key_prefix)]
        if is_folder:
            for num, key in enumerate(keys):
                client.download_file(Bucket=bucket, Key=key, Filename=path.format(num))
        else:
            client.download_file(Bucket=bucket, Key=keys[0], Filename=path)


def list_all_objects_under_prefix(
    client: BaseClient, s3_bucket: str, s3_key_prefix: str
) -> Iterator[Tuple[str, int]]:
    """List all S3 keys in a bucket starting with a given prefix.

    Yield:
        tuples of (S3 object key, object size in bytes)
    """
    paginator = client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=s3_bucket, Prefix=s3_key_prefix)
    for page in page_iterator:
        objects = page["Contents"]
        for obj in objects:
            yield (obj["Key"], obj["Size"])


@dataclass
class ExportedS3File:
    """A S3 object stored in a Terality export bucket."""

    bucket: str
    key: str
    size_bytes: int
