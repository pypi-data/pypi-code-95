from os import path
from typing import Union, List, Callable, Dict, Any, Tuple
from swimlane_platform.lib.args_config_questions import Configuration
from swimlane_platform.lib import mongo_admin_password_question, mongo_sw_password_question
from swimlane_platform.lib.expected_exceptions import ValidationException
from swimlane_platform.lib.names import names
from swimlane_platform.lib.env_manager import read_dict
from swimlane_platform.lib.base_with_log import BaseWithLog
from swimlane_platform.lib.debug_decorators import debug_function_return, debug_function_args
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import quote
from pymongo import uri_parser


class DbConfiguration(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> None
        super(DbConfiguration, self).__init__(config)
        self.secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)

    @debug_function_return
    @debug_function_args
    def get_mongo_uri(self, mongo_settings):
        # type: (Union[None,Dict[str, Any]]) -> str
        """
        Returns formatted MongoDb Uri.
        :param mongo_settings: MongoDb settings.
        :return: MongoDb uri string.
        """
        url = 'mongodb://'
        user_name = mongo_settings.get('username', '')
        password = quote(mongo_settings.get('password', ''))
        if user_name or password:
            url += '{user}:{password}@'.format(user=user_name, password=password)
        url += ','.join(['{host}:{port}'.format(host=node[0], port=node[1]) for node in mongo_settings['nodelist']])
        if mongo_settings.get('database'):
            url += '/{database}'.format(database=mongo_settings['database'])
        if mongo_settings.get('options'):
            url += '?'
            items = ['{key}={value}'.format(key=key, value=value) for key, value in mongo_settings['options'].items()]
            url += '&'.join(items)
        return url

    @debug_function_return
    @debug_function_args
    def parse_mongo_uri(self, uri):
        # type: (str) -> Dict[str, Union[str, List[Tuple[str, str]], Dict[str, str]]]
        return uri_parser.parse_uri(uri, validate=False)

    @debug_function_return
    def get_sw_user_name(self):
        # type: () -> str
        """
        Gets swimlane user name.
        :return: swimlane user name.
        :exception: ValidationException if cannot find user name.
        """
        return self._chain('Cannot find swimlane user name.',
                           lambda: self._inspect_mongo_env(names.MONGO_ENV_SW_NAME),
                           lambda: self._inspect_api_env_swimlane_connection('username')
                           )

    @debug_function_return
    def get_sw_password(self):
        # type: () -> str
        """
        Gets swimlane user password.
        :return: swimlane user password.
        :exception: ValidationException if cannot find password.
        """
        return self._chain('Cannot find swimlane user password.',
                           lambda: self._inspect_answered_questions(mongo_sw_password_question),
                           lambda: self._inspect_mongo_env(names.MONGO_ENV_SW_PASSWORD),
                           lambda: self._inspect_api_env_swimlane_connection('password')
                           )

    @debug_function_return
    def get_admin_user_name(self):
        # type: () -> str
        """
        Gets admin user name.
        :return: admin user name.
        :exception: ValidationException if cannot find user name.
        """
        return self._chain('Cannot find admin user name.',
                           lambda: self._inspect_mongo_env(names.MONGO_ENV_ADMIN_NAME))

    @debug_function_return
    def get_admin_password(self):
        # type: () -> str
        """
        Gets admin password.
        :return: admin password.
        :exception: ValidationException if cannot find password.
        """
        return self._chain('Cannot find admin user password.',
                           lambda: self._inspect_answered_questions(mongo_admin_password_question),
                           lambda: self._inspect_mongo_env(names.MONGO_ENV_ADMIN_PASSWORD)
                           )

    @debug_function_return
    @debug_function_args
    def _inspect_api_env_swimlane_connection(self, key):
        # type: (str) -> Union[str, None]
        """
        Returns value for the key in Swimlane connection string. Taken from .api-env
        :param key: Key in connection string. i.e. username, password, database etc
        :return: None if not present or the value found.
        """
        api_env = read_dict(path.join(self.secrets_dir, names.API_ENV_FILE))
        swimlane_connection = api_env.get(names.DOT_NET_SWIMLANE_CONN_KEY)
        if swimlane_connection:
            uri = self.parse_mongo_uri(swimlane_connection)
            return uri.get(key)
        return None

    @debug_function_return
    @debug_function_args
    def _inspect_mongo_env(self, key):
        # type: (str) -> Union[None, str]
        """
        Returns value found in .mongo-env for a key.
        :param key: Key, i.e swimlane user, admin password. Correct key names are in names
        :return: None if not found or value.
        """
        mongo_env = read_dict(path.join(self.secrets_dir, names.MONGO_ENV_FILE))
        return mongo_env.get(key)

    @debug_function_return
    @debug_function_args
    def _inspect_answered_questions(self, question):
        # type: (Dict[str, Any]) -> Union[None, str]
        """
        Returns value if the question has been answered.
        :param question: question to search for in answered args object.
        :return: None if not found or value.
        """
        question_name = question.get('name')
        return self.config.get(question_name) if question_name else None

    @debug_function_return
    @debug_function_args
    def _chain(self, error, *functions):
        # type: (str, List[Callable]) -> str
        """
        Evaluate and returns first value from submitted functions.
        :param error: Exception to throw if values are not found.
        :param functions: Lambda functions to evaluate to get value. Done for performance reasons.
        :return: value or raise specified error.
        """
        for f in functions:
            value = f()
            if value:
                return value
        raise ValidationException(error)
