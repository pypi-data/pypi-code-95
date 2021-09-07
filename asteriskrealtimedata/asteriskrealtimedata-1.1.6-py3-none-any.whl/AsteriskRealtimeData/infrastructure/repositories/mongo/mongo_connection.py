from typing import Any
from antidote import service
from AsteriskRealtimeData.environments import Config
from pymongo import MongoClient
from pymongo.database import Database

from AsteriskRealtimeData.infrastructure.repositories.connection_interface import Connection


@service(singleton=True)
class MongoConnection(Connection):
    _database_connection: Any

    def __init__(self) -> None:
        super().__init__()
        self.connect(
            self.getHost(), self.getPort(), self.getUser(), self.getPassword(), self.getDatabase(),
        )

    def connect(self, host: str, port: int, user: str, password: str, database: str) -> None:
        self._database_connection = Database(
            MongoClient(host=[host], document_class=dict, tz_aware=False, connect=True), database,
        )

    def get_connection(self) -> Any:
        return self._database_connection

