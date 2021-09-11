from swimlane_platform.lib.names import names
from swimlane_platform.lib.debug_decorators import debug_function_args


class DockerImage:

    def __init__(self, repository=names.DEV_REPOSITORY, image_name=None, version=None, is_dev=False):
        # type: (str, str, str, bool) -> DockerImage
        """
        Constructor
        :param repository: Repository name.
        :param image_name: Image name.
        :param version: Version.
        :param is_dev: True if running in development environment.
        """
        self.repository = repository
        self.image_name = image_name
        self.version = version
        self.is_dev = is_dev

    @debug_function_args
    def _parse(self, tag):
        # type: (str) -> None
        """
        Parses full tag to object properties.
        :param tag: The full tag.
        """
        tag = tag.replace(self.repository, '')
        self.image_name, self.version = tag.rsplit(':', 1)

    @staticmethod
    def parse(tag, is_dev):
        # type: (str, bool) -> DockerImage
        """
        Parses swimlane image tag and returns DockerImage
        :param tag: The full image value from docker-compose
        :param is_dev: If image is pulled from development repository.
        :return: DockerImage
        """
        docker_image = DockerImage(is_dev=is_dev)
        docker_image._parse(tag)
        return docker_image

    @property
    def archive_name(self):
        # type: () -> str
        """
        Returns the archive image for docker image.
        :return: Archive image name.
        """
        return '{image}.tgz'.format(image=self.image_name.split('/')[-1])

    @property
    def full_name(self):
        # type: () -> str
        """
        Combines docker image tag parts together.
        :return: Full image tag.
        """
        return '{repository}{image}:{version}' \
            .format(repository=self.repository if self.is_dev else '', image=self.image_name, version=self.version)
