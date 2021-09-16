from ._package_manager import create_manager
from ...tools._common import cached_property


class PackageManager:
    def __init__(self, package_name) -> None:
        self.package_name = package_name

    @cached_property
    def _manager(self):
        return create_manager(self.package_name)

    def update_files(self) -> None:
        """Download the latest update files and the latest init file if none has been downloaded yet."""
        self._manager.update_files()

    def reset_files(self) -> None:
        """Cleans up files and force the download of the latest init update files and all subsequent update files.
        Note: A call to reset_files() is equivalent to a call to cleanup_files() followed by update_files()."""
        self._manager.reset_files()

    def cleanup_files(self) -> None:
        """Remove all previously downloaded files."""
        self._manager.cleanup_files()

    def cleanup_db(self) -> None:
        """Clean up the db accordingly to config file."""
        self._manager.cleanup_db()

    def update_db(self) -> None:
        """Update database
        Note: call cleanup_db() beforehand if there is a new init file."""
        self._manager.update_db()
