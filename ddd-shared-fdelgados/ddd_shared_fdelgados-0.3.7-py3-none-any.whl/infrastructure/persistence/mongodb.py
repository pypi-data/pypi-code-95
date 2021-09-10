import abc
from typing import Optional, List

from pymongo import MongoClient

from shared_context.domain.model import AggregateRoot, Repository


class MongoDbRepository(Repository, metaclass=abc.ABCMeta):
    def __init__(
        self,
        database: str,
        collection: str,
        username: str,
        password: str,
        host: Optional[str] = 'localhost',
        port: Optional[int] = 27017
    ):
        self._database = database
        self._collection = collection

        self._client = MongoClient(
            host,
            port=port,
            username=username,
            password=password,
            authSource=self._database
        )

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def database(self):
        return self.client[self._database]

    @property
    def collection(self):
        database = self.database

        return database[self._collection]

    def add(self, aggregate: AggregateRoot) -> None:
        pass

    def save(self, aggregate: AggregateRoot) -> None:
        pass

    def find(self, **kwargs) -> AggregateRoot:
        pass

    def find_all(self, **kwargs) -> List[AggregateRoot]:
        pass
