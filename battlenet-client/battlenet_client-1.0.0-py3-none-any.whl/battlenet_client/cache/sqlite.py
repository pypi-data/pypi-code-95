from decouple import config
from datetime import datetime, timedelta
import sqlite3


class Cache:
    def __init__(self, host=None):
        if not host:
            host = config('CACHE_HOST', default=':memory:')

        self._db_client = sqlite3.connect(host)
        self._cursor = self._db_client.cursor()

    def check_cache(self, collection_name, category, category_id, locale):
        """
        checks on the cache for basic validity.

        Args:
            collection_name (str):  The name of the collection, usually a name similar to the API addon package ie "wow"
            category (str): the category, usually the category of item, ie 'achievements'
            category_id (str or int): the id to lookup, IE 'achievement id'
            locale (str): locale string

        Returns:
            result: single document that matches the criteria
            None: if there is no result
        """

        duration = self._db_client['cache']['expiry'].find_one({'category': category})
        result = self._db_client['cache'][collection_name].find_one({'category': category, 'category_id': category_id,
                                                                     'locale': locale})

        if result and (result['lastUpdated'] + timedelta(seconds=duration['duration']) > datetime.utcnow()):
            return result

        return None

    def insert_cache(self, collection_name, category, category_id, data, locale):
        """
        adds an item to the cache

        Args:
            collection_name (str): the name of the collection, ie the game abbreviation
            category (str): the category being queried, ie 'achievements'
            category_id (str or int): the ID within the category being searched
            locale (str): the locale to use for the query
            data (str): the JSON encoded data to be stored in the document

        Returns:
            bool: True on successful insert, otherwise False
        """

        insert = {
            'category': category,
            'category_id': category_id,
            'locale': locale,
            'lastUpdated': datetime.utcnow(),
            'data': data
        }

        return self._db_client['cache'][collection_name].insert_one(insert).inserted_id

    def delete_cache(self, collection_name, category, category_id, locale):
        """
        removes an item to the cache

        Args:
            collection_name (str): the name of the collection, ie the game abbreviation
            category (str): the category being queried, ie 'achievements'
            category_id (str or int): the ID within the category being searched
            locale (str): the locale to use for the query

        Returns:
            bool: True on successful delete, otherwise False
        """

        return self._db_client['cache'][collection_name].delete_one({'category': category, 'category_id': category_id,
                                                                     'locale': locale})

    def update_cache(self, collection_name, category, category_id, data, locale):
        """
        removes an item to the cache

        Args:
            collection_name (str): the name of the collection, ie the game abbreviation
            category (str): the category being queried, ie 'achievements'
            category_id (str or int): the ID within the category being searched
            locale (str): the locale to use for the query
            data (str): the JSON encoded data to update

        Returns:
            bool: True on successful delete, otherwise False
        """

        self._db_client['cache'][collection_name].update_one({'category': category, 'category_id': category_id,
                                                              'locale': locale},
                                                             {{'$set': {'data': data}},
                                                              {'$currentDate': {'lastUpdated': True}}},
                                                             upsert=True)
