from swimlane_platform.lib import names
from swimlane_platform.lib.base_with_log import BaseWithLog
from os import path
from swimlane_platform.lib.args_config_questions import Configuration
from stat import *
from swimlane_platform.lib.os_manager import OsManager
from swimlane_platform.lib.constants import SWIMLANE_UID_GID
from swimlane_platform.lib.debug_decorators import info_function_start_finish

class SetupPermissions(BaseWithLog):

    SECRETS_DIR_PERMS = S_IRWXU
    SECRETS_FILE_PERMS = S_IREAD | S_IWRITE
    SSL_WEB_CERTIFICATE_PERMS = S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH | S_IWOTH
    API_TASKS_UID_GID = SWIMLANE_UID_GID
    WEB_UID_GID = SWIMLANE_UID_GID

    def __init__(self, config):
        # type: (Configuration) -> SetupPermissions
        super(SetupPermissions, self).__init__(config)
        self.os_manager = OsManager(self.logger)
        self.secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)

    @info_function_start_finish('Setup Permissions.')
    def run(self):
        # type: () -> None
        """
        Main sequence of events.
        """
        self.check_and_set_perms(self.secrets_dir, self.SECRETS_DIR_PERMS)
        self.check_and_set_perms(path.join(self.secrets_dir, names.SSL_WEB_CERTIFICATE), self.SSL_WEB_CERTIFICATE_PERMS)
        self.check_and_set_perms(path.join(self.secrets_dir, names.TASKS_ENV_FILE), self.SECRETS_FILE_PERMS)
        self.check_and_set_perms(path.join(self.secrets_dir, names.MONGO_ENV_FILE), self.SECRETS_FILE_PERMS)
        self.check_and_set_perms(path.join(self.secrets_dir, names.API_ENV_FILE), self.SECRETS_FILE_PERMS)
        self.check_and_set_owner(path.join(self.secrets_dir, names.SSL_WEB_KEY), self.WEB_UID_GID, self.WEB_UID_GID)
        self.check_and_set_perms(path.join(self.secrets_dir, names.SSL_WEB_KEY), self.SECRETS_FILE_PERMS)
        self.check_and_set_owner(path.join(self.secrets_dir, names.DB_ENCRYPTION_KEY), self.API_TASKS_UID_GID,
                                 self.API_TASKS_UID_GID)
        self.check_and_set_perms(path.join(self.secrets_dir, names.DB_ENCRYPTION_KEY), self.SECRETS_FILE_PERMS)

    # noinspection PyBroadException
    def check_and_set_perms(self, file_system_path, permission):
        # type: (str, int) -> None
        """
        Verifies permission and sets it if it's different.
        :param file_system_path: File or folder path.
        :param permission: Octal number for permission.
        """
        if self.os_manager.get_permissions_linux(file_system_path) != permission:
            try:
                self.os_manager.set_permissions_linux(file_system_path, permission)
                self.logger.verbose('Changed permission on {name} to {perms}'
                                    .format(name=file_system_path, perms=permission))
            except Exception:
                self.logger.warn('Could not change permissions on {file}.'.format(file=file_system_path))
                self.logger.warn('You should do it manually "chmod {file} {perms}"'
                                 .format(file=file_system_path, perms=permission))

    # noinspection PyBroadException
    def check_and_set_owner(self, file_system_path, uid, gid):
        # type: (str, int, int) -> None
        """
        Verifies owner on file system object and sets it to correct one if wrong
        :param file_system_path: File or folder path.
        :param uid: User id.
        :param gid: Group id.
        """
        _uid, _gid = self.os_manager.get_owner_linux(file_system_path)
        if uid != _uid or gid != _gid:
            try:
                self.os_manager.set_owner_linux(file_system_path, uid, gid)
                self.logger.verbose('Changed owner on {name} to {uid}:{gid}'
                                    .format(name=file_system_path, uid=uid, gid=gid))
            except Exception:
                self.logger.warn('Could not change owner on {file}.'.format(file=file_system_path))
                self.logger.warn('You should do it manually "sudo chown {uid}:{gid} {file}"'
                                 .format(file=file_system_path, uid=uid, gid=gid))


def run(config):
    # type: (Configuration) -> None
    """
    The script run method, that can be called by other script or from file run method.
    :param config: Configuration information collected by parent script.
    """
    SetupPermissions(config).run()
