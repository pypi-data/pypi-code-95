from swimlane_platform.lib.mongo_manager import MongoManager
from swimlane_platform.lib.names import names
from swimlane_platform.lib.debug_decorators import info_function_start_finish, debug_function_args
from swimlane_platform.lib.docker_compose_manager import DockerComposeManager
from swimlane_platform.shared_steps import enable_turbine, set_mongo_tls_flags
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
import semver
from os import path


class UpgradeFrom912To1000(UpgradeStep):
    FROM = semver.parse_version_info('9.1.2')  # type: semver.VersionInfo
    TO = semver.parse_version_info('10.0.0')  # type: semver.VersionInfo

    @debug_function_args
    def upgrade_image_versions(self, install_dir, dev):
        # type: (str, bool) -> None
        """
        Changes image versions to the new ones
        :param dev: If the images will be pulled from development repository.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        docker_compose = self.upgrade_standard_images(dev, install_dir)
        docker_compose.set('mongo:4.2.1', 'services', names.SW_MONGO, 'image')
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
        MongoManager(self.config).set_database_compatibility('4.2')
        docker_compose_manager.docker_compose_down()

    @info_function_start_finish('Upgrade From 9.1.2 To 10.0.0.')
    def process(self):
        # type: () -> None
        enable_turbine.run(self.config)
        self.upgrade_image_versions(names.INSTALL_DIR, self.config.args.dev)
        set_mongo_tls_flags.run(self.config)
        self.upgrade_compatibility_mode()
