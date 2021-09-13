from decouple import config
from datetime import datetime, timedelta
import mariadb


class Cache:
    def __init__(self, host=None, port=None, user=None, passwd=None, db_name=None):
        if not host:
            host = config('CACHE_HOST', default='127.0.0.1')

        if not port:
            port = config('CACHE_PORT', default=5432)

        if not user:
            user = config('CACHE_USER', default=None)

        if not passwd:
            passwd = config('CACHE_PASS', default=None)

        if not db_name:
            db_name = config('CACHE_DB', default=None)

        self._db_client = mariadb.connect(host=host, port=port, user=user, password=passwd, database=db_name)
        self._cursor = self._db_client.cursor()

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

        expiry_query = '''SELECT expiry.duration AS duration FROM expiry, categories, api_groups, games 
            WHERE games.abbrev=%s AND games.release=%s AND api_groups.game = games.id AND api_groups.api_name = %s AND
            categories.name = %s AND  categories.api_name_id = api_groups.id AND expiry.category = categories.id'''

        result_query = '''SELECT cache.data FROM cache, categories, api_groups, games
            WHERE games.abbrev=%s AND games.release=%s and api_groups.game = games.id AND api_groups.api_name = %s AND
            categories.name = %s AND categories.api_name_id = api_groups.id AND cache.category = categories.id AND 
            cache.api_id = %s AND cache.locale = %s'''

        self._cursor.excute(expiry_query, (game, release, api_name, category))
        if not self._db_client.rowcount():
            return None
        duration = self._cursor.fetchone()

        self._cursor.excute(result_query, (game, release, api_name, category, api_id, locale))
        result = self._cursor.fetchone()

        if duration and result and (result['lastUpdated'] + timedelta(seconds=duration['duration']
                                                                      ) > datetime.utcnow()):
            return result

        return None

    def insert_cache(self, game, release, api_name, category, api_id, data, locale):
        """
        adds an item to the cache

        Args:
            game (str):  The name of the collection, usually a name similar to the API addon package ie "wow"
            release (str): the release of the game, defaults to empty string for the retail version
            api_name (str): the api_name, usually the api_name of item, ie 'achievements'
            category (str): the category within the API grouping
            api_id (str or int): the id to lookup, IE 'achievement id'
            data (str): the JSON encoded data to be stored in the document
            locale (str): locale string

        Returns:
            bool: True on successful insert, otherwise False
        """

        insert_query = '''INSERT INTO cache (category, locale, cache, api_id, last_updated)
            SELECT (categories.id, %s, %s, %s, NOW()) FROM
            categories, api_groups, games WHERE games.abbrev=%s AND games.release=%s and api_groups.game = games.id AND
            api_groups.api_name = %s AND categories.name = %s AND categories.api_name_id = api_groups.id AND
            data.category = categories.id AND data.api_id = %s AND data.locale = %s'''

        self._cursor.excute(insert_query, (locale, data, api_id, game, release, api_name, category, api_id, locale))
        row_count = self._db_client.rowcount

        self._db_client.commit()

        if row_count:
            return True

        return False

    def delete_cache(self, game, release, api_name, category, api_id, locale):
        """
        removes an item to the cache

        Args:
            game (str):  The name of the collection, usually a name similar to the API addon package ie "wow"
            release (str): the release of the game, defaults to empty string for the retail version
            api_name (str): the api_name, usually the api_name of item, ie 'achievements'
            category (str): the category within the API grouping
            api_id (str or int): the id to lookup, IE 'achievement id'
            locale (str): locale string


        Returns:
            bool: True on successful delete, otherwise False
        """

        delete_query = '''DELETE FROM cache WHERE EXISTS (SELECT cache.* FROM cache, categories, api_groups, games
            WHERE games.abbrev=%s AND games.release=%s and api_groups.game = games.id AND api_groups.api_name = %s AND
            categories.name = %s AND categories.api_name_id = api_groups.id AND cache.category = categories.id AND 
            cache.api_id = %s AND cache.locale = %s)'''

        self._cursor.excute(delete_query, (game, release, api_name, category, api_id, locale))
        if self._db_client.rowcount:
            return False

        return True

    def update_cache(self, game, release, api_name, category, api_id, data, locale):
        """
        updates the cache via an update/insert method
        Args:
            game (str):  The name of the collection, usually a name similar to the API addon package ie "wow"
            release (str): the release of the game, defaults to empty string for the retail version
            api_name (str): the api_name, usually the api_name of item, ie 'achievements'
            category (str): the category within the API grouping
            api_id (str or int): the id to lookup, IE 'achievement id'
            data (str): the JSON encoded data to be stored in the document
            locale (str): locale string

        Returns:
            bool: True on successful delete, otherwise False
        """

        update_query = '''UPDATE cache, catgories, api_names, games SET data.data = %s, data.last_update = NOW()
        WHERE games.abbrev=%s AND games.release=%s and api_names.game = games.id AND api_names.api_name = %s AND
            categories.name = %s AND categories.api_name_id = api_names.id AND data.category = categories.id AND 
            data.api_id = %s AND data.locale = %s'''

        self._cursor.excute(update_query, (data, game, release, api_name, category, api_id, locale))

        if self._db_client.rowcount:
            return True

        return False
