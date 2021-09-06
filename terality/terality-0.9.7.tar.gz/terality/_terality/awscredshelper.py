import time
from typing import Optional

from common_client_scheduler import AwsCredentials, DataTransferResponse

from .globals import global_client


class AwsCredentialsFetcher:
    """Small utility to lazily fetch temporary AWS credentials from the Terality API.

    `get_credentials` will fetch credentials on the first call, and cache the result.

    Those credentials are used to upload files to Terality-owned S3 buckets.
    """

    def __init__(self) -> None:
        self._credentials: Optional[AwsCredentials] = None
        self._credentials_fetched_at = time.monotonic()

    def get_credentials(self) -> AwsCredentials:
        if self._credentials is None or time.monotonic() > self._credentials_fetched_at + 30 * 60:
            self._fetch_credentials()
        assert self._credentials is not None
        return self._credentials

    def _fetch_credentials(self) -> None:
        res: DataTransferResponse = global_client().send_request("transfers", {})
        self._credentials = res.temporary_upload_aws_credentials
        self._credentials_fetched_at = time.monotonic()
