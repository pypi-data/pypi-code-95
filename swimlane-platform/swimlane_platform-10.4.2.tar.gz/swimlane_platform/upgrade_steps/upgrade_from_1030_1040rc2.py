from swimlane_platform.lib import names, env_manager
from swimlane_platform.lib.debug_decorators import info_function_start_finish, debug_function_args
from swimlane_platform.shared_steps import enable_turbine
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
from os import path
import semver


class UpgradeFrom1030To1040rc2(UpgradeStep):
    FROM = semver.parse_version_info('10.3.0')  # type: semver.VersionInfo
    TO = semver.parse_version_info('10.4.0-rc2')  # type: semver.VersionInfo

    @info_function_start_finish('Upgrade From 10.3.0 To 10.4.0-rc2')
    def process(self):
        # type: () -> None
        enable_turbine.run(self.config)
        self.upgrade_image_versions(names.INSTALL_DIR, self.config.args.dev)
        self.update_env_vars(names.INSTALL_DIR)

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
    def update_env_vars(self, install_dir):
        # type: (str, bool) -> None
        """
        Updates environment variables in .env files
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        # Modify env files.
        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            new_env_file = dict((key, value) for key, value in env_file.items())
            new_env_file.pop('SWIMLANE_FeatureManagement__ContentExchange', None)
            env_manager.write_dict(file_path, new_env_file)