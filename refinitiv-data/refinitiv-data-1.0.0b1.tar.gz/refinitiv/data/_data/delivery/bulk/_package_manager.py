from ._actions import Actions
from ._db_manager import DBManager, create_db_manager_by_package_name
from ._file_manager import FileManager
from ... import configure
from .cfs._tools import (
    path_join,
    create_dirs_if_no_exists,
)
from ...log import root_logger
from ...tools._common import cached_property, make_counter


def get_console_logger(id_):
    return root_logger.getChild(f"{id_}.console")


def create_logpath(package_name):
    package_config = configure.get(f"bulk.{package_name}.package")
    path = package_config.get("download.path")
    create_dirs_if_no_exists(path)
    return path_join(path, "log.txt")


class _PackageManager:
    __inst_count = make_counter()

    def __init__(self, name):
        self._id = f"bulk.package_manager.{_PackageManager.__inst_count()}"
        self.name = name

    @cached_property
    def actions(self) -> Actions:
        return Actions(self._id, self.logpath)

    @cached_property
    def file_manager(self) -> FileManager:
        package_config = configure.get(f"bulk.{self.name}.package")
        package_name = package_config.get("name")
        if self.name.startswith("esg."):
            bucket = package_config.get("bucket", "ESG")
        else:
            bucket = package_config.get("bucket")
        download_path = package_config.get("download.path")
        auto_extract = package_config.get("download.auto-extract")

        if package_config.get("download.auto-retry.enabled"):
            auto_retry_count = package_config.get("download.auto-retry.count")
        else:
            auto_retry_count = 0

        file_manager = FileManager(
            actions=self.actions,
            logger=self.logger,
            package_name=package_name,
            bucket=bucket,
            path=download_path,
            auto_extract=auto_extract,
            auto_retry=auto_retry_count,
        )
        return file_manager

    @cached_property
    def db_manager(self) -> DBManager:
        return create_db_manager_by_package_name(
            self.name,
            self.actions,
            self.logger,
        )

    @cached_property
    def logpath(self):
        return create_logpath(self.name)

    @cached_property
    def logger(self):
        return get_console_logger(self._id)

    def update_files(self):
        self.file_manager.update_files()

    def reset_files(self):
        self.cleanup_files()
        self.update_files()

    def cleanup_files(self):
        self.file_manager.cleanup_files()

    def update_db(self):
        filesdata_for_update = self.file_manager.read_files_for_update()
        self.db_manager.update_db(filesdata_for_update)

    def cleanup_db(self):
        self.db_manager.cleanup_db()


def create_manager(package_name):
    return _PackageManager(package_name)
