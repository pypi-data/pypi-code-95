from swimlane_platform.lib.args_config_questions import Configuration
from typing import Dict, List
from os import path
from swimlane_platform.lib import BaseWithLog, names, database_encryption_key_question, \
    mongo_admin_password_question, mongo_sw_password_question
from swimlane_platform.lib.env_manager import read_dict, write_dict
from swimlane_platform.lib.db_configuration import DbConfiguration
from swimlane_platform.lib.debug_decorators import info_function_start_finish, verbose_function_start_finish


class SetupSwimlaneEnvironment(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> SetupSwimlaneEnvironment
        super(SetupSwimlaneEnvironment, self).__init__(config)
        self.secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)
        self.db_configuration = DbConfiguration(self.config)

    @info_function_start_finish('Setup Swimlane environment.')
    def run(self):
        # type: () -> None
        """
        Main sequence of events.
        """
        self.setup_db_encryption_key()
        self.setup_passwords_in_env_file()

    @verbose_function_start_finish('Save db encryption key.')
    def setup_db_encryption_key(self):
        # type: () -> None
        """
        Writes entered db encryption key to the file used in docker-compose
        """
        with open(path.join(self.secrets_dir, names.DB_ENCRYPTION_KEY), 'w') as fs:
            fs.write(self.config.args.db_encryption_key)

    @verbose_function_start_finish('Configure env files.')
    def setup_passwords_in_env_file(self):
        # type: () -> None
        """
        Configure .env files
        """
        assert self.config.args.mongo_sw_password
        assert self.config.args.mongo_admin_password
        # Modify swimlane url in env file
        for env_file in [names.API_ENV_FILE, names.TASKS_ENV_FILE]:
            filename = path.join(self.secrets_dir, env_file)
            env_dict = read_dict(filename)
            for key in [names.DOT_NET_SWIMLANE_CONN_KEY, names.DOT_NET_HISTORY_CONN_KEY]:
                db_url = env_dict[key]
                mongo_settings = self.db_configuration.parse_mongo_uri(db_url)
                mongo_settings['password'] = self.config.args.mongo_sw_password
                env_dict[key] = self.db_configuration.get_mongo_uri(mongo_settings)
            write_dict(filename, env_dict)
            self.logger.verbose('{name} file was saved with new passwords.'.format(name=env_file))
        # Modify passwords in mongodb env
        mongo_env_filename = path.join(self.secrets_dir, names.MONGO_ENV_FILE)
        mongo_env_dict = read_dict(mongo_env_filename)
        mongo_env_dict[names.MONGO_ENV_ADMIN_PASSWORD] = self.config.args.mongo_admin_password
        mongo_env_dict[names.MONGO_ENV_SW_PASSWORD] = self.config.args.mongo_sw_password
        write_dict(mongo_env_filename, mongo_env_dict)
        self.logger.verbose('{name} file was saved with new passwords.'.format(name=names.MONGO_ENV_FILE))


def questions():
    # type: () -> List[Dict[str, str]]
    return [
        database_encryption_key_question,
        mongo_admin_password_question,
        mongo_sw_password_question
    ]


def run(config):
    # type: (Configuration) -> None
    """
    The script run method, that can be called by other script or from file run method.
    :param config: Configuration information collected by parent script.
    """
    config.collect(questions())
    SetupSwimlaneEnvironment(config).run()
