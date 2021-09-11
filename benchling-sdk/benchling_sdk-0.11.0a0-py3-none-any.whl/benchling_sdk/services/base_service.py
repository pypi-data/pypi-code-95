from abc import ABC

from benchling_api_client.client import Client
from benchling_sdk.helpers.retry_helpers import RetryStrategy


class BaseService(ABC):
    _client: Client
    _retry_strategy: RetryStrategy

    def __init__(self, client: Client, retry_strategy: RetryStrategy = RetryStrategy()):
        self._client = client
        self._retry_strategy = retry_strategy

    @property
    def client(self) -> Client:
        return self._client

    @property
    def retry_strategy(self) -> RetryStrategy:
        return self._retry_strategy
