import re
from os import path
import docker
from docker import DockerClient
from docker.errors import NotFound
from docker.models.containers import Container
from docker.models.images import Image
from typing import List, Union, Dict, Iterable, Callable, Generator
from swimlane_platform.lib.names import names
from swimlane_platform.lib.docker_image import DockerImage
from swimlane_platform.lib.version_manager import semver_parse
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return
from swimlane_platform.lib.expected_exceptions import ValidationException
from swimlane_platform.lib.logger import SplitStreamLogger
import subprocess
from semver import VersionInfo


class DockerManager:
    client = None  # type: DockerClient

    def __init__(self, logger):
        # type: (SplitStreamLogger) -> DockerManager
        self.client = docker.from_env()
        self.logger = logger

    @debug_function_args
    def logs_by_line(self, container_name):
        # type: (str) -> Generator[str]
        """
        Blocking log reader. Line by line.
        :param container_name: Container name.
        """
        return self.client.containers.get(container_name).logs(stream=True, stdout=True, stderr=True)

    @debug_function_args
    def image_run_command(self, image_name, command, name, env=None, volumes=None, network=None):
        # type: (str, Union[str, List[str]], str, Union[List[str], Dict[str, str]], Dict[str, object], str) -> Iterable
        """
        Docker run command with stderr and stream set to true by default. And forced parameters.
        :param image_name: Image name
        :param command: Command
        :param name: Container name. Needed for later removing.
        :param env: Environmental variables.
        :param volumes: Volumes.
        :param network: Network name.
        :return: Logs.
        """
        return self.client.containers.run(image_name,
                                          command=command,
                                          name=name,
                                          stderr=True,
                                          stream=True,
                                          environment=env,
                                          volumes=volumes,
                                          network=network)

    @debug_function_args
    def image_pull(self, image_name):
        # type: (str) -> Image
        """
        Pulls image from repository.
        :param image_name: Repository+Image Tag
        :return Image pulled.
        """
        return self.client.images.pull(image_name)

    @debug_function_args
    def image_load(self, image_file_name):
        # type: (str) -> List[Image]
        """
        Loads images from local file.
        :param image_file_name: Compressed image file (from save)
        :return List of images loaded.
        """
        with open(image_file_name, 'rb') as bs:
            return self.client.images.load(bs)

    @debug_function_args
    def image_re_tag(self, old_tag, new_tag):
        # type: (str, str) -> None
        """
        Creates new tag.
        :param new_tag: New name+tag
        :param old_tag: Old name+tag
        """
        subprocess.check_output(['docker', 'tag', old_tag, new_tag])

    @debug_function_args
    def container_remove(self, name):
        # type: (str) -> None
        """
        Removes used container.
        :param name: Name of a container.
        """
        try:
            container = self.client.containers.get(name)
            container.remove(force=True)
        except NotFound:
            pass

    @debug_function_args
    def container_stop(self, container):
        # type: (Container) -> None
        """
        Stops container if it is running.
        :param container: The container.
        """
        if container.status == 'running':
            container.stop()

    @debug_function_args
    def container_start(self, container):
        # type: (Container) -> None
        """
        Starts container if it was stopped.
        :param container: The container.
        """
        if container.status != 'running':
            container.start()

    @debug_function_return
    @debug_function_args
    def container_get_network_name(self, container_name):
        # type: (str) -> str
        """
        Gets the name of the network specified container connected to.
        :param container_name: container name.
        :return: network name.
        """
        container = self.container_get(container_name)
        return container.attrs["HostConfig"]["NetworkMode"] if container else None

    @debug_function_return
    @debug_function_args
    def container_get_dotnet_env(self, container_name):
        # type: (str) -> List[str]
        """
        Gets the environment variables related to dotnet in the specified container.
        :param container_name: container name.
        :return: List of environment variables key=value.
        """
        container = self.container_get(container_name)
        if not container:
            return []
        return [env for env in (container.attrs["Config"]["Env"]) if re.search("__.+(?==)", env)]

    @debug_function_return
    @debug_function_args
    def container_check_volume_mapped(self, container, folder_path):
        # type: (Container, str) -> bool
        """
        Checks if pre-requisite volume is attached.
        :param container: Docker container.
        :param folder_path: path the volume is mapped to.
        """
        mounts = container.attrs['Mounts']
        mount = [mount for mount in mounts if mount['Destination'] == folder_path]
        return bool(mount)

    @debug_function_args
    def containers_run(self, func, *names):
        # type: (Callable, str) -> None
        """Runs specified function on the specified containers.
        :param func: Function to run.
        :param names: arg list of container names (could be partials)
        """
        for container in self.containers_get(*names):
            func(container)

    @debug_function_return
    @debug_function_args
    def containers_get(self, *names):
        # type: (str) -> List[Container]
        """
        Returns containers (running and stopped) by name.
        :param names: Names of containers.
        :return: Containers.
        """
        containers = self.client.containers.list(all=True)
        return [container for name in names for container in containers if str(container.name).find(name) != -1]

    @debug_function_return
    @debug_function_args
    def container_get(self, name):
        # type: (str) -> Union[Container, None]
        """
        Returns container (running and stopped) by name.
        :param name: Name of container.
        :return: Container.
        """
        try:
            return self.client.containers.get(name)
        except NotFound:
            return None

    @debug_function_args
    def containers_exists_validate(self, *names):
        # type: (str) -> None
        """
        Throws validation exceptions if one of the names is not found.
        :param names: Names of the containers.
        """
        result = self.containers_get(*names)
        if len(result) != len(names):
            found = [container.name for container in result]
            not_found = ','.join([name for name in names if name not in found])
            raise ValidationException("Container(s) {name} not found.".format(name=not_found))

    @debug_function_return
    @debug_function_args
    def containers_get_state(self, *names):
        # type: (str) -> Dict[str, str]
        """
        Returns dictionary of container names and their statuses.
        :param names: Container names.
        :return: Container statuses.
        """
        return dict(((container.name, container.status) for container in self.containers_get(*names)))

    @debug_function_return
    @debug_function_args
    def container_restore_state(self, states):
        # type: (Dict[str, str]) -> None
        """
        Starts containers that were running and stops the ones that weren't
        :param states: Container statuses.
        """
        if not states:
            return
        running = 'running'
        containers = self.containers_get(*states.keys())
        for container in containers:
            existing = container.status
            pre_existing = states[container.name]
            if pre_existing != running and existing == running:
                self.container_stop(container)
            elif pre_existing == running and existing != running:
                self.container_start(container)

    @property
    def images(self):
        # type: () -> List[Image]
        """
        All available images on the host.
        :return: List of images (info)
        """
        return self.client.images.list(all=True)

    @debug_function_return
    def images_get_tags(self):
        # type: () -> List[str]
        """
        Get all available images tags.
        :return: List of tag names.
        """
        return [image.tags[0] for image in self.images if image.tags]

    @debug_function_return
    def images_get_tags(self):
        # type: () -> List[str]
        """
        Get all available images tags.
        :return: List of tag names.
        """
        return [image.tags[0] for image in self.images if image.tags]

    @debug_function_args
    def image_remove(self, image_name):
        # type: (str) -> None
        try:
            self.client.images.remove(image_name)
        except NotFound:
            pass

    @debug_function_args
    def volume_remove(self, volume_name):
        # type: (str) -> None
        """
        Removes volume (running and stopped) by name.
        :param volume_name: The name of the volume.
        """
        try:
            volume = self.client.volumes.get(volume_name)
            volume.remove()
        except NotFound:
            pass

    @debug_function_args
    def login(self, registry, user, password, persist=True):
        # type: (str, str, str, bool) -> None
        """Creates login to registry under specified user.
        :param persist: If it should be written to config.json
        :param registry: The registry to login to.
        :param user: User name.
        :param password: Registry password.
        """
        self.client.login(registry=registry, username=user, password=password)
        if persist:
            subprocess.check_output(['docker', 'login', '-u', user, '-p', password, registry])

    @debug_function_return
    def docker_version(self):
        # type: () -> VersionInfo
        """
        Returns the installed docker version info.
        :return: semver VersionInfo for docker
        """
        docker_version = str(self.client.version()["Version"])
        version = semver_parse(docker_version)
        if version:
            return version
        # Docker version is not semver compatible
        no_leading_zeroes = re.sub(r'\b0+(\d+\.)', r'\1', docker_version)
        return semver_parse(no_leading_zeroes)

    def logs(self, container_name):
        # type: (str) -> str
        """
        Returns all logs from container.
        :param container_name:
        """
        return str(self.client.containers.get(container_name).logs())

    @debug_function_return
    @debug_function_args
    def extract_or_pull_images(self, image_tags, version, is_dev, installer_is_offline, extracted_files_folder):
        # type: (List[str], str, bool, bool, str) -> (str, str)
        """
        Method that either pulls required docker images or extracts them from archive if offline.
        :param image_tags: Images required.
        :param version: Version of image to populate if docker-compose file is a template.
        :param is_dev: Specifies if the environment is dev, required to pull from nexus or rename to production, if
         offline and production.
        :param installer_is_offline: Specifies if installer runs offline.
        :param extracted_files_folder: Where offline files are located.
        :return:
        """
        repository = names.DEV_REPOSITORY if is_dev else ''
        if installer_is_offline:
            images_file = path.join(extracted_files_folder, names.DOCKER_IMAGE_ARCHIVE_NAME)
            images = self.image_load(images_file)
            if not is_dev:
                for tag in (str(image.tags[0]) for image in images):
                    if tag.startswith(names.DEV_REPOSITORY):
                        new_tag = tag.replace(names.DEV_REPOSITORY, repository)
                        self.image_re_tag(tag, new_tag)
                        version = new_tag.split(':')[-1]
            for tag in (str(image.tags[0]) for image in images):
                self.logger.verbose("{image} loaded from archive.".format(image=tag))
        else:
            for image_tag in image_tags:
                image = image_tag.replace(names.TEMPLATE_REPOSITORY_TAG, repository)\
                    .replace(names.TEMPLATE_VERSION_TAG, version)
                self.image_pull(image)
                self.logger.verbose("{image} docker image pulled.".format(image=image))
        return repository, version

    def extract_or_pull_image(self, docker_image,  is_dev, installer_is_offline, extracted_files_folder):
        # type: (DockerImage, bool, bool, str) -> (str, str)
        """
        Pulls or extracts offline image based on naming convention.
        :param docker_image: Docker image type.
        :param is_dev: True if runs on development environment.
        :param installer_is_offline: True if offline.
        :param extracted_files_folder: Location of archive files.
        :return:
        """
        repository = names.DEV_REPOSITORY if is_dev else ''
        version = docker_image.version
        if installer_is_offline:
            image_tag = path.join(extracted_files_folder, docker_image.archive_name)
            image = self.image_load(image_tag)
            if not is_dev:
                tag = str(image[0].tags[0])
                if tag.startswith(names.DEV_REPOSITORY):
                    new_tag = tag.replace(names.DEV_REPOSITORY, repository)
                    self.image_re_tag(tag, new_tag)
                    version = new_tag.split(':')[-1]
                self.logger.verbose("{image} loaded from archive.".format(image=tag))
        else:
            self.image_pull(docker_image.full_name)
            self.logger.verbose("{image} docker image pulled.".format(image=docker_image.full_name))
        return repository, version
