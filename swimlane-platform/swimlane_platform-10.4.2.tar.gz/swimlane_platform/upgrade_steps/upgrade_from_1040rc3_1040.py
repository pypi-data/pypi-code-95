from swimlane_platform.lib import names
from swimlane_platform.lib.debug_decorators import info_function_start_finish, debug_function_args
from swimlane_platform.lib.docker_manager import DockerManager
from swimlane_platform.shared_steps import enable_turbine
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
import semver


class UpgradeFrom1040rc3To1040(UpgradeStep):
    FROM = semver.parse_version_info('10.4.0-rc3')  # type: semver.VersionInfo
    TO = semver.parse_version_info('10.4.0')  # type: semver.VersionInfo

    @info_function_start_finish('Upgrade From 10.4.0-rc3 To 10.4.0')
    def process(self):
        # type: () -> None
        enable_turbine.run(self.config)
        self.upgrade_image_versions(names.INSTALL_DIR, self.config.args.dev)
        self.remove_reports_volume()

    @debug_function_args
    def upgrade_image_versions(self, install_dir, dev):
        # type: (str, bool) -> None
        """
        Updates image versions
        :param dev: If the images will be pulled from development repository.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        docker_compose = self.upgrade_standard_images(self.config.args.dev, names.INSTALL_DIR)
        docker_compose.save()


    @debug_function_args
    def remove_reports_volume(self):
        # type: (str, bool) -> None
        """
        Removes the reports volume so it can be rebuilt by the application
        """
        docker_manager = DockerManager(self.logger)
        docker_manager.volume_remove('swimlane_reports')
