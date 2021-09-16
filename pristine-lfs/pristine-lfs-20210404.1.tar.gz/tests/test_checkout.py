from pristine_lfs import do_checkout
from pristine_lfs.util import Version


def test_pristine_lfs_simple_checkout(fake_pristine_lfs):
    repo, tarball, size, sha = fake_pristine_lfs
    outdir = repo / 'tmp'

    do_checkout('pristine-lfs', tarball=tarball.name, outdir=outdir)
    assert len(list(outdir.glob('**'))) == 1, list(outdir.glob('**'))
    assert (outdir / tarball.name).is_file(), 'Extracted tarball not found'
    assert (outdir / tarball.name).stat().st_size == size, 'Extracted tarball of a wrong size'


def test_pristine_lfs_auto_checkout(test_git_repo):
    repo, tarball, size, sha = test_git_repo
    outdir = repo / 'tmp-explicit'

    do_checkout('pristine-lfs', tarball=tarball.name, outdir=outdir)
    assert len(list(outdir.glob('*'))) == 1, list(outdir.glob('*'))
    assert (outdir / tarball.name).is_file()
    assert (outdir / tarball.name).stat().st_size == size

    outdir = repo / 'tmp-auto'

    do_checkout('pristine-lfs', tarball=None, outdir=outdir)
    assert len(list(outdir.glob('*'))) == 1, list(outdir.glob('*'))
    assert (outdir / tarball.name).is_file(), 'Extracted tarball not found'
    assert (outdir / tarball.name).stat().st_size == size, 'Extracted tarball of a wrong size'

    outdir = repo / 'tmp-empty'

    do_checkout('pristine-lfs', package='true', version='1', outdir=outdir)
    assert len(list(outdir.glob('*'))) == 0, list(outdir.glob('*'))
    assert not (outdir / tarball.name).is_file(), 'Found a tarball which should not be there'

    do_checkout('pristine-lfs', package='true', version=Version('1'), outdir=outdir)
    assert len(list(outdir.glob('*'))) == 0, list(outdir.glob('*'))
    assert not (outdir / tarball.name).is_file(), 'Found a tarball which should not be there'

    do_checkout('pristine-lfs', package='true', version='0', outdir=outdir)
    assert len(list(outdir.glob('*'))) == 1, list(outdir.glob('*'))
    assert (outdir / tarball.name).is_file(), 'Extracted tarball not found'

    outdir = repo / 'tmp-empty-2'

    do_checkout('pristine-lfs', package='true', version='0', outdir=outdir)
    assert len(list(outdir.glob('*'))) == 1, list(outdir.glob('*'))
    assert (outdir / tarball.name).is_file(), 'Extracted tarball not found'
