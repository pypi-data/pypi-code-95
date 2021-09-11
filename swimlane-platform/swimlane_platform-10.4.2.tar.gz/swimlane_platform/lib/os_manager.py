import platform
import distro
from typing import Tuple
from swimlane_platform.lib import names
from swimlane_platform.lib.version_manager import semver_parse
from swimlane_platform.lib.logger import SplitStreamLogger
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return
from swimlane_platform.lib.constants import SWIMLANE_UID_GID
from os import stat, chmod, path, listdir
import os

try:
    # noinspection PyUnresolvedReferences
    from os import chown
except ImportError:
    pass


class OsManager:

    def __init__(self, logger):
        # type: (SplitStreamLogger) -> OsManager
        self.logger = logger

    @debug_function_return
    @debug_function_args
    def is_linux(self):
        # type: () -> bool
        """
        Verifies that os is linux
        :return: True if linux
        """
        return platform.system() == 'Linux'

    @debug_function_return
    @debug_function_args
    def is_match_distribution_linux(self, name, min_version, major_version_must_match=False):
        # type: (str, str, bool) -> bool
        """
        Verifies that os matches parameters send.
        :param name: Distribution name. i.e centos, rhel etc
        :param min_version: Minimum version of distribution
        :param major_version_must_match: Whether distro's major version must match that of min_version 
        :return: True if matches
        """
        linux_distribution = platform.linux_distribution(full_distribution_name=False)
        if not linux_distribution:
            self.logger.debug('Cannot obtain linux distribution info.')
            return False
        distribution_name, distribution_version, _ = linux_distribution
        if name != distribution_name:
            self.logger.debug('{value} does not match the name.'.format(value=distribution_name))
            return False
        version_info = semver_parse(distribution_version)
        if semver_parse(min_version) > version_info:
            self.logger.debug('{d_version}:{p_version} is lower than min version.'
                              .format(d_version=distribution_version, p_version=str(version_info)))
            return False
        if major_version_must_match and semver_parse(min_version).major != version_info.major:
            self.logger.debug('{d_version}:{p_version} has different major version than min version.'
                                .format(d_version=distribution_version, p_version=str(version_info)))
            return False
        return True

    @debug_function_return
    @debug_function_args
    def get_platform(self):
        # type: () -> str
        """
        Gets platform os long name. i.e. Linux-3.10.0-957.1.3.el7.x86_64-x86_64-with-centos-7.6.1810-Core
        :return: Long name
        """
        return platform.platform()

    @debug_function_return
    @debug_function_args
    def get_permissions_linux(self, file_system_path):
        # type: (str) -> int
        """
        Gets linux permissions of file system objects as oct str. i.e 660 etc
        :param file_system_path: File or folder path.
        :return Octal number for permission
        """
        return stat(file_system_path).st_mode & 0o777

    @debug_function_args
    def set_permissions_linux(self, file_system_path, permission):
        # type: (str, oct) -> None
        """
        Sets permissions on linux on file system objects.
        :param file_system_path: File or folder path.
        :param permission: Octal number for permission.
        """
        chmod(file_system_path, permission)

    @debug_function_return
    @debug_function_args
    def get_owner_linux(self, file_system_path):
        # type: (str) -> Tuple[int, int]
        """
        Gets linux owner information of file system objects as int. i.e (501, 500) etc
        :param file_system_path: File or folder path.
        :return Tuple with uid and gid respectively
        """
        stats = stat(file_system_path)
        return stats.st_uid, stats.st_gid

    @debug_function_args
    def set_owner_linux(self, file_system_path, uid, gid):
        # type: (str, int, int) -> None
        """
        Sets owner on linux on file system objects.
        :param file_system_path: File or folder path.
        :param uid: User id.
        :param gid: Group id.
        """
        chown(file_system_path, uid, gid)

    @debug_function_return
    def get_distribution_linux(self):
        # type: () -> str
        """
        Returns Linux distribution id. i.e centos, rhel etc
        :return: distribution id.
        """
        return distro.id()

    @debug_function_return
    def swimlane_can_start(self):
        """
        Checks whether or not Swimlane can start under the current user
        :return True if Swimlane can start under the current user, False otherwise
        """
        secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)
        files_to_check = {names.DB_ENCRYPTION_KEY, names.SSL_WEB_CERTIFICATE, names.SSL_WEB_KEY}
        for filename in filter(lambda f: f in files_to_check, listdir(secrets_dir)):
            stats = stat(path.join(secrets_dir, filename))
            if stats.st_uid != SWIMLANE_UID_GID:
                return False
        return True

    @debug_function_args
    def copy_with_permissions(self, file_origination, file_destination, permission, is_binary=False):
        """
        Copies content of the file to the file with different permissions.
        @param file_origination: Full path to original file.
        @param file_destination: Full path to destination file.
        @param permission: Permissions in numeric format.
        """
        # Getting content early, so you can overwrite itself.
        with open(file_origination, ('rb' if is_binary else 'r')) as file_out:
            content = file_out.read()

        umask = 0o777 ^ permission
        try:
            os.remove(file_destination)
        except OSError:
            pass

        # Open file descriptor
        umask_original = os.umask(umask)
        try:
            file_destination = os.open(file_destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, permission)
        finally:
            os.umask(umask_original)

        # Open file handle and write to file
        with os.fdopen(file_destination, ('wb' if is_binary else 'w')) as file_in:
            file_in.write(content)
