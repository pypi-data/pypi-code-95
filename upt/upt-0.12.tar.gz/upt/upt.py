# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import argparse
from enum import Enum
import logging
import os
import urllib.request
import sys
import tempfile

from packaging.specifiers import SpecifierSet
import pkg_resources

import upt.checksum
import upt.exceptions
import upt.log


class Backend(object):
    def current_version(self, frontend, pkgname, output=None):
        """Return the currently packaged version of a package.

        This method must return the currently packaged version of PKGNAME,
        packaged using the given FRONTEND.
        TODO: output
        """
        return input(f'Current version of {pkgname} ({frontend.name})?')

    def update_package(self, pdiff, output=None):
        raise NotImplementedError()

    def needs_requirement_interactive(self, req, phase):
        while True:
            ret = input(f'Should we package {req} (phase {phase})? [y/n] ')
            if ret.lower() in ('y', 'yes'):
                return True
            elif ret.lower() in ('n', 'no'):
                return False
            else:
                continue  # pragma: nocover

    def needs_requirement(self, req, phase):
        logger = logging.getLogger('upt')
        if not hasattr(self, 'package_versions'):
            return self.needs_requirement_interactive(req, phase)

        versions = self.package_versions(req.name)
        if not versions:
            logger.info(f'Dependency {req}: currently not packaged. '
                        f'Packaging it.')
            return True

        if not req.specifier:
            logger.info(f'Dependency {req}: currently packaged, no specific '
                        f'version is required. Not packaging it.')
            return False

        s = SpecifierSet(req.specifier)
        compatible_versions = list(s.filter(versions))
        if compatible_versions:
            logger.info(f'Dependency {req}: at least one compatible version '
                        f'found in {compatible_versions}. Not packaging it.')
            return False
        else:
            logger.info(f'Dependency {req}: no compatible version found '
                        f'in {versions}. Packaging it.')
            return True


class Frontend(object):
    """Base class for all upt Frontends."""
    pass


class PackageUpToDateException(Exception):
    def __init__(self, pkgname, version):
        self.pkgname = pkgname
        self.version = version

    def __str__(self):
        return f'{self.pkgname} is already up-to-date ({self.version})'


class ArchiveType(Enum):
    SOURCE_TARGZ = 1
    RUBYGEM = 2


class ArchiveUnavailable(Exception):
    def __str__(self):
        return 'No such archive could be found'


class Archive(object):
    '''An archive file.

    This can be a source tarball, a Python wheel, a Ruby gem, a binary, etc.
    '''
    def __init__(self, url, archive_type=ArchiveType.SOURCE_TARGZ, size=0,
                 md5=None, sha256=None, rmd160=None, sha256_base64=None,
                 sha512=None):
        self.url = url
        self.archive_type = archive_type
        self._size = size
        self._filepath = None  # Absolute path on the local filesystem
        self._filename = None  # Filename on the local filesystem
        self._hashes = {}
        if md5 is not None:
            self.md5 = md5
        if sha256 is not None:
            self.sha256 = sha256
        if rmd160 is not None:
            self.rmd160 = rmd160
        if sha256_base64 is not None:
            self.sha256_base64 = sha256_base64
        if sha512 is not None:
            self.sha512 = sha512

    @property
    def filepath(self):
        if self._filepath is None:
            self._filepath = os.path.join(tempfile.gettempdir(), self.filename)
            urllib.request.urlretrieve(self.url, filename=self._filepath)
        return self._filepath

    @property
    def filename(self):
        if self._filename is None:
            self._filename = os.path.basename(self.url)
        return self._filename

    @property
    def size(self):
        if self._size == 0:
            self._size = os.stat(self.filepath).st_size
        return self._size

    def _checksum(self, hash_name):
        try:
            return self._hashes[hash_name]
        except KeyError:
            value = upt.checksum.compute_checksum(self.filepath, hash_name)
            self._hashes[hash_name] = value
            return value

    @property
    def md5(self):
        return self._checksum('md5')

    @md5.setter
    def md5(self, value):
        self._hashes['md5'] = value

    @property
    def rmd160(self):
        return self._checksum('rmd160')

    @rmd160.setter
    def rmd160(self, value):
        self._hashes['rmd160'] = value

    @property
    def sha256(self):
        return self._checksum('sha256')

    @sha256.setter
    def sha256(self, value):
        self._hashes['sha256'] = value

    @property
    def sha256_base64(self):
        return self._checksum('sha256_base64')

    @sha256_base64.setter
    def sha256_base64(self, value):
        self._hashes['sha256_base64'] = value

    @property
    def sha512(self):
        return self._checksum('sha512')

    @sha512.setter
    def sha512(self, value):
        self._hashes['sha512'] = value


class PackageRequirement(object):
    """Package Requirement.

    Two main attributes are used:
    - name: a string, representing the name of the package.
    - specifier: a string, representing a version specifier as defined in
                 https://www.python.org/dev/peps/pep-0440/#version-specifiers .
                 The format of the specifier is subject to changes.
    """
    def __init__(self, name, specifier=None):
        self.name = name
        self.specifier = specifier

    def __str__(self):
        if self.specifier is not None:
            return f'{self.name} ({self.specifier})'
        else:
            return f'{self.name}'

    def __eq__(self, other):
        return (self.name == other.name and
                self.specifier == other.specifier)


class Package(object):
    """Base class for all packages.

    Constructor arguments:
    - name: required, the name of the package
    - version: required, the version of the package, as a str

    Optional keyword arguments:
    - homepage: a string, representing the official homepage of the package
    - summary: a short summary of the package's purpose
    - description: a long description of the package's purpose
    - requirement: a dict with 3 keys:
        - 'config': the config dependencies of the package;
        - 'build': the build dependencies of the package;
        - 'run': the runtime dependencies of the package;
        - 'test': the test dependencies of the package.
      The values associated with these keys are always lists of
      PackageRequirement objects.
    - licenses: a list of upt.licenses.License objects
    """
    def __init__(self, name, version, **kwargs):
        self.name = name
        self.version = version
        self.homepage = kwargs.get('homepage', '')
        self.summary = kwargs.get('summary', '')
        self.description = kwargs.get('description', '')
        # Software requirements, as instances of PackageRequirement: {
        #     'build': [pkg1, ...],
        #     'run': [pkg2, ...],
        #     'test': [pkg3, ...]
        # }
        self.requirements = kwargs.get('requirements', {})
        self.licenses = kwargs.get('licenses', [])
        self.archives = kwargs.get('archives', [])

    def __str__(self):
        return f'{self.name}@{self.version}'

    def get_archive(self, archive_type=ArchiveType.SOURCE_TARGZ):
        for archive in self.archives:
            if archive.archive_type == archive_type:
                return archive
        else:
            raise ArchiveUnavailable()

    def _clean(self):
        for archive in self.archives:
            if archive._filepath is not None:
                os.remove(archive._filepath)


class PackageDiff(object):
    def __init__(self, old, new):
        self.old = old
        self.new = new

    @property
    def old_version(self):
        return self.old.version

    @property
    def new_version(self):
        return self.new.version

    def new_requirements(self, phase):
        old_names = [req.name for req in self.old.requirements.get(phase, [])]
        new_names = [req.name for req in self.new.requirements.get(phase, [])]
        added_names = set(new_names) - set(old_names)
        return [
            req for req in self.new.requirements.get(phase, [])
            if req.name in added_names
        ]

    def updated_requirements(self, phase):
        old_names = [req.name for req in self.old.requirements.get(phase, [])]
        new_names = [req.name for req in self.new.requirements.get(phase, [])]
        updated_names = set(old_names) & set(new_names)
        return [
            req for req in self.new.requirements.get(phase, [])
            if req.name in updated_names
        ]

    def deleted_requirements(self, phase):
        old_names = [req.name for req in self.old.requirements.get(phase, [])]
        new_names = [req.name for req in self.new.requirements.get(phase, [])]
        deleted_names = set(old_names) - set(new_names)
        return [
            req for req in self.old.requirements.get(phase, [])
            if req.name in deleted_names
        ]


def create_parser(frontends, backends):
    parser = argparse.ArgumentParser(prog='upt')

    subparsers = parser.add_subparsers(title='Commands', dest='cmd')

    # List backends
    subparsers.add_parser('list-backends',
                          help='List installed backends')

    # List frontends
    subparsers.add_parser('list-frontends',
                          help='List installed frontends')

    # Actually package software
    parser_package = subparsers.add_parser('package',
                                           help='Package a piece of software')
    required_args = parser_package.add_argument_group('Required arguments')
    required_args.add_argument('-f', '--frontend',
                               required=len(frontends) > 1,
                               choices=frontends,
                               default=frontends[0] if frontends else None,
                               help='Frontend to use')
    required_args.add_argument('-b', '--backend',
                               required=len(backends) > 1,
                               choices=backends,
                               default=backends[0] if backends else None,
                               help='Backend to use')
    logger_group = parser_package.add_mutually_exclusive_group()
    logger_group.add_argument('--debug', action='store_const',
                              const=logging.DEBUG, dest='log_level',
                              help='Print debug messages.')
    parser_package.add_argument('-o', '--output',
                                help='Output file/directory. Defaults to '
                                     'stdout/current directory. This may be '
                                     'ignored by the backend.')
    logger_group.add_argument('-q', '--quiet', action='store_const',
                              const=logging.CRITICAL+1, dest='log_level',
                              help='Suppress all logging output')
    parser_package.add_argument('-r', '--recursive', action='store_true',
                                help='Recursively package requirements'),
    parser_package.add_argument('-c', '--color', action='store_true',
                                help='Show colored logging output'),
    parser_package.add_argument('-u', '--update', action='store_true',
                                help='Update package'),
    parser_package.add_argument('package', help='Name of the package. '
                                                'Use <package>@<version> to '
                                                'package a specific version.')

    return parser


def _get_installed_plugins(entrypoint):
    plugins = {}
    for ep in pkg_resources.iter_entry_points(entrypoint):
        plugin_cls = ep.load()
        plugins[plugin_cls.name] = plugin_cls

    return plugins


def _get_installed_frontends():
    return _get_installed_plugins('upt.frontends')


def _get_installed_backends():
    return _get_installed_plugins('upt.backends')


def package(pkg_name, version, frontend, backend, output, recursive,
            packaged=[]):
    logger = logging.getLogger('upt')

    try:
        upt_pkg = None
        upt.log.logger_set_formatter(logger, 'Frontend')
        upt_pkg = frontend.parse(pkg_name, version)
        upt_pkg.frontend = frontend.name
        upt.log.logger_set_formatter(logger, 'Backend')
        backend.create_package(upt_pkg, output=output)
        packaged.append(pkg_name)
        if recursive:
            for phase, requirements in upt_pkg.requirements.items():
                for requirement in requirements:
                    # Let's not repackage what we have already packaged.
                    if requirement.name in packaged:
                        continue

                    if backend.needs_requirement(requirement, phase):
                        package(requirement.name, None, frontend, backend,
                                output, recursive, packaged)
    except upt.exceptions.UnhandledFrontendError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except (upt.exceptions.InvalidPackageNameError,
            upt.exceptions.InvalidPackageVersionError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    finally:
        if upt_pkg is not None:
            # We always want to clean up after ourselves.
            upt_pkg._clean()


def _extract_name_version_from_package(package):
    try:
        name, version = package.split('@')
    except ValueError:
        name, version = package, None
    return name, version or None


def update(pkg_name, version, frontend, backend, output):
    logger = logging.getLogger('upt')

    upt.log.logger_set_formatter(logger, 'Backend')
    old_version = backend.current_version(frontend, pkg_name, output)

    # Parse both the old and the new version of the package in order to create
    # a "diff".
    upt.log.logger_set_formatter(logger, 'Frontend')
    old_pkg = frontend.parse(pkg_name, old_version)
    old_pkg.frontend = frontend.name
    new_pkg = frontend.parse(pkg_name, version)
    new_pkg.frontend = frontend.name
    diff = PackageDiff(old_pkg, new_pkg)
    if diff.new_version == old_version:
        raise PackageUpToDateException(pkg_name, old_version)

    # Let the backend do its magic.
    upt.log.logger_set_formatter(logger, 'Backend')
    logger.info(f'Updating {pkg_name} from {old_version} to {new_pkg.version}')
    try:
        backend.update_package(diff, output=output)
    except NotImplementedError:
        logger.error(f'The "{backend.name}" backend  does not implement the '
                     'update feature yet.')
        sys.exit(1)


def main():
    frontends = _get_installed_frontends()
    backends = _get_installed_backends()
    parser = create_parser(list(frontends.keys()), list(backends.keys()))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # We need to handle this here, because if we let the parser run in an
    # environment without frontends/backends, it will return a useless error
    # message, such as "choose a frontend in {}".
    if sys.argv[1] == 'package':
        if not frontends:
            sys.exit('You need to install at least one frontend, for instance '
                     'upt-cpan, upt-pypi or upt-rubygems')

        if not backends:
            sys.exit('You need to install at least one backend, for instance '
                     'upt-fedora, upt-freebsd, upt-guix, upt-nix or '
                     'upt-openbsd')

    args = parser.parse_args()

    if args.cmd == 'list-backends':
        for backend in backends.keys():
            print(backend)
        sys.exit(0)

    if args.cmd == 'list-frontends':
        for frontend in frontends.keys():
            print(frontend)
        sys.exit(0)

    if args.cmd == 'package':
        # There will not be a KeyError here, since argparse will catch "wrong"
        # values for us.
        frontend = frontends[args.frontend]()
        backend = backends[args.backend]()
        name, version = _extract_name_version_from_package(args.package)
        upt.log.create_logger(args.log_level, args.color)
        if args.update:
            try:
                update(name, version, frontend, backend, args.output)
            except PackageUpToDateException as e:
                logger = logging.getLogger('upt')
                logger.info(e)
            except (upt.exceptions.InvalidPackageNameError,
                    upt.exceptions.InvalidPackageVersionError) as e:
                logger = logging.getLogger('upt')
                upt.log.logger_set_formatter(logger, 'Frontend')
                logger.error(e)
                sys.exit(1)
        else:
            package(name, version, frontend, backend, args.output,
                    args.recursive)
