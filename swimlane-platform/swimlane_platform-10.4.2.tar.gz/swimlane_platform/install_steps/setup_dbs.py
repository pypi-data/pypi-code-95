from __future__ import print_function
from swimlane_platform.lib import names
from swimlane_platform.lib.base_with_log import BaseWithLog
from swimlane_platform.lib.docker_manager import DockerManager
from time import time
from swimlane_platform.lib.docker_compose_manager import DockerComposeManager
from swimlane_platform.lib.expected_exceptions import ExpectedException
from swimlane_platform.lib.args_config_questions import Configuration
from os import path
from swimlane_platform.lib.debug_decorators import info_function_start_finish, verbose_function_start_finish


class SetupDbs(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> SetupDbs
        super(SetupDbs, self).__init__(config)
        self.secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)
        self.docker_manager = DockerManager(self.logger)

    @info_function_start_finish('Setup Databases.')
    def run(self):
        # type: () -> None
        """
        Main sequence of events.
        """
        self.start_mongo_install_container()

    @verbose_function_start_finish('Start mongo installation container.')
    def start_mongo_install_container(self):
        # type: () -> None
        """
        Writes entered db encryption key to the file used in docker-compose
        """
        main_docker_compose = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
        install_docker_compose = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_INSTALL_FILE)
        docker_compose_manager = DockerComposeManager(self.logger, main_docker_compose, install_docker_compose)
        docker_compose_manager.docker_compose_run('--no-ansi', 'up', '-d', names.SW_MONGO)
        mongo_success_message = b"Successfully completed MongoDB initialization for Swimlane."
        error_message = b"ERROR: SWIMLANE INITIALIZATION ERROR OCCURRED"
        by_line = self.docker_manager.logs_by_line(names.SW_MONGO)
        try:
            start = time()
            for line in by_line:
                if mongo_success_message in line:
                    self.logger.info(str(mongo_success_message))
                    break
                if error_message in line:
                    raise ExpectedException('An error occurred initializing ${name}.'.format(name=names.SW_MONGO))
                if time() - start > 30:
                    raise ExpectedException('A timeout occurred initializing ${name}.'.format(name=names.SW_MONGO))
                else:
                    self.logger.debug(str(line))
        except ExpectedException:
            self.config.collect([{
                'type': 'confirm',
                'name': 'show_db_init_logs',
                'message': 'Error occurred, do you want to see the logs?'
            }])
            if self.config.args.show_db_init_logs:
                print(str(self.docker_manager.logs(names.SW_MONGO)))
            raise
        finally:
            by_line.close()
            docker_compose_manager.docker_compose_down()


def run(config):
    # type: (Configuration) -> None
    """
    The script run method, that can be called by other script or from file run method.
    :param config: Configuration information collected by parent script.
    """
    SetupDbs(config).run()
