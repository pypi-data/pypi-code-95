from swimlane_platform.lib.version_manager import semver_parse
from swimlane_platform.lib import BaseWithLog, \
    Configuration, \
    ValidationException, \
    names, \
    DockerManager, \
    AnswerRequiredValidator, \
    DockerComposeManager
from swimlane_platform.lib.constants import SWIMLANE_UID_GID
from swimlane_platform.lib.debug_decorators import debug_function_return, info_function_start_finish
from os import getuid, path, mkdir, rmdir
from json import load
from swimlane_platform.lib.os_manager import OsManager
from uuid import uuid1


class PreFlightCheck(BaseWithLog):
    """
    Class responsible for checking environment before attempting to install.
    """

    def __init__(self, config):
        # type: (Configuration) -> None
        super(PreFlightCheck, self).__init__(config)
        self.os_manager = OsManager(self.logger)

    @info_function_start_finish('Pre-flight checks.')
    def run(self):
        # type: () -> bool
        verification_result = True
        try:
            verification_result &= self.check_os()
            verification_result &= self.check_current_user()
            verification_result &= self.check_docker_version()
            verification_result &= self.check_docker_compose_version()
            verification_result &= self.check_docker_repository_access()
            verification_result &= self.check_installation_dir_permissions()
        except ValidationException as e:
            self.logger.error('Critical validation failed and further checks will not continue: {error}'
                              .format(error=e))
            verification_result = False
        return verification_result

    @debug_function_return
    def check_os(self):
        # type: () -> bool
        """
        Validates if Swimlane is getting installed on supported os.
        """
        if not self.os_manager.is_linux():
            raise ValidationException('Operating system must be linux.')
        match_centos = self.os_manager.is_match_distribution_linux('centos', '7.5.1804')
        match_rhel = self.os_manager.is_match_distribution_linux('redhat', '7.6.0', True)
        if not (match_centos or match_rhel):
            _os = self.os_manager.get_platform()
            raise ValidationException('{os} is not on the list of supported distributions.'.format(os=_os))
        return True

    @debug_function_return
    def check_current_user(self):
        # type: () -> bool
        """
        Checks if user is not a service user, but sudo.
        """
        uid = getuid()
        if uid == 0:
            self.logger.warn('Installer is currently running as root (sudo). This is NOT RECOMMENDED!')
            questions = [{
                'type': 'confirm',
                'name': 'continue_if_user_is_root',
                'message': 'Do you still wish to continue with root user?'
            }]
            self.config.collect(questions)
            if not self.config.args.continue_if_user_is_root:
                raise ValidationException("User is root, installation aborted.")
        elif uid != SWIMLANE_UID_GID:
            self.logger.warn('Installer is currently running as a user with a UID of {uid}. '.format(uid=uid)
                            + 'It is recommended that you run Swimlane under a user with a UID of '
                            + '{uid_gid} and a GID of {uid_gid}, otherwise Swimlane might not start '.format(uid_gid=SWIMLANE_UID_GID)
                            + 'once installation is complete.')
            questions = [{
                'type': 'confirm',
                'name': 'continue_if_user_has_incorrect_uid_gid',
                'message': 'Do you still wish to continue the install as the current user?'
            }]
            self.config.collect(questions)
            if not self.config.args.continue_if_user_has_incorrect_uid_gid:
                raise ValidationException('User does not have correct UID or GID, aborting')
        return True

    # noinspection PyBroadException
    @debug_function_return
    def check_docker_version(self):
        # type: () -> bool
        """
        Verifies the installed docker meets requirements.
        """
        # skip verification on RedHat - it uses it's own docker.
        if self.os_manager.get_distribution_linux() == 'rhel':
            return True

        version = '18.6.0'
        try:
            docker_manager = DockerManager(self.logger)
        except Exception:
            self.logger.error('Docker not found. '
                              'Please install Docker version ${version} or greater.'.format(version=version))
            return False
        if docker_manager.docker_version() < semver_parse(version):
            self.logger.error('Unsupported version of Docker detected. '
                              'Please install Docker version ${version} or greater.'.format(version=version))
            return False
        try:
            _ = docker_manager.images
        except Exception:
            self.logger.error('Installer cannot run Docker commands. '
                              'Please ensure that docker is running and a user is in the docker group.')
            return False
        return True

    # noinspection PyBroadException
    @debug_function_return
    def check_docker_compose_version(self):
        # type: () -> bool
        """
        Verifies the installed docker-compose meets requirements.
        """
        version = '1.22.0'
        try:
            docker_compose_version = DockerComposeManager(self.logger, '').docker_compose_version()
            if docker_compose_version < semver_parse(version):
                self.logger.error('docker-compose version is unsupported. '
                                  'Please install docker-compose version ${version} or greater.'
                                  .format(version=version))
                return False
            return True
        except Exception:
            self.logger.error('docker-compose not found. '
                              'Please install docker-compose version ${version} or greater.'
                              .format(version=version))
            return False

    @debug_function_return
    def check_docker_repository_access(self):
        # type: () -> bool
        """
        Checks if docker can login to nexus or PyPi.
        :return: True if passes
        """
        if self.config.args.installer_is_offline:
            return True
        repo_name = names.DEV_REPOSITORY.rstrip('/') if self.config.args.dev else 'https://index.docker.io/v1/'
        config_json = path.expanduser('~/.docker/config.json')
        if not path.exists(config_json):
            self.logger.debug("{name} is not found so no docker information.".format(name=config_json))
            no_login = True
        else:
            with open(path.expanduser(config_json)) as fs:
                docker_config = load(fs)
            registered_repositories = [str(key) for key, value in docker_config['auths'].items()]
            no_login = not [1 for repository in registered_repositories if repo_name in repository]
        if no_login:
            questions = [
                {
                    'type': 'confirm',
                    'name': 'collect_docker_login',
                    'message': 'You are not logged in to {name}, log in now?'.format(name=repo_name)
                },
                {
                    'type': 'input',
                    'name': 'docker_repo_user',
                    'message': '{name} user name?'.format(name=repo_name),
                    'when': lambda a: 'collect_docker_login' in a and a['collect_docker_login'],
                    'validate': AnswerRequiredValidator
                },
                {
                    'type': 'password',
                    'name': 'docker_repo_password',
                    'message': '{name} password?'.format(name=repo_name),
                    'when': lambda a: 'collect_docker_login' in a and a['collect_docker_login'],
                    'validate': AnswerRequiredValidator
                }]
            self.config.collect(questions)
            if not self.config.args.docker_repo_user or not self.config.args.docker_repo_password:
                self.logger.error("Cannot proceed without login to {name}.".format(name=repo_name))
                return False
            DockerManager(self.logger).login(repo_name, self.config.args.docker_repo_user,
                                             self.config.args.docker_repo_password)
        return True

    # noinspection PyBroadException
    @debug_function_return
    def check_installation_dir_permissions(self):
        # type: () -> bool
        """
        Checks if user can write to /opt
        :return: True if can.
        """
        dir_id = 'f' + str(uuid1()).replace('-', '_')
        new_dir = path.join(names.INSTALL_DIR, dir_id)
        try:
            mkdir(new_dir)
            rmdir(new_dir)
        except Exception:
            self.logger.error('Cannot install to {name}. Ensure current user has write permissions.'
                              .format(name=names.INSTALL_DIR))
            return False
        return True
