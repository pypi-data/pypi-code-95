from swimlane_platform.lib.mongo_manager import MongoManager
from swimlane_platform.lib.docker_compose_manager import DockerComposeManager
from swimlane_platform.lib import names, env_manager
from swimlane_platform.lib.docker_compose_file_manager import DockerComposeFileManager
from swimlane_platform.lib.debug_decorators import info_function_start_finish, debug_function_args
from swimlane_platform.shared_steps import enable_turbine
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
from os import path
import semver


class UpgradeFrom1022To1030(UpgradeStep):
    FROM = semver.parse_version_info('10.2.2')  # type: semver.VersionInfo
    TO = semver.parse_version_info('10.3.0')  # type: semver.VersionInfo

    @info_function_start_finish('Upgrade From 10.2.2 To 10.3.0')
    def process(self):
        # type: () -> None
        enable_turbine.run(self.config)        
        self.upgrade_image_versions(names.INSTALL_DIR, self.config.args.dev)
        self.add_report_service(names.INSTALL_DIR)
        self.upgrade_compatibility_mode()
        self.add_env_vars(names.INSTALL_DIR)

    @debug_function_args
    def upgrade_image_versions(self, install_dir, dev):
        # type: (str, bool) -> None
        """
        Changes mongo image version to 4.4.2
        :param dev: If the images will be pulled from development repository.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        docker_compose = self.upgrade_standard_images(self.config.args.dev, names.INSTALL_DIR)
        docker_compose.set('mongo:4.4.2', 'services', names.SW_MONGO, 'image')
        docker_compose.save()

    @debug_function_args
    def add_report_service(self, install_dir):
        # type: (str, bool) -> None
        """
        Adds report service to docker-compose file
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        docker_compose = DockerComposeFileManager(self.logger, path.join(install_dir, names.DOCKER_COMPOSE_FILE))
        docker_compose.set(False, 'volumes', 'reports', 'external')
        docker_compose.set(['ALL'], 'services', names.SW_REPORTS, 'cap_drop')
        docker_compose.set(['CHOWN', 'KILL'], 'services', names.SW_REPORTS, 'cap_add')
        docker_compose.set(names.SW_REPORTS, 'services', names.SW_REPORTS, 'container_name')
        docker_compose.set(['no-new-privileges'], 'services', names.SW_REPORTS, 'security_opt')
        docker_compose.set('unless-stopped', 'services', names.SW_REPORTS, 'restart')
        docker_compose.set(['reports:/app'], 'services', names.SW_REPORTS, 'volumes')
        docker_compose.set({"internal_network": {"aliases": ['sw-reports']}}, 'services', names.SW_REPORTS, 'networks')

        docker_compose.save()

    @debug_function_args
    def upgrade_compatibility_mode(self):
        # type: () -> None
        """
        Issues database compatibility command.
        """
        docker_compose_file = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
        docker_compose_manager = DockerComposeManager(self.logger, docker_compose_file)
        docker_compose_manager.docker_compose_up(names.SW_MONGO)
        MongoManager(self.config).set_database_compatibility('4.4')
        docker_compose_manager.docker_compose_down()


    @debug_function_args
    def add_env_vars(self, install_dir):
        # type: (str, bool) -> None
        """
        Adds the new env variables to the api and tasks env files
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        # Modify env files.
        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            new_env_file = dict((key, value) for key, value in env_file.items())            
            new_env_file['SWIMLANE_FeatureManagement__DynamicOrchestration'] = 'false'
            new_env_file['SWIMLANE_FeatureManagement__ContentExchange'] = 'false'
            new_env_file['SWIMLANE_OpenSSL__MinProtocol'] = 'TLSv1.2'
            new_env_file['SWIMLANE_OpenSSL__CipherString'] = 'DEFAULT@SECLEVEL=2'
            new_env_file['SWIMLANE_ReportsService__BaseUrl'] = 'http://sw-reports:4000/'
            env_manager.write_dict(file_path, new_env_file)