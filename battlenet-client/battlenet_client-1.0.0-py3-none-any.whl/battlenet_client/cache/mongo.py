from urllib.parse import quote_plus
from decouple import config
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import ExecutionTimeout, OperationFailure


class Cache:
    
    def __init__(self, host=None, port=None, user=None, passwd=None, db_name=None):

        if not host:
            host = config('CACHE_HOST', default='127.0.0.1')

        if not port:
            port = config('CACHE_PORT', default=27017)

        if not user:
            user = quote_plus(config('CACHE_USER'))

        if not passwd:
            passwd = quote_plus(config('CACHE_PASS'))

        if not db_name:
            db_name = quote_plus(config('CACHE_DB'))

        dsn = f'mongodb://{user}:{passwd}@{host}:{port}/{db_name}'
        try:
            self._db_client = MongoClient(dsn)
        except OperationFailure as error:
            print(error)

    def check_cache(self, game, release, api_name, category, api_id, locale):
        """
        checks on the cache for basic validity.

        Args:
            game (str):  The name of the collection, usually a name similar to the API addon package ie "wow"
            release (str): the release of the game, defaults to empty string for the retail version
            api_name (str): the api_name, usually the api_name of item, ie 'achievements'
            category (str): the category within the API grouping or empty
            api_id (str or int): the id to lookup, IE 'achievement id'
            locale (str): locale string

        Returns:
            result: single document that matches the criteria
            None: if there is no result
        """

        if not game:
            return None

        try:
            duration = self._db_client['cache']['expiry'].find_one({"game": game, "release": release,
                                                                    "api_name": api_name})
        except ExecutionTimeout:
            return None
        else:
            result = self._db_client['cache']['data'].find_one({"game": game, "release": release, "api_name": api_name,
                                                                "category": category, "api_id": str(api_id),
                                                                "locale": locale})

        if duration and result and (result['last_updated'] + timedelta(seconds=duration['duration']) >
                                    datetime.utcnow()):
            return result['data']

        return None

    def insert_cache(self, game, release, api_name, category, api_id, data, locale):
        """
        adds an item to the cache

        Args:
            game (str): the name of the collection, ie the game abbreviation
            release (str): the release of the data request
            api_name (str): the api_name being queried, ie 'achievements'
            category (str): the category within the API grouping
            api_id (str or int): the ID within the api_name being searched
            locale (str): the locale to use for the query
            data (str or bytes): the JSON encoded data to be stored in the document

        Returns:
            bool: True on successful insert, otherwise False
        """

        insert = {
            'game': game,
            'release': release,
            'api_name': api_name,
            'category': category,
            'api_id': api_id,
            'locale': locale,
            'last_updated': datetime.utcnow(),
            'data': data
        }

        return self._db_client['cache']['data'].insert_one(insert)

    def delete_cache(self, game, release, api_name, category, api_id, locale):
        """
        removes an item to the cache

        Args:
            game (str): the name of the collection, ie the game abbreviation
            release (str): release other than retail
            api_name (str): the api_name being queried, ie 'achievements'
            category (str): the category within the API grouping
            api_id (str or int): the ID within the api_name being searched
            locale (str): the locale to use for the query

        Returns:
            bool: True on successful delete, otherwise False
        """

        return self._db_client['cache']['data'].delete_one({"game": game, "release": release, "api_name": api_name,
                                                            "category": category, "api_id": api_id,
                                                            "locale": locale})

    def update_cache(self, game, release, api_name, category, api_id, data, locale):
        """
        removes an item to the cache

        Args:
            game (str): the name of the collection, ie the game abbreviation
            release (str): release data other than retail
            api_name (str): the api_name being queried, ie 'achievements'
            category (str): the category within the API grouping
            api_id (str or int): the ID within the api_name being searched
            locale (str): the locale to use for the query
            data (str or bytes): the JSON encoded data to update

        Returns:
            bool: True on successful delete, otherwise False
        """

        self._db_client['cache']['data'].update_one({"game": game, "release": release, "api_name": api_name,
                                                     "category": category, "api_id": api_id, "locale": locale},
                                                    {'$set': {'data': data}, '$currentDate': {'last_updated': True}},
                                                    upsert=True)
