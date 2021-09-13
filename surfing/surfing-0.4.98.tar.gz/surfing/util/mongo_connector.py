
from surfing.util.singleton import Singleton
from surfing.util.config import SurfingConfigurator

import pandas as pd
import pymongo


class MongoConnector(metaclass=Singleton):

    def __init__(self, config_path=None) -> None:
        if config_path:
            self._settings = SurfingConfigurator(config_path).get_mongo_settings()
        else:
            self._settings = SurfingConfigurator().get_mongo_settings()
        self._client = None
        self._db_client = None

    def get_client(self):
        if self._db_client:
            return self._db_client
        conn_str = f'mongodb://{self._settings.username}:{self._settings.password}@{self._settings.host}/'
        self._client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
        self._db_client = self._client[self._settings.db]
        try:
            print(self._client.server_info(), self._settings.db)
        except Exception:
            print("Unable to connect to the server.")
        return self._db_client

    def put(self, collection, key, obj):
        data = {'_id': key, '_content': obj}
        self.get_client()[collection].replace_one({"_id": key}, data, True)

    def get(self, collection, key):
        _data = self.get_client()[collection].find_one({"_id": key})
        if isinstance(_data, dict):
            return _data['_content']
        return None

    def get_collections(self):
        # get collection list
        return self.get_client().list_collection_names()

    def get_items(self, collection):
        # get all items from collection
        cursor = self.get_client()[collection].find({})
        return {item['_id']: item['_content'] for item in cursor}

'''
    def append_one(self, db, collection, key, obj):
        data = {'_id': key}
        data.update(obj)
        return self._client[db][collection].insert_one(data)

    def get2(self, db, collection, key):
        return self._client[db][collection].find_one({"_id": key})

    def insert(self, db, collection, key, obj, upsert=True):
        self._client[db][collection].replace_one({"_id": key}, obj, upsert)

    # def _append_list(self, dbName, collectionName, d):
    #     db = self.dbClient[dbName]
    #     collection = db[collectionName]
    #     ids = collection.insert_many(d)
    #     return ids

    def query(self, db, collectionName, flt=None, since=None, limit=None, sort_key=None):
        collection = self._client[db][collectionName]
        if flt is None:
            if since is not None:
                flt = {'dbTime': {'$gte': since}}
            else:
                flt = {}
        else:
            if since is not None and 'dbTime' not in flt:
                flt['dbTime'] = {'$gte': since}
        if limit is not None:
            if sort_key is None:
                cursor = list(collection.find(flt).limit(limit))
            else:
                cursor = list(collection.find(flt).limit(limit).sort(sort_key, pymongo.DESCENDING))
        else:
            if sort_key is None:
                cursor = list(collection.find(flt))
        if len(cursor) > 0:
            return pd.DataFrame(cursor).drop('_id', axis=1).sort_index()
'''

if __name__ == '__main__':
    print(SurfingConfigurator().get_mongo_settings())
    connector = MongoConnector()
    connector.put('test', 'IF', {'contract': 'IF2209', 'lol': 'IF'})
    connector.put('test', 'IF2', {'1': 'IF2209', 'lol': 'IF'})
    a = connector.get('test', 'IF')
    print(a)
    print(connector.get('test', None))
    print(connector.get_items('test'))
    print(connector.get_collections())
