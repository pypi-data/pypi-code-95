from pymongo import MongoClient
from typing import Union, Dict
from swimlane_platform.lib.db_configuration import DbConfiguration
from swimlane_platform.lib.args_config_questions import Configuration
from swimlane_platform.lib import BaseWithLog
from swimlane_platform.lib.expected_exceptions import ExpectedException
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return


class MongoManager(BaseWithLog):

    def __init__(self, config, uri=None):
        # type: (Configuration, Union[str, None]) -> None
        super(MongoManager, self).__init__(config)
        self.db_configuration = DbConfiguration(self.config)
        uri = uri if uri else self.get_admin_connection_uri()
        self.client = MongoClient(host=uri)

    @debug_function_return
    @debug_function_args
    def db_exists(self, db_name):
        # type: (str) -> bool
        """
        Verifies if database already exists on the server
        :param db_name: Database name
        :return: True if database exists, false otherwise.
        """
        try:
            existing_database_names = self.client.list_database_names()
        except Exception:
            raise ExpectedException('Cannot connect to database {name}'.format(name=db_name))
        return db_name in existing_database_names

    @debug_function_args
    def create_user(self, db_name, user_name, user_password, create_database=False, role='dbOwner'):
        # type: (str, str, str, bool, str) -> None
        """
        Creates the user in the selected database. Creates database if it doesn't exists and so requested.
        :param db_name: Name of the database.
        :param user_name: New user name.
        :param user_password: New user password.
        :param create_database: Should you create new database if it doesn't exists.
        :param role: The role user should have in the database.
        """
        try:
            existing_database_names = self.client.list_database_names()
        except Exception:
            raise ExpectedException('Cannot connect to database {name}'.format(name=db_name))

        if db_name not in existing_database_names and not create_database:
            raise ExpectedException('Database does not exist.')

        try:
            db = self.client.get_database(db_name)
        except Exception:
            raise ExpectedException('Cannot create database {name}'.format(name=db_name))

        try:
            db.command('createUser', user_name, pwd=user_password, roles=[{'role': role, 'db': db_name}])
        except Exception as e:
            raise ExpectedException('Cannot create user {name}. {error}'.format(name=user_name, error=e))

    @debug_function_return
    @debug_function_args
    def get_admin_connection_uri(self, ssl_req=True):
        # type: (bool) -> str
        """
        Gets default admin database connection URI.
        :param ssl_req: Is ssl required.
        :return: URI connection string.
        """
        uri_dict = dict()
        uri_dict['nodelist'] = [('localhost', 27017)]
        uri_dict['database'] = 'admin'
        uri_dict['password'] = self.db_configuration.get_admin_password()
        uri_dict['username'] = self.db_configuration.get_admin_user_name()
        if ssl_req:
            uri_dict['options'] = {'ssl': 'true', 'ssl_cert_reqs': 'CERT_NONE'}
        return self.db_configuration.get_mongo_uri(uri_dict)

    @debug_function_return
    @debug_function_args
    def user_exists(self, db, user_name):
        # type: (str, str) -> bool
        """
        Checks if user is defined in admin database for specific databases.
        :param db: Database name.
        :param user_name: User name. i.e. Swimlane.
        :return: True if user is defined.
        """
        users = self.client.get_database(db).command('usersInfo').get('users')
        return user_name in [user.get('user') for user in users]

    @debug_function_return
    @debug_function_args
    def get_swimlane_settings(self):
        # type: () -> Dict[str, Union[str, Dict]]
        """
        Returns current settings from Swimlane database.
        """
        database = self.client.get_database('Swimlane')
        collection = database.get_collection('Settings')
        return collection.find_one()

    @debug_function_return
    @debug_function_args
    def set_swimlane_settings(self, settings):
        # type: (object) -> None
        """
        Returns current settings from Swimlane database.
        """
        database = self.client.get_database('Swimlane')
        collection = database.get_collection('Settings')
        collection.find_one_and_replace({}, settings)

    @debug_function_args
    def set_database_compatibility(self, version):
        # type: (str) -> None
        """
        Sets compatibility option.
        :param version: Compatibility version.
        """
        self.client.get_database('admin').command('setFeatureCompatibilityVersion', version)
