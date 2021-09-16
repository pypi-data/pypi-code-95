import hashlib
import os
import tarfile
from pathlib import Path
from textwrap import dedent
from typing import NamedTuple, Optional

import pytest


try:
    from sh.contrib import git
except ImportError:
    assert False, "These tests require Git"


class WorkDir(NamedTuple):
    path: Path
    tarball: Optional[Path] = None
    size: Optional[int] = None
    sha: Optional[str] = None


@pytest.fixture
def empty_git_repo(tmp_path):
    os.chdir(tmp_path)
    git.init()
    git.config('user.name', 'Committer Name')
    git.config('user.email', 'name@example.org')
    git.config('commit.gpgsign', 'false')

    assert (tmp_path / '.git').is_dir()
    yield WorkDir(tmp_path)


@pytest.fixture(params=['/bin/true'])
def fake_tarball(empty_git_repo, request):
    repo, *_ = empty_git_repo

    tarball = Path('true_0.orig.tar.gz')
    with tarfile.open(tarball, mode='w:gz') as f:
        f.add(request.param)

    size = tarball.stat().st_size
    h = hashlib.sha256()
    with open(tarball, mode='rb') as f:
        while True:
            chunk = f.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    sha = h.hexdigest()

    yield WorkDir(repo, tarball, size, sha)


@pytest.fixture
def fake_pristine_lfs(fake_tarball):
    repo, tarball, size, sha = fake_tarball

    git.checkout('-b', 'pristine-lfs')
    git.lfs.track('*.tar.*')
    with Path('.gitattributes') as f:
        assert f.is_file()
        assert f.stat().st_size != 0
        git.add(f)

    git.add(tarball)
    git.commit(message=f'add {tarball.name}')
    commit = git('rev-parse', 'pristine-lfs^{tree}').strip('\n')
    pointer = git('cat-file', 'blob', f"{commit}:{tarball.name}")
    assert pointer == dedent(
        f"""
        version https://git-lfs.github.com/spec/v1
        oid sha256:{sha}
        size {size}
        """).lstrip('\n'), 'Object pointer doesn’t match the object'

    yield WorkDir(repo, tarball, size, sha)


@pytest.fixture
def test_git_repo(fake_pristine_lfs):
    repo, tarball, size, sha = fake_pristine_lfs

    # clean index
    empty = git('hash-object', '-t', 'tree', '/dev/null').strip('\n')
    git('read-tree', empty)
    # start a new empty branch
    git.checkout(orphan='debian/test')
    with Path('debian/changelog') as changelog:
        changelog.parent.mkdir()
        changelog.write_text(dedent(
            """
            true (0-0) UNRELEASED; urgency=medium
            
              * Empty.
            
             -- Nobody <nobody@example.org>  Thu, 01 Jan 1970 12:00:00 +0100
            """).lstrip('\n'))  # noqa: W293
        git.add(changelog)
    git.commit(message='pretend packaging')
    git.reset(hard=True)
    git.clean(force=True)

    yield WorkDir(repo, tarball, size, sha)


def pytest_collection_modifyitems(items):
    # sort doctests before normal tests
    # but run smoke tests first
    def test_key(item):
        return type(item).__name__, not [mark.name == 'smoke' for mark in item.iter_markers()]
    items.sort(key=test_key)
