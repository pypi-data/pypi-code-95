from montydb import MontyClient, set_storage
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


class ConnectionError(Exception):
    pass


class Database:

    """
    Initialize the database. All this class really does is decide whether to use MontyClient or MongoClient.
    Used for when the user does not have mongodb installed.
    """

    def __init__(self, dbName: str, **kwargs):

        # Parameters
        self.connectionString = kwargs.get("connectionString")
        self.dbPath = kwargs.get("dbPath", "./db")
        self.logging = kwargs.get("logging")
        self.dbName = dbName

        self.client = None
        self.db = None
        self.type = "tinydb"

        if self.connectionString:
            try:
                self.client = MongoClient(
                    self.connectionString, serverSelectionTimeoutMS=2000
                )
                self.db = self.client[self.dbName]
                self.client.server_info()
                self.type = "mongo"

                if self.logging:
                    self.logging.success("Successfully connected to mongodb.")
            except ServerSelectionTimeoutError:
                if self.logging:
                    self.logging.warning(
                        "Failed to connect to mongodb, falling back to tinydb."
                    )

        if self.type == "tinydb":
            try:
                set_storage(self.dbPath, cache_modified=5)
                self.client = MontyClient(self.dbPath)
                self.db = self.client[self.dbName]

                if self.logging:
                    self.logging.success("Successfully connected to tinydb.")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to tinydb. ({e})")
