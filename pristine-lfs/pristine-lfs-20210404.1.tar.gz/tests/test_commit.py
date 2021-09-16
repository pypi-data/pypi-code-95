from textwrap import dedent

import pytest
from sh.contrib import git

from pristine_lfs import do_commit, do_commit_files
from pristine_lfs.errors import DifferentFilesExist


def test_pristine_lfs_commit(fake_tarball):
    repo, tarball, size, sha = fake_tarball

    do_commit(tarball.open('rb'), branch='pristine-lfs')
    do_commit(tarball.open('rb'), branch='pristine-lfs', message='blip %s %s %s')
    do_commit(tarball.open('rb'), branch='pristine-lfs', message='blip')

    # verify the file has indeed been committed
    commit = git('rev-parse', 'pristine-lfs^{tree}').strip('\n')
    pointer = git('cat-file', 'blob', f"{commit}:{tarball.name}")
    assert pointer == dedent(
        f"""
        version https://git-lfs.github.com/spec/v1
        oid sha256:{sha}
        size {size}
        """).lstrip('\n'), 'Object pointer doesn’t match the object'

    stored = repo / '.git' / 'lfs' / 'objects' / sha[:2] / sha[2:4] / sha
    assert stored.is_file(), 'Object has not been stored by LFS'


def test_pristine_lfs_commit_overwrite(fake_tarball):
    repo, tarball, size, sha = fake_tarball

    do_commit(tarball.open('rb'), branch='pristine-lfs')
    tarball.write_text('Text')

    with pytest.raises(DifferentFilesExist):
        do_commit(tarball.open('rb'), branch='pristine-lfs', message='blip %s %s %s')


def test_pristine_lfs_commit_overwrite_forced(fake_tarball):
    repo, tarball, size, sha = fake_tarball

    do_commit(tarball.open('rb'), branch='pristine-lfs')
    tarball.write_text('Text')

    do_commit(tarball.open('rb'), branch='pristine-lfs', message='blip %s %s %s', force_overwrite=True)


def test_pristine_lfs_commit_files(fake_tarball):
    repo, tarball, size, sha = fake_tarball

    sig = tarball.with_suffix('.gz.asc')
    fake_sig_text = 'Fake signature'
    sig.write_text(fake_sig_text)

    do_commit_files([tarball.open('rb'), sig.open('rb')], branch='pristine-lfs', message='blip %s %s %s')

    commit = git('rev-parse', 'pristine-lfs^{tree}').strip('\n')
    pointer = git('cat-file', 'blob', f"{commit}:{tarball.name}")
    assert pointer == dedent(
        f"""
        version https://git-lfs.github.com/spec/v1
        oid sha256:{sha}
        size {size}
        """).lstrip('\n'), 'Object pointer doesn’t match the object'

    sig_text = git('cat-file', 'blob', f"{commit}:{sig.name}")
    assert sig_text == fake_sig_text
