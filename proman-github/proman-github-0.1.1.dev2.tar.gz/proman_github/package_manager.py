"""Provide package manager capabilities using GitHub."""
import os
import platform
import shutil
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from urllib.request import Request, urlopen

import magic
from github import Github
from proman_common.packaging_bases import PackageManagerBase
from proman_common.filepaths import GlobalDirs

# from proman_github import config
# from proman_github import filesystem
from proman_github.archive import Archive
from proman_github.dependency import Dependency

if TYPE_CHECKING:
    from github.GithubReleaseAsset import GithubReleaseAsset
    from github.GitRelease import GitRelease
    from github.PaginatedList import PaginatedList
    from proman_github.manifest import Manifest


class PackageManager(PackageManagerBase):
    """Proide package manager for GitHub releases."""

    def __init__(
        self,
        manifest: Optional['Manifest'] = None,
        force: bool = False,
        update: bool = False,
        **options: Any,
    ) -> None:
        """Initialize GitHub package manager."""
        self.__manifest = manifest
        self.__arch: str = options.get('arch', platform.machine().lower())
        self.__platform: str = (
            options.get('platorm', platform.system().lower())
        )
        self.__dirs = options.get('dirs', GlobalDirs())
        self.__github = options.get('github', Github())
        self.__archive = options.get('archive', Archive())

    def __get_release(
        self,
        name: str,
        version: str = 'latest',
    ) -> Optional['GitRelease']:
        """Get project releases."""
        release = None
        repo = self.__github.get_repo(name)
        if repo:
            if version == 'latest':
                release = repo.get_latest_release()
            else:
                for x in repo.get_releases():
                    if x.tag_name == version:
                        release = x
                if release:
                    release = self.__github\
                        .get_repo(name)\
                        .get_release(id=release.id)
        return release

    def __get_asset(
        self,
        assets: 'PaginatedList',
        archive: Optional[str] = None,
        arch: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> Optional['GithubReleaseAsset']:
        """Get archive for platform or architecture."""
        match = None
        weight = 0
        asset_names = [x.name for x in assets]
        for asset in assets:
            asset_weight = 0
            if archive and archive in asset_names:
                return asset
            elif (
                asset.content_type == 'application/octet-stream'
                or asset.content_type == 'application/gzip'
                or asset.content_type == 'application/zip'
            ):
                if self.__platform != '' and self.__platform in asset.name:
                    asset_weight += 2
                if self.__arch and self.__arch in asset.name:
                    asset_weight += 1
                if suffix and asset.name.endswith(suffix):
                    asset_weight += 1
                if asset_weight > weight:
                    match = asset
                    weight = asset_weight
        return match

    def _get_dependency(
        self, package: str, version: str = 'latest', dev: bool = False
    ) -> Optional[Dependency]:
        """Lookup dependency."""
        release = self.__get_release(package, version=version)
        if release:
            asset = self.__get_asset(release.get_assets())
            if asset:
                dependency = Dependency(
                    asset,
                    version=release.tag_name,
                    dev=dev
                )
                return dependency
        return None

    def _unpack_archive(self, path: str, dest: str) -> List[str]:
        """Unpack tarball."""
        os.makedirs(dest)
        self.__archive.unpack(path, dest)
        return os.listdir(dest)

    def __install_executable(self, executable: str, source_path: str) -> None:
        """Install executable."""
        executable_path = os.path.join(self.__dirs.executable_dir, executable)
        if not os.path.exists(executable_path):
            os.makedirs(self.__dirs.executable_dir, exist_ok=True)
            shutil.move(source_path, executable_path)
            if os.name == 'posix':
                st = os.stat(executable_path)
                os.chmod(executable_path, st.st_mode | 0o111)
        else:
            print('already installed:', executable)

    def _install_asset(self, source_path: str, filename: str) -> None:
        """Install package."""
        # handle download
        mimetype = magic.from_file(source_path, mime=True)
        if mimetype == 'application/x-executable':
            self.__install_executable(filename, source_path)
        else:
            contents_dir = os.path.join(
                os.path.dirname(source_path), 'contents'
            )
            contents = self._unpack_archive(source_path, contents_dir)
            for path in contents:
                contents_file = os.path.join(contents_dir, path)
                if os.path.isfile(contents_file):
                    mimetype = magic.from_file(contents_file, mime=True)
                    if mimetype == 'application/x-executable':
                        self.__install_executable(filename, contents_file)

    def install(self, *packages: Any, **options: Any) -> None:
        """Install GitHub release."""
        version = options.get('version', 'latest')
        dev = options.get('dev', False)
        # force = options.get('force', False)

        for package in list(packages):
            if '/' in package:
                filename = package.split('/')[1]
            else:
                raise Exception('package requires both group and project')

            dependency = self._get_dependency(
                package=package, version=version, dev=dev
            )
            if dependency:
                with TemporaryDirectory() as temp_dir:
                    filepath = os.path.join(temp_dir, dependency.name)
                    self.__download(dependency, filepath)
                    self._install_asset(
                        source_path=filepath, filename=filename
                    )
                if self.__manifest:
                    self.__manifest.add_dependency(dependency)

    def __remove_path(self, path: str) -> None:
        """Remove package directory from path."""
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
        except OSError as err:
            print(f"unable to delete direcotry path due to: {err}")

    def __uninstall_executable(self, executable: str) -> None:
        """Uninstall executable."""
        executable_path = os.path.join(self.__dirs.executable_dir, executable)
        if os.path.exists(executable_path):
            self.__remove_path(executable_path)
        else:
            print('already uninstalled:', executable)

    def uninstall(self, *packages: Any, **options: Any) -> None:
        """Perform package uninstall."""
        dev = options.get('dev', False)
        # force = options.get('force', False)

        # TODO: janky stop-gap
        for package in packages:
            if self.__manifest:
                self.__manifest.remove_dependency(package, dev)
            executable = package.split('/')[1] if '/' in package else package
            self.__uninstall_executable(executable=executable)

    def update(self, *packages: Any, **options: Any) -> None:
        """Update the package."""
        dev = options.get('dev', False)
        force = options.get('force', False)

        # TODO: janky stop-gap
        if self.__manifest:
            for package in packages:
                self.uninstall(package, dev, force)
                self.install(package, dev, version='latest')
            else:
                dependencies = self.__manifest.lockfile.get_locks()
                print(dependencies)

    def search(self, query: str, **options: Any) -> 'PaginatedList':
        """Perform package search."""
        sort = options.pop('sort', None) or 'stars'
        order = options.pop('order', None) or 'desc'
        result = self.__github.search_repositories(
            query=query, sort=sort, order=order, **options
        )
        return result

    def info(self, name: str, output: str) -> Dict[str, Any]:
        """Retrieve package information."""
        return {}

    def __download(
        self, dependency: Dependency, dest: str, **options: Any
    ) -> None:
        request = Request(
            dependency.url,
            headers={'Accept': 'application/octet-stream'},
        )
        with urlopen(request) as response:
            data = response.read()
            with open(dest, 'wb') as f:
                f.write(data)

    def download(self, package: str, dest: str, **options: Any) -> None:
        """Download package."""
        try:
            version = options.get('version', 'latest')
            dependency = self._get_dependency(package=package, version=version)
            if dependency:
                dest_path = os.path.join(dest, dependency.name)
                self.__download(dependency, dest_path, **options)
            else:
                raise Exception('could not locate download')
        except OSError as err:
            print(f"unable to download github release due to: {err}")
