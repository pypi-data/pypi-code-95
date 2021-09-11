from os import path

from swimlane_platform.lib import BaseWithLog, DockerComposeFileManager, names, DockerImage
from abc import abstractproperty, ABCMeta, abstractmethod
import semver
from future.utils import with_metaclass


class UpgradeStep(with_metaclass(ABCMeta, BaseWithLog)):

    @abstractproperty
    def FROM(self):
        # type: () -> semver.VersionInfo
        pass

    @abstractproperty
    def TO(self):
        # type: () -> semver.VersionInfo
        pass

    @abstractmethod
    def process(self):
        # type: () -> None
        pass

    def upgrade_standard_images(self, dev, install_dir):
        # type: (bool, str) -> DockerComposeFileManager
        """

        :param dev: True if run in development environment.
        :param install_dir: Installation directory where docker-compose file is.
        :return: DockerComposeFileManager to add additional upgrades.
        """
        docker_compose = DockerComposeFileManager(self.logger, path.join(install_dir, names.DOCKER_COMPOSE_FILE))
        api_image = DockerImage(image_name='swimlane/swimlane-api', version=str(self.TO), is_dev=dev).full_name
        docker_compose.set(api_image, 'services', names.SW_API, 'image')
        tasks_image = DockerImage(image_name='swimlane/swimlane-tasks', version=str(self.TO), is_dev=dev).full_name
        docker_compose.set(tasks_image, 'services', names.SW_TASKS, 'image')
        web_image = DockerImage(image_name='swimlane/swimlane-web', version=str(self.TO), is_dev=dev).full_name
        docker_compose.set(web_image, 'services', names.SW_WEB, 'image')
        reports_image = DockerImage(image_name='swimlane/swimlane-reports', version=str(self.TO), is_dev=dev).full_name
        docker_compose.set(reports_image, 'services', names.SW_REPORTS, 'image')
        return docker_compose
