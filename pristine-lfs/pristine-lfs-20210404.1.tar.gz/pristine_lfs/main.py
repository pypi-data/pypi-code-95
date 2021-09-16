# pristine-lfs
#
# store pristine tarballs in Git LFS
#
# Copyright (C) 2019—2021 Collabora Ltd
# Copyright (C) 2019—2021 Andrej Shadura <andrew.shadura@collabora.co.uk>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
import os
import sys
from fnmatch import fnmatch
from gettext import gettext as _
from pathlib import Path
from typing import (
    IO,
    Iterable,
    Optional,
    Sequence,
    Union
)

import sh
from debian import deb822
from debian.changelog import Changelog, Version

from .errors import (
    CommandFailed,
    DifferentFilesExist,
    GitError,
    UnsupportedHashAlgorithm,
)
from .log import logger
from .util import (
    check_branch,
    checkout_lfs_file,
    checkout_package,
    commit_lfs_file,
    commit_lfs_files,
    find_branch,
    find_remote_branches,
    list_git_files,
    track_remote_branch,
    verify_lfs_file,
)


def do_commit(tarball: IO[bytes], branch: str, message: Optional[str] = None, force_overwrite: bool = False, **kwargs):
    """
    Commit the open file to a branch using Git LFS.
    Set force_overwrite to overwrite an existing file with the same name and a different checksum.
    Message may contain "%s" which gets replaced with a comma-separate list of the file committed.
    """
    if check_branch(branch) is None:
        if find_remote_branches(branch):
            track_remote_branch(branch)
    commit_lfs_file(tarball, branch, message, overwrite=force_overwrite)


def do_commit_files(tarballs: Sequence[IO[bytes]], branch: str, message: Optional[str] = None,
                    force_overwrite: bool = False, **kwargs):
    """
    Commit open files to a branch using Git LFS.
    Set force_overwrite to overwrite existing files with same names and different checksums.
    Message may contain "%s" which gets replaced with a comma-separate list of the file committed.
    """
    if check_branch(branch) is None:
        if find_remote_branches(branch):
            track_remote_branch(branch)
    commit_lfs_files(tarballs, branch, message, overwrite=force_overwrite)


def do_checkout(branch: str, tarball: Optional[str] = None, outdir: Union[str, Path] = '.', full: bool = False,
                package: Optional[str] = None, version: Union[str, Version, None] = None, **kwargs):
    """
    Check out one or multiple files.
    If tarball is non-None:
        * file name only: tarball to check out to outdir.
        * path with to file: the location where to check out to
    If tarball is None:
        * if package and version are specified, that version
          is checked out
        * a tarball corresponding to the latest entry in
          debian/changelog is found and checked out

    When full is set, tarball is a name of a .dsc file;
    all corresponding tarball *and* the .dsc file are
    checked out. If None, debian/changelog is used
    to find the set of files to check out.
    """
    branch = find_branch(branch)
    if tarball:
        path, slash, tarball = tarball.rpartition('/')
        if path:
            outdir = path
    else:
        if not package or not version:
            changelog = Path("debian/changelog")
            with changelog.open() as f:
                ch = Changelog(f, max_blocks=1)
            package, version = ch.package, ch.version

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if full:
        if tarball:
            dsc_file = tarball
        else:
            fver = Version(version)
            fver.epoch = None
            dsc_file = f'{package}_{fver}.dsc'
        logger.info(_("Checking out file {} in {}").format(dsc_file, outdir))
        checkout_lfs_file(branch, dsc_file, outdir)
        if dsc_file.endswith('.dsc'):
            with (outdir / dsc_file).open('r') as dsc:
                d = deb822.Dsc(dsc)
            package = str(d['Source'])
            version = Version(d['Version'])
            files = [f["name"] for f in d["Files"]]
            checkout_package(package, version, branch, outdir, files)
    else:
        if tarball:
            logger.info(_("Checking out file {} in {}").format(tarball, outdir))
            checkout_lfs_file(branch, tarball, outdir)
        else:
            checkout_package(str(package), Version(version), branch, outdir)


def do_list(branch: str, **kwargs) -> Iterable[str]:
    """
    List all files on the specified branch except .gitattributes.
    """
    branch = find_branch(branch)
    for f in list_git_files(branch):
        if f != '.gitattributes':
            yield f


def do_import(dsc: IO[str], branch: str, message: Optional[str] = None, force_overwrite: bool = False,
              full: bool = False, **kwargs):
    """
    Import all tarballs and detached signatures related to an open .dsc file.
    Set force_overwrite to overwrite an existing file with the same name and a different checksum.
    Message may contain "%s" which gets replaced with a comma-separate list of the file committed.
    When full is set, the .dsc file and the Debian packaging tarball are also imported.
    """
    d = deb822.Dsc(dsc)
    package = d['Source']
    version = Version(d['Version'])

    tarball_glob = f'{package}_{version.upstream_version}.orig.tar.*'
    component_tarball_glob = f'{package}_{version.upstream_version}.orig-*.tar.*'
    dsc_dir = os.path.dirname(dsc.name)

    if check_branch(branch) is None:
        if find_remote_branches(branch):
            track_remote_branch(branch)

    tarballs = [os.path.join(dsc_dir, f['name']) for f in d['Files']
                if full or fnmatch(f['name'], tarball_glob) or fnmatch(f['name'], component_tarball_glob)]
    if full:
        tarballs += [dsc.name]

    if tarballs:
        logger.info("Importing: %s" % " ".join(tarballs))
        commit_lfs_files([open(tarball, 'rb') for tarball in tarballs], branch, message, overwrite=force_overwrite)


def do_verify(branch: str, tarball: Union[str, Path], **kwargs) -> bool:
    """
    Verify an existing tarball is the same as the one committed with pristine-lfs.
    """
    branch = find_branch(branch)
    tarball = Path(tarball)
    return verify_lfs_file(branch, tarball)


def main(*args):
    prog = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(description=_('store pristine tarballs in Git LFS'), prog=prog)
    if args and hasattr(parser, 'exit_on_error'):
        parser.exit_on_error = False

    parser.add_argument('-v', '--verbose', action='count', help=_('be more verbose'))
    parser.add_argument('--debug', action='store_const', const=2, dest='verbose', help=_('be debuggingly verbose'))
    parser.set_defaults(verbose=0, func=lambda *x, **kw: parser.print_usage(file=sys.stderr))
    subparsers = parser.add_subparsers(required=False)

    parser_commit = subparsers.add_parser('commit', help=_('commit a tarball'))
    parser_commit.add_argument('--force-overwrite', action='store_true', help=_('overwrite already stored files'))
    parser_commit.add_argument('-m', '--message', default=None, help=_('commit message'))
    parser_commit.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_commit.add_argument('tarball', type=argparse.FileType('rb'), help=_('tarball to commit'))
    parser_commit.add_argument('upstream', nargs='?', default=None, help=_('ignored'))
    parser_commit.set_defaults(func=do_commit)

    # we have to do some trickery since argparse doesn’t support this syntax natively
    parser_checkout = subparsers.add_parser('checkout', help=_('checkout a tarball'))
    parser_checkout.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_checkout.add_argument('--full', default=False, action='store_true',
                                 help=_('also check out all related files of the Debian package'))
    parser_checkout.add_argument('-o', '--outdir', default='.', help=_('output directory for the tarball'))
    checkout_group = parser_checkout.add_mutually_exclusive_group(required=True)
    checkout_group.add_argument('--auto', default=False, action='store_true',
                                help=_('check out all tarballs required by the currently checked out Debian package'))
    checkout_group.add_argument('tarball', nargs='?', default=None, help=_('tarball to check out'))
    parser_checkout.set_defaults(func=do_checkout)

    parser_list = subparsers.add_parser('list', help=_('list tarballs stored in the repository'))
    parser_list.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_list.set_defaults(func=do_list)

    parser_import = subparsers.add_parser('import-dsc', help=_('import tarballs and their signatures from a .dsc'))
    parser_import.add_argument('dsc', type=argparse.FileType('r'), help='.dsc file to use')
    parser_import.add_argument('--force-overwrite', action='store_true', help=_('overwrite already stored files'))
    parser_import.add_argument('--full', default=False, action='store_true',
                               help=_('also import all related files of the Debian package'))
    parser_import.add_argument('-m', '--message', default=None, help=_('commit message'))
    parser_import.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_import.set_defaults(func=do_import)

    parser_verify = subparsers.add_parser('verify', help=_('verify a tarball against Git LFS metadata'))
    parser_verify.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_verify.add_argument('tarball', help=_('tarball to verify'))
    parser_verify.set_defaults(func=do_verify)

    args = parser.parse_args(args or sys.argv[1:])

    logging.basicConfig(format='{levelname[0]}: {message!s}', style='{', level=(logging.WARNING - 10 * args.verbose))

    # sh is printing debug on the info channel
    logging.getLogger(sh.__name__).setLevel(logging.WARNING - 10 * (args.verbose - 1))

    try:
        ret = args.func(**vars(args))
        if isinstance(ret, Iterable):
            for item in ret:
                print(item)
        elif isinstance(ret, bool):
            return 0 if ret else 1
    except CommandFailed as e:
        print(_('Failed to run %s:') % e.full_cmd, file=sys.stderr)
        print(e.stderr.decode(sh.DEFAULT_ENCODING, "replace"), file=sys.stderr)
        return e.exit_code
    except FileNotFoundError as e:
        print(_('abort: file %s not found ') % e.filename, file=sys.stderr)
        return os.EX_OSERR
    except OSError as e:
        print(_('I/O error: %s') % e, file=sys.stderr)
        return os.EX_OSERR
    except KeyboardInterrupt:
        print(file=sys.stderr)
        print(_('about: Interrupted by user'), file=sys.stderr)
        return 1
    except (DifferentFilesExist, GitError, UnsupportedHashAlgorithm) as e:
        print(_("abort: %s\n") % e, file=sys.stderr)
        return 1
