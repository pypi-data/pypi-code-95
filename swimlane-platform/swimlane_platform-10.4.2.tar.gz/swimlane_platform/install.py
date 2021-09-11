from os import path
import os
import pkg_resources
import swimlane_platform
from swimlane_platform.lib.functions import find_remote_sibling
from swimlane_platform.lib import ValidationException, \
    Configuration, \
    info_function_start_finish, \
    debug_function_args, \
    BaseWithLog, \
    names, \
    DockerComposeManager, \
    VersionValidator, \
    DockerManager, \
    DockerComposeFileManager, \
    web_ssl_questions, \
    ssl_questions
from swimlane_platform.shared_steps import enable_mongo_ssl
from swimlane_platform.lib.version_manager import pypi_version_to_semver
from swimlane_platform.lib.os_manager import OsManager
from swimlane_platform.lib.constants import SWIMLANE_UID_GID
from swimlane_platform.install_steps import enable_web_ssl
from swimlane_platform.add_file_encryption_key import run as run_add_file_encryption
from swimlane_platform.install_steps.setup_swimlane_environment import run as run_setup_environment
from swimlane_platform.install_steps.set_permissions import run as run_set_permissions
from swimlane_platform.shared_steps import enable_turbine
from swimlane_platform.install_steps.setup_dbs import run as run_setup_dbs
from swimlane_platform.lib.questions_groups import offline_questions
import shutil
import glob
from swimlane_platform.install_steps import PreFlightCheck
from builtins import str


class SwimlaneInstaller(BaseWithLog):

    def __init__(self, config):
        # type: (Configuration) -> None
        super(SwimlaneInstaller, self).__init__(config)
        script_path = path.dirname(path.realpath(__file__))
        self.template_dir = find_remote_sibling(script_path, names.TEMPLATE_DIR)
        self.docker_manager = DockerManager(self.logger)
        self.os_manager = OsManager(self.logger)

    @info_function_start_finish('Install Swimlane.')
    def run(self):
        # type: () -> None
        """
        Main Swimlane install method.
        """
        if not PreFlightCheck(self.config).run():
            return
        self.install_swimlane_files()
        self.get_swimlane_images()
        # order is important
        enable_web_ssl.run(self.config)
        enable_mongo_ssl.run(self.config)
        # ******************
        run_setup_environment(self.config)
        run_setup_dbs(self.config)
        run_set_permissions(self.config)
        run_add_file_encryption(self.config)
        enable_turbine.run(self.config)
        self.run_after_install()

    @info_function_start_finish('Installing Swimlane files.')
    def install_swimlane_files(self):
        """
        Make install directories and copy files there
        """
        self.create_if_does_not_exists(names.INSTALL_DIR)
        secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)
        self.create_if_does_not_exists(secrets_dir)
        db_init_dir = path.join(names.INSTALL_DIR, names.DB_INIT_SUB_FOLDER)
        self.create_if_does_not_exists(db_init_dir)
        self.copy_if_does_not_exists(self.template_dir, names.INSTALL_DIR, '*.yml')
        template_db_init = path.join(self.template_dir, names.DB_INIT_SUB_FOLDER)
        self.copy_if_does_not_exists(template_db_init, db_init_dir, '*.sh')
        self.copy_if_does_not_exists(path.join(self.template_dir, names.SECRETS_SUB_FOLDER), secrets_dir, '.*')
        # Explicit name due to security issues.
        self.os_manager.copy_with_permissions(path.join(template_db_init, 'init-mongodb-users.sh'),
                                              path.join(db_init_dir, 'init-mongodb-users.sh'), 0x655)

    @info_function_start_finish('Getting Swimlane docker images.')
    def get_swimlane_images(self):
        """Loads or pulls docker images required by Swimlane.
        In case of offline, analyses the images bundled, until build will know or care about repository
        re-tags nexus images. In case of online, analyses docker-compose file template and decides
        which version to pull.
        In both cases modifies docker-compose template to use correct images.
        """
        docker_compose_file = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
        docker_compose_file_manager = DockerComposeFileManager(self.logger, docker_compose_file)
        version = str(self.config.args.version) if self.config.args.version else self.latest_version()
        repository, version = self.docker_manager.extract_or_pull_images(docker_compose_file_manager.get_image_tags(),
                                                                         version,
                                                                         self.config.args.dev,
                                                                         self.config.args.installer_is_offline,
                                                                         self.config.args.extracted_files_folder)
        docker_compose_file_manager.replace_in_file_and_reload(names.TEMPLATE_REPOSITORY_TAG, repository)
        docker_compose_file_manager.replace_in_file_and_reload(names.TEMPLATE_VERSION_TAG, version)

    @staticmethod
    def latest_version():
        # type: () -> str
        """
        Returns the latest version of swimlane platform.
        :return: swimlane platform package version.
        """
        version_string = pkg_resources.get_distribution(swimlane_platform.__name__).version
        version = pypi_version_to_semver(version_string)
        if version:
            return str(version)
        else:
            raise ValidationException('Cannot parse package version {version} to Swimlane'.format(version=version))

    @info_function_start_finish('After installation.')
    def run_after_install(self):
        # type: () -> None
        """
        Prompts the user and starts or leaves containers as is.
        """
        START_COMMAND_MSG = 'cd /opt/swimlane and run "docker-compose up -d"'
        if not self.os_manager.swimlane_can_start():
            self.logger.warn('Swimlane is not currently able to start. Please change the UID and GID of the ' +
                             'current user to {uid_gid}, then {start_cmd} to start the Swimlane Services manually'
                             .format(uid_gid=SWIMLANE_UID_GID, start_cmd=START_COMMAND_MSG))
            return

        questions = [{
            'type': 'confirm',
            'name': 'start_swimlane',
            'message': 'Would you like to start the Swimlane services?'
        }]

        self.config.collect(questions)
        if self.config.args.start_swimlane:
            docker_compose_file = path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE)
            DockerComposeManager(self.logger, docker_compose_file).docker_compose_up()
        else:
            self.logger.info(
                'To start the Swimlane Services manually, {0}.'.format(START_COMMAND_MSG))

    @debug_function_args
    def create_if_does_not_exists(self, dir_path):
        """Creates directory first checking for it's existence."""
        if not path.exists(dir_path):
            os.mkdir(dir_path)
            self.logger.verbose("{source} directory created.".format(source=dir_path))

    @debug_function_args
    def copy_if_does_not_exists(self, source, target, mask):
        for filepath in glob.glob1(source, mask):
            if not path.exists(path.join(target, filepath)):
                source_file = path.join(source, filepath)
                shutil.copy2(source_file, target)
                self.logger.verbose("File {source} copied to {target}".format(source=source_file, target=target))


def run(config):
    # type: (Configuration) -> None
    # noinspection PyCompatibility
    questions = offline_questions
    questions.append({
        'type': 'input',
        'name': 'version',
        'message': 'For development installation which version do you want to use?',
        'default': SwimlaneInstaller.latest_version(),
        'validate': VersionValidator,
        'when': lambda a: a.get('dev') and not a.get('installer_is_offline')
    })
    questions.extend(web_ssl_questions)
    config.collect(questions)
    if config.args.web_ssl_self_signed:
        config.collect(ssl_questions)
    SwimlaneInstaller(config).run()
