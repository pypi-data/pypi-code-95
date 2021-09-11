from typing import Union
from os import path
from json import load
from swimlane_platform.lib.mongo_manager import MongoManager
from swimlane_platform.lib.functions import find_remote_sibling, copy_if_not_exist
from swimlane_platform.lib import names, DockerImage, DockerComposeManager, turbine_enable_questions
from swimlane_platform.lib.env_manager import read_dict, write_dict
from swimlane_platform.lib.args_config_questions import Configuration
from swimlane_platform.lib.base_with_log import BaseWithLog
from swimlane_platform.lib.docker_compose_file_manager import DockerComposeFileManager
from swimlane_platform.lib.debug_decorators import info_function_start_finish, debug_function_return
from swimlane_platform.lib.db_configuration import DbConfiguration


class EnableTurbine(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> None
        super(EnableTurbine, self).__init__(config)
        self.secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)
        self.template_dir = find_remote_sibling(path.dirname(path.realpath(__file__)), names.TEMPLATE_DIR)
        self.mongo_manager = MongoManager(self.config)
        self.db_configuration = DbConfiguration(self.config)

    @info_function_start_finish('Enabling Turbine.')
    def run(self):
        # type: () -> None
        """
        Main method for enabling turbine engine.
        """
        self.copy_files()
        self.modify_env_file()
        self.modify_compose_file()
        self.initialize_turbine_database()

    @info_function_start_finish('Adding turbine compose file to main docker-compose.')
    def modify_compose_file(self, main=None, turbine=None):
        # type: (Union[None, str], Union[None, str]) -> None
        """
        Overrides (in a docker-compose sense) main docker-compose file with Turbine.
        :param main: Main docker-compose file path (for testing)
        :param turbine: Turbine docker-compose file path (for testing)
        """
        main = main if main else path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
        turbine = turbine if turbine else path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_TURBINE_FILE)
        docker_compose_main = DockerComposeFileManager(self.logger, main)
        docker_compose_turbine = DockerComposeFileManager(self.logger, turbine)
        version = self.config.args.turbine_image_version if self.config.args.dev \
            else self.get_turbine_version_from_json()
        for name, service in docker_compose_turbine.get('services').items():
            if 'image' in service and 'swimlane' in service['image']:
                docker_image = DockerImage.parse(service['image'], self.config.args.dev)
                docker_image.version = version
                docker_compose_turbine.set(docker_image.full_name, 'services', name, 'image')
        docker_compose_main.override(docker_compose_turbine)
        docker_compose_main.save()

    @info_function_start_finish('Initializing Turbine database.')
    def initialize_turbine_database(self):
        # start Mongo
        main_docker_compose = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
        docker_compose_manager = DockerComposeManager(self.logger, main_docker_compose)
        docker_compose_manager.docker_compose_up(names.SW_MONGO)
        # access Mongo and make changes
        mongo_manager = MongoManager(self.config)
        user_name = self.db_configuration.get_sw_user_name()
        if not mongo_manager.user_exists(names.TURBINE_DATABASE, user_name):
            mongo_manager.create_user(names.TURBINE_DATABASE,
                                      user_name,
                                      self.db_configuration.get_sw_password(),
                                      create_database=True)
        # shut down service
        docker_compose_manager.docker_compose_down()

    @info_function_start_finish('Modifying env file.')
    def modify_env_file(self):
        # type: () -> None
        """
        Set the correct connection string to Mongo
        """
        db_key = 'DB_URL'
        turbine_env_file = path.join(self.secrets_dir, names.TURBINE_ENV_FILE)
        turbine_env_dict = read_dict(turbine_env_file)
        mongo_uri_dict = self.db_configuration.parse_mongo_uri(turbine_env_dict[db_key])
        mongo_uri_dict['username'] = self.db_configuration.get_sw_user_name()
        mongo_uri_dict['password'] = self.db_configuration.get_sw_password()
        turbine_env_dict[db_key] = self.db_configuration.get_mongo_uri(mongo_uri_dict)
        write_dict(turbine_env_file, turbine_env_dict)

    @info_function_start_finish('Copying turbine related files.')
    def copy_files(self):
        # type: () -> None
        """
        Copy turbine related files. Important for upgrade mostly.
        Currently install copies files using wild cards.
        """
        copy_if_not_exist(path.join(self.template_dir, names.DOCKER_COMPOSE_TURBINE_FILE),
                          path.join(self.template_dir, names.DOCKER_COMPOSE_TURBINE_FILE))
        copy_if_not_exist(path.join(self.template_dir, names.SECRETS_SUB_FOLDER, names.TURBINE_ENV_FILE),
                          path.join(self.secrets_dir, names.TURBINE_ENV_FILE))

    @debug_function_return
    def get_turbine_version_from_json(self):
        # type: () -> str
        """
        Returns turbine version.
        :return: version.
        """
        fp = open(path.join(self.template_dir, 'setup.json'))
        setup_json = load(fp)
        return setup_json.get('turbine_version')


def run(config):
    # type: (Configuration) -> None
    config.collect(turbine_enable_questions)
    if config.args.turbine_enable:
        EnableTurbine(config).run()
