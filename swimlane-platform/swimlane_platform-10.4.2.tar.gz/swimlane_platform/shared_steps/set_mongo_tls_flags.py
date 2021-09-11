from __future__ import print_function
from swimlane_platform.lib import Configuration, names, DockerComposeFileManager, BaseWithLog, \
    info_function_start_finish
from os import path


class SetMongoTlsFlags(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> SetMongoTlsFlags
        super(SetMongoTlsFlags, self).__init__(config)
        self.install_dir = names.INSTALL_DIR

    @info_function_start_finish('Set MongoDB TLS Flags')
    def run(self):
        # type: () -> None
        """
        Sets TLS flags in MongoDB start command.
        """
        docker_compose = DockerComposeFileManager(self.logger, path.join(self.install_dir, 'docker-compose.yml'))
        command = '--tlsMode requireTLS --tlsCertificateKeyFile /run/secrets/mongodb.pem'
        docker_compose.set(command, 'services', names.SW_MONGO, 'command')
        docker_compose.save()


def run(config):
    # type: (Configuration) -> None
    """
    The script run method, that can be called by other script or from file run method.
    :param config: Configuration information collected by parent script.
    """
    SetMongoTlsFlags(config).run()
