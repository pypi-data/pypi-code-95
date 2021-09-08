"""API to download, uncompress and cache files such as binary models.

"""
__author__ = 'Paul Landes'

from typing import Union, Tuple, Dict, List
from dataclasses import dataclass, field
import logging
import re
from pathlib import Path
import urllib
from urllib.parse import ParseResult
import patoolib
from zensols.util import APIError, PackageResource
from zensols.persist import persisted
from zensols.config import Dictable
from zensols.install import Downloader

logger = logging.getLogger(__name__)


class InstallError(APIError):
    """Raised for issues while downloading or installing files."""


@dataclass
class Resource(Dictable):
    """A resource that is installed by downloading from the Internet and then
    optionally uncompressed.  Once the file is downloaded, it is only
    uncompressed if it is an archive file.  This is determined by the file
    extension.

    """
    _DICTABLE_ATTRIBUTES = 'remote_name is_compressed compressed_name'.split()
    _FILE_REGEX = re.compile(r'^(.+)\.(tar\.gz|tgz|tar\.bz2|' +
                             '|'.join(patoolib.ArchiveFormats) + ')$')
    _NO_FILE_REGEX = re.compile(r'^(?:.+/)?(.+?)\.(.+)?$')

    url: str = field()
    """The URL that locates the file to install."""

    name: str = field(default=None)
    """Used for local file naming."""

    clean_up: bool = field(default=True)
    """Whether or not to remove the downloaded compressed after finished."""

    def __post_init__(self):
        url: ParseResult = urllib.parse.urlparse(self.url)
        remote_path = Path(url.path)
        m = self._FILE_REGEX.match(remote_path.name)
        if m is None:
            m = self._NO_FILE_REGEX.match(remote_path.name)
            self._extension = None
            if m is None:
                self.remote_name = remote_path.name
            else:
                self.remote_name = m.group(1)
            if self.name is None:
                self.name = remote_path.name
        else:
            self.remote_name, self._extension = m.groups()
            if self.name is None:
                self.name = self.remote_name

    def uncompress(self, path: Path = None, out_dir: Path = None):
        """Uncompress the file.

        :param path: the file to uncompress

        :param out_dir: where the uncompressed files are extracted

        """
        if path is None:
            src = Path(self.compressed_name)
            out_dir = Path('.')
        else:
            src = path
            if out_dir is None:
                out_dir = path.parent
        dst_dir = out_dir / self.name
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'uncompressing {src} to {out_dir}')
        out_dir.mkdir(parents=True, exist_ok=True)
        patoolib.extract_archive(str(src), outdir=str(out_dir))
        if not dst_dir.is_dir():
            ext_dir = out_dir / self.remote_name
            if not ext_dir.is_dir():
                raise InstallError(f'Trying to create {dst_dir} but ' +
                                   f'missing extracted dir: {ext_dir}')
            if logger.isEnabledFor(logging.INFO):
                logger.info(f'renaming {ext_dir} to {dst_dir}')
            ext_dir.rename(dst_dir)
        if self.clean_up:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f'cleaning up downloaded file: {src}')
            src.unlink()

    @property
    def is_compressed(self) -> bool:
        """Whether or not the file is compressed.

        """
        return self._extension is not None

    @property
    def compressed_name(self) -> str:
        """The file name with the extension and used to uncompress.  If the resource
        isn't compressed, just the name is returned.

        """
        if self.is_compressed:
            name = f'{self.name}.{self._extension}'
        else:
            name = self.name
        return name


@dataclass
class Status(Dictable):
    """Tells of what was installed and how.

    """
    resource: Resource = field()
    """The resource that might have been installed."""

    downloaded_path: Path = field()
    """The path where :obj:`resource` was downloaded, or None if it wasn't
    downloaded.

    """

    target_path: Path = field()
    """Where the resource was installed and/or downloaded on the file system.

    """

    uncompressed: bool = field()
    """Whether or not the resource was uncompressed."""


@dataclass
class Installer(object):
    """Downloads files from the internet and optionally extracts them.

    :see: :class:`.Resource`

    """
    installs: Tuple[Resource] = field()
    """The list of resources to install."""

    package_resource: Union[str, PackageResource] = field(default=None)
    """Package resource (i.e. ``zensols.someappname``).  This field is converted to
    a package if given as a string during post initialization.  This is used to
    set :obj:`base_directory` using the package name from the home directory if
    given.  Otherwise, :obj:`base_directory` is used.  One must be set.

    """

    base_directory: Path = field(default=None)
    """The directory to base relative resource paths.

    :see: :obj:`package_resource`

    """

    downloader: Downloader = field(default_factory=Downloader)
    """Used to download the file from the Internet."""

    def __post_init__(self):
        if self.package_resource is None and self.base_directory is None:
            raise InstallError(
                'Either package_resource or base_directory must be set')
        if isinstance(self.package_resource, str):
            self.package_resource = PackageResource(self.package_resource)
        if self.base_directory is None:
            home = Path('~/').expanduser()
            parts = self.package_resource.name.split('.')
            parts[0] = '.' + parts[0]
            self.base_directory = home / Path(*parts)

    def get_path(self, inst: Resource, compressed: bool = False) -> Path:
        fname = inst.compressed_name if compressed else inst.name
        if fname is None:
            fname = inst.remote_name
        return self.base_directory / fname

    def _install(self, inst: Resource, dst_path: Path) -> Status:
        uncompressed: bool = False
        downloaded_path: Path = False
        target_path: Path = None
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'installing {inst.name} to {dst_path}')
        if inst.is_compressed:
            comp_path = self.get_path(inst, True)
            if not comp_path.is_file():
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'missing compressed file {comp_path}')
                self.downloader.download(inst.url, comp_path)
                downloaded_path = comp_path
            inst.uncompress(comp_path)
            target_path = comp_path
            uncompressed = True
        else:
            self.downloader.download(inst.url, dst_path)
            downloaded_path = dst_path
            target_path = dst_path
        return Status(inst, downloaded_path, target_path, uncompressed)

    @property
    @persisted('_by_name')
    def by_name(self) -> Dict[str, Resource]:
        """All resources as a dict with keys as their respective names."""
        return {i.name: i for i in self.installs}

    def install(self) -> List[Status]:
        """Download and install all resources.

        """
        statuses: List[Status] = []
        for inst in self.installs:
            local_path: Path = self.get_path(inst, False)
            status: Status = None
            if local_path.exists():
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'found: {local_path}--skipping')
                comp_path = self.get_path(inst, True)
                status = Status(inst, None, comp_path, False)
            else:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'missing {local_path}')
                status = self._install(inst, local_path)
            statuses.append(status)
        return statuses
