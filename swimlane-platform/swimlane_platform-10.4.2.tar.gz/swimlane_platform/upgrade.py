#!/usr/bin/env python
from os import path
from semver import VersionInfo
from typing import List
from swimlane_platform.lib import Configuration, DockerComposeFileManager, DockerComposeManager, DockerManager, \
    names, debug_function_args, debug_function_return, info_function_start_finish, \
    ValidationException, BaseWithLog
from swimlane_platform.lib.args_config_questions import PathExistsValidator, VersionValidator
from swimlane_platform.lib.version_manager import semver_parse
from swimlane_platform.upgrade_steps import Upgrades
from swimlane_platform.lib.questions_groups import offline_questions
import semver


class SwimlaneUpgrader(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> None
        super(SwimlaneUpgrader, self).__init__(config)
        self.docker_manager = DockerManager(self.logger)

    @info_function_start_finish('Swimlane upgrade.')
    def run(self):
        # type: () -> None
        """
        Main method for upgrading Swimlane installation.
        """
        args = self.config.args
        current_version = self.get_service_version(names.SW_API)
        requested_version = semver.parse_version_info(args.version)
        if not self.need_upgrade(current_version, requested_version):
            self.logger.info('No upgrade applied, current version is bigger or equal to requested one.')
            return

        compose_file = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
        compose_file_override = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_OVERRIDE_FILE)
        old_images = DockerComposeFileManager(self.logger, compose_file).get_image_tags()
        self.stop_containers(compose_file, compose_file_override)
        self.run_incremental_upgrades(current_version, requested_version)
        new_images = DockerComposeFileManager(self.logger, compose_file).get_image_tags()
        self.docker_manager.extract_or_pull_images(new_images,
                                                   args.version,
                                                   args.dev,
                                                   args.installer_is_offline,
                                                   args.extracted_files_folder)
        self.clean_images(old_images, new_images)
        self.start_containers(compose_file, compose_file_override)

    @debug_function_return
    @debug_function_args
    def need_upgrade(self, current_version, upgrade_version):
        # type: (semver.VersionInfo, semver.VersionInfo) -> bool
        """
        Compares versions to determine if upgrade is needed.
        :param current_version: Current version of Swimlane.
        :param upgrade_version: New version of Swimlane.
        :return: True if upgrade needed.
        """
        return current_version < upgrade_version

    @debug_function_return
    @debug_function_args
    def get_service_version(self, service_name):
        # type: (str) -> semver.VersionInfo
        """
        Gets service image version.
        :return: image version
        """
        docker_compose = DockerComposeFileManager(self.logger, path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE))
        image_name = docker_compose.get('services', service_name, 'image')
        return self._get_version_from_image(image_name)

    @info_function_start_finish()
    @debug_function_args
    def clean_images(self, old_images, new_images):
        # type: (List[str],List[str]) -> None
        """
        Removes old images if they are replaced with newer ones.
        """
        images_to_remove = (image for image in old_images if image not in new_images)
        for old_image in images_to_remove:
            self.docker_manager.image_remove(old_image)
            self.logger.info('Removed {image} image.'.format(image=old_image))

    @info_function_start_finish('Running incremental upgrades.')
    @debug_function_args
    def run_incremental_upgrades(self, current_version, version):
        # type: (VersionInfo, VersionInfo) -> None
        """
        Runs all incremental upgrades up to a particular version.
        :param current_version: Current version.
        :param version: Target version.
        """
        if not self.need_upgrade(current_version, version):
            return
        upgrade = next((u for u in Upgrades if u.FROM == current_version), None)
        if upgrade:
            upgrade_step = upgrade(self.config)
            upgrade_step.process()
            self.run_incremental_upgrades(upgrade_step.TO, version)

    @debug_function_return
    @debug_function_args
    def _get_version_from_image(self, image_name):
        # type: (str) -> semver.VersionInfo
        """
        Returns the version part of an image.
        :param image_name:
        :return:
        """
        error = ValidationException('Cannot get current version. Cannot determine steps needed.')
        if not image_name:
            raise error
        split = image_name.split(':')
        if len(split) < 1:
            raise error
        tag = split[-1]
        version = semver_parse(tag)
        if not version:
            if tag == '4.0-7.0.0-beta':
                return VersionInfo(7, 0, 0)
            elif tag == '4.0-7.0.1-beta':
                return VersionInfo(7, 0, 1)
            raise error
        return version

    @info_function_start_finish()
    @debug_function_args
    def start_containers(self, *args):
        # type: (List[str]) -> None
        """
        Starts containers
        :param args: docker-compose files (full path).
        """
        DockerComposeManager(self.logger, *args).docker_compose_up()

    @info_function_start_finish()
    @debug_function_args
    def stop_containers(self, *args):
        # type: (List[str]) -> None
        """
        Starts containers
        :param args: docker-compose files (full path).
        """
        DockerComposeManager(self.logger, *args).docker_compose_down()


def run(config):
    # type: (Configuration) -> None
    """
    The script run method, that can be called by other script.
    :param config: Configuration information collected by parent script.
    """
    questions = offline_questions
    questions.append(
        {
            'type': 'input',
            'name': 'version',
            'message': 'What version do you want to upgrade to?',
            'validate': VersionValidator
        })
    config.collect(questions)
    SwimlaneUpgrader(config).run()
