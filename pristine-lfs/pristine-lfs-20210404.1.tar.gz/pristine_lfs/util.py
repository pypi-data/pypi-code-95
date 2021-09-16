# pristine-lfs
#
# Git and Git LFS routines
# This requires Git and git-lfs to be installed.
#
# Copyright (C) 2019—2021 Collabora Ltd
# Copyright (C) 2019—2021 Andrej Shadura <andrew.shadura@collabora.co.uk>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import hashlib
import os
from contextlib import contextmanager
from fnmatch import fnmatch, fnmatchcase
from gettext import gettext as _
from pathlib import Path
from typing import IO, Any, Generator, Iterable, Mapping, Optional, Sequence, Tuple, Union, cast

import sh
from debian.changelog import Version

from .errors import (
    DifferentFilesExist,
    GitBranchNotFound,
    GitFileNotFound,
    UnsupportedHashAlgorithm,
)
from .gitwrap import git
from .log import logger


gitattributes = """*.tar.* filter=lfs diff=lfs merge=lfs -text
*.tar.*.asc -filter -diff merge=binary -text
*.dsc -filter !diff merge=binary !text
"""

pre_push_hook = """#!/bin/sh -e

case "$GIT_LFS_SKIP_PUSH" in
    true | on | 1)
        exit 0
        ;;
    *)
        git lfs pre-push "$@"
        ;;
esac
"""

supported_lfs_hashsums = ['sha256']


@contextmanager
def open_index(name: str) -> Generator[Path, None, None]:
    index = Path(git_dir()) / f"index-{name}"
    if index.exists():
        index.unlink()
    try:
        yield index
    finally:
        if index.exists():
            index.unlink()


AttributeValue = Union[str, bool, None]
Attribute = Tuple[str, AttributeValue]


def parse_attr(attr: str) -> Attribute:
    """
    Parse a Git attribute into its value:

    >>> parse_attr('attr')
    ('attr', True)
    >>> parse_attr('-attr')
    ('attr', False)
    >>> parse_attr('!attr')
    ('attr', None)
    >>> parse_attr('attr=text')
    ('attr', 'text')
    """
    if attr.startswith('!'):
        return attr[1:], None
    if attr.startswith('-'):
        return attr[1:], False
    if '=' not in attr:
        return attr, True
    return cast(Attribute, tuple(attr.split('=', maxsplit=1)))


def parse_git_attributes(s: str) -> Iterable[tuple[str, Mapping[str, AttributeValue]]]:
    """
    Parse Git attributes from a string:

    >>> list(parse_git_attributes('''
    ... ab*     merge=filfre
    ... abc     -foo -bar
    ... *.c     frotz
    ... *
    ... '''))
    [('ab*', {'merge': 'filfre'}),
     ('abc', {'foo': False, 'bar': False}),
     ('*.c', {'frotz': True}),
     ('*', {})]
    >>> list(parse_git_attributes('[attr]binary -diff -merge -text'))
    [('[attr]binary', {'diff': False, 'merge': False, 'text': False})]
    >>> list(parse_git_attributes('''
    ... # this is a comment
    ... a*      foo !bar -baz
    ... abc     foo bar baz
    ... *.jpg -text -diff
    ... *               text=auto
    ... *.txt           text
    ... *.vcproj        text eol=crlf
    ... *.sh            text eol=lf
    ... *.jpg           -text
    ... '''))
    [('a*', {'foo': True, 'bar': None, 'baz': False}),
     ('abc', {'foo': True, 'bar': True, 'baz': True}),
     ('*.jpg', {'text': False, 'diff': False}),
     ('*', {'text': 'auto'}),
     ('*.txt', {'text': True}),
     ('*.vcproj', {'text': True, 'eol': 'crlf'}),
     ('*.sh', {'text': True, 'eol': 'lf'}),
     ('*.jpg', {'text': False})]
    """
    lines = [line.strip() for line in s.splitlines()]
    # strip comments, split each line by consecutive spaces
    lines = [line.split() for line in lines if len(line) and not line.startswith('#')]
    for line in lines:
        if len(line):
            glob, *attrs = line
            yield glob, {k: v for k, v in [
                parse_attr(a) for a in attrs
            ]}


default_gitattributes = list(parse_git_attributes(gitattributes))


def check_branch(name: str) -> Optional[str]:
    """
    Check a branch exists, return the hash it points at, if it does.

    None if there’s no such branch
    """
    try:
        return git('show-ref', '--heads', '--hash', '--', name)
    except sh.ErrorReturnCode:
        return None


def git_dir() -> str:
    return git('rev-parse', '--git-dir').strip('\n')


def git_head() -> str:
    return git('rev-parse', '-q', '--verify', '--symbolic-full-name', 'HEAD', _ok_code=[0, 1]).strip('\n')


def branch_remote(name: str) -> Optional[str]:
    '''
    Find an upstream remote for a tracking branch
    '''
    if not name.startswith('refs/heads/') and not name.startswith('refs/'):
        name = 'refs/heads/' + name
    return git('for-each-ref', '--format=%(upstream:remotename)', '--', name, _ok_code=[0, 1]).strip('\n') or None


def find_remote_branches(name: str) -> list[tuple[str, str]]:
    try:
        branches = [line.split(' ') for line in git('show-ref', '--', name).splitlines()]
        return [(b[0], b[1]) for b in branches if b[1].startswith('refs/remotes/')]
    except sh.ErrorReturnCode:
        return []


def preferred_remote_branch(remote_branches: list[tuple[str, str]]) -> tuple[str, str]:
    logger.debug("Remote branches: %r", remote_branches)
    current_remote = branch_remote(git_head())
    logger.debug("Current remote: %r", current_remote)
    remote_branches = [
        (commit, ref) for (commit, ref) in remote_branches
        if current_remote and ref.startswith('refs/remotes/' + current_remote)
    ] + remote_branches
    return remote_branches[0]


def track_remote_branch(name: str):
    remote_branches = find_remote_branches(name)
    if len(remote_branches) == 0:
        raise RuntimeError('remote branch expected but not found')
    commit, branch = preferred_remote_branch(remote_branches)
    git('branch', '--track', name, branch)


def find_branch(branch: str) -> str:
    if check_branch(branch) is None:
        remote_branches = find_remote_branches(branch)
        if remote_branches:
            commit, branch = preferred_remote_branch(remote_branches)
        else:
            raise GitBranchNotFound(branch)
    return branch


def store_lfs_object(io: Any) -> str:
    return str(git.lfs.clean(io.name, _in=io))


def store_git_object(io: Any) -> str:
    return git('hash-object', '-w', '--stdin', _in=io).strip('\n')


def stage_file(filename: Union[str, bytes], io: Any, index: Path = None):
    blob = store_git_object(io)
    if isinstance(filename, bytes):
        filename = filename.decode()
    git('update-index', '--add', '--replace', '--cacheinfo', "100644,%s,%s" % (blob, filename), index=index)


def create_commit(branch: str, message: str, index: Path = None) -> str:
    tree = git('write-tree', index=index).strip('\n')
    if not len(tree):
        raise RuntimeError('write-tree failed')

    if check_branch(branch) is not None:
        commit = git('commit-tree', tree, '-p', branch, _in=message).strip('\n')
    else:
        commit = git('commit-tree', tree, _in=message).strip('\n')
    if not len(commit):
        raise RuntimeError('commit-tree failed')

    git('update-ref', 'refs/heads/%s' % branch, commit)

    return commit


def refresh_main_index():
    git('update-index', '--ignore-submodules', '-q', '--ignore-missing', '--unmerged', '--refresh')


def parse_diff_entry(entry: str) -> Mapping[str, str]:
    r"""
    >>> parse_diff_entry(
    ... ":100644 100644 777f41fb18215a23a779a831b38d24ff6171775a c5ac094096d35c687c0cc5054b5a1433c293ebd5 M\tpristine_lfs/main.py"
    ... )
    {'srcmode': '100644',
     'dstmode': '100644',
     'srchash': '777f41fb18215a23a779a831b38d24ff6171775a',
     'dsthash': 'c5ac094096d35c687c0cc5054b5a1433c293ebd5',
     'srcname': 'pristine_lfs/main.py',
     'dstname': '',
     'status': 'M'}
    >>> parse_diff_entry(
    ... ":100644 100644 f0adb461cd94419245cf0b16a0edf1e2daf6688b f0adb461cd94419245cf0b16a0edf1e2daf6688b R100\told\tnew"
    ... )
    {'srcmode': '100644',
     'dstmode': '100644',
     'srchash': 'f0adb461cd94419245cf0b16a0edf1e2daf6688b',
     'dsthash': 'f0adb461cd94419245cf0b16a0edf1e2daf6688b',
     'srcname': 'old',
     'dstname': 'new',
     'status': 'R100'}
    """
    treediff, names = entry.split('\t', maxsplit=1)
    srcmode, dstmode, srchash, dsthash, status = treediff.lstrip(':').split(' ')
    srcname, _, dstname = names.partition('\t')
    return {
        'srcmode': srcmode,
        'dstmode': dstmode,
        'srchash': srchash,
        'dsthash': dsthash,
        'srcname': srcname,
        'dstname': dstname,
        'status': status,
    }


def commit_lfs_file(io: IO[bytes], branch: str, template: str = None, overwrite: bool = False):
    """
    Store the file in the LFS storage and commit it to a branch.
    """
    commit_lfs_files([io], branch, template=template, overwrite=overwrite)


def commit_lfs_files(ios: Sequence[IO[bytes]], branch: str, template: str = None, overwrite: bool = False):
    """
    Store the files in the LFS storage and commit them to a branch.
    """
    # make sure the pre-push hook has been set up
    hook_path = Path(git_dir()) / 'hooks' / 'pre-push'
    if not hook_path.is_file():
        try:
            hook_path.parent.mkdir(exist_ok=True)
            hook_path.write_text(pre_push_hook)
            hook_path.chmod(0o755)
        except IOError as e:
            logger.warning(_('Failed to set up pre-push hook: %s') % e.strerror)

    with open_index("pristine-lfs") as index:
        # make sure we include all previously committed files
        if check_branch(branch) is not None:
            git(git('ls-tree', '-r', '--full-name', branch), 'update-index', '--index-info', index=index)

        # make sure .gitattributes is present
        stage_file('.gitattributes', gitattributes, index=index)

        for io in ios:
            filename = os.path.basename(io.name)
            if not is_lfs_managed(os.path.basename(filename), default_gitattributes):
                stage_file(filename, io, index=index)
            else:
                metadata = store_lfs_object(io)
                stage_file(filename, metadata, index=index)

        if check_branch(branch) is not None:
            diff = git('diff-index', '--cached', branch, index=index).strip().splitlines()
            if not diff:
                logger.info(_("Nothing to commit"))
                return
            parsed_diff = [parse_diff_entry(d) for d in diff]
            overwritten = [d['srcname'] for d in parsed_diff if d['srchash'] != ('0' * 40) and d['srcname'] != '.gitattributes']
            if any(overwritten) and not overwrite:
                raise DifferentFilesExist(overwritten)

        if not template:
            template = "pristine-lfs data for %s"

        message = template.replace('%s', ', '.join([os.path.basename(io.name) for io in ios]))

        create_commit(branch, message, index=index)

        refresh_main_index()


def list_lfs_files(branch: str) -> list[str]:
    return git.lfs('ls-files', '--name-only', branch).splitlines()


def parse_entry(entry: str) -> tuple[str, ...]:
    info, name = entry.split('\t')
    mode, type, hash = info.split(' ')
    return mode, type, hash, name


def list_git_files(branch: str) -> Mapping[str, str]:
    entries = [parse_entry(line) for line in git('ls-tree', '-r', '--full-name', branch).splitlines()]
    return {e[3]: e[2] for e in entries if e[1] == 'blob'}


def is_lfs_managed(filename: str, attributes: Iterable[tuple[str, Mapping[str, AttributeValue]]]):
    lfs_managed = False
    for pattern, attrs in attributes:
        if fnmatchcase(filename, pattern):
            if 'filter' in attrs:
                lfs_managed = attrs['filter'] == 'lfs'
    return lfs_managed


def checkout_lfs_file(branch: str, filename: str, outdir: Union[str, Path] = '.'):
    files = list_git_files(branch)
    if '.gitattributes' in files:
        attributes = parse_git_attributes(git('cat-file', 'blob', files['.gitattributes']))
    else:
        attributes = []

    if filename not in files:
        raise GitFileNotFound(filename, branch)

    with (Path(outdir) / filename).open(mode='wb') as tarball:
        if is_lfs_managed(filename, attributes):
            metadata = git('cat-file', 'blob', files[filename])
            git.lfs.smudge(filename, _out=tarball, _in=metadata)
        else:
            git('cat-file', 'blob', files[filename], _out=tarball)


def verify_lfs_file(branch: str, tarball: Path) -> bool:
    files = list_git_files(branch)

    filename = tarball.name
    if filename not in files:
        raise GitFileNotFound(filename, branch)

    metadata = git('cat-file', 'blob', files[filename])
    parsed_metadata = dict(parse_pointer(metadata))
    oid = parsed_metadata['oid']
    algo, hashsum = oid.split(':', 1)
    if algo not in supported_lfs_hashsums:
        raise UnsupportedHashAlgorithm(algo)

    h = getattr(hashlib, algo)()
    with open(tarball, mode='rb') as f:
        while True:
            chunk = f.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    calc_hashsum = h.hexdigest()
    if hashsum == calc_hashsum:
        logger.info(f"{algo} hash for the tarball: {hashsum}, matches the stored one")
    else:
        logger.warning(_("%(tarball)s does not match stored hash (expected %(stored_hash)s, got %(tarball_hash)s)") % {
            'tarball': filename,
            'stored_hash': hashsum,
            'tarball_hash': calc_hashsum,
        })
    return hashsum == calc_hashsum


def checkout_package(package: str, version: Version, branch: str, outdir: Union[str, Path],
                     requested: Optional[Sequence[str]] = None):
    logger.info(_("Checking out files for {package} version {version} to {outdir}:").format(
        package=package,
        version=version, outdir=outdir
    ))
    tarball_glob = f'{package}_{version.upstream_version}.orig.tar.*'
    component_tarball_glob = f'{package}_{version.upstream_version}.orig-*.tar.*'

    files = list_git_files(branch)
    if requested:
        # TODO: handle missing files
        tarballs = [f for f in files if f in requested]
    else:
        tarballs = [f for f in files if fnmatch(f, tarball_glob) or fnmatch(f, component_tarball_glob)]

    for f in tarballs:
        logger.info("         ... {}".format(f))
        checkout_lfs_file(branch, f, outdir)
    logger.info(_("Done."))


def parse_pointer(pointer: IO[str]) -> Iterable[tuple[str, str]]:
    """
    Parse Git LFS file pointer into a mapping of keys to values

    >>> from io import StringIO
    >>> dict(parse_pointer(StringIO('''version https://git-lfs.github.com/spec/v1
    ... oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393
    ... size 12345
    ... ''')))
    {'version': 'https://git-lfs.github.com/spec/v1',
     'oid': 'sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393',
     'size': '12345'}
    """
    for line in pointer:
        key, value = line.rstrip('\n').split(' ', 1)
        yield key, value
