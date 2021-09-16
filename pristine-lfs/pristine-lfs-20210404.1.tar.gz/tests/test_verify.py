from pristine_lfs import do_commit, do_verify


def test_pristine_lfs_commit(fake_tarball):
    repo, tarball, size, sha = fake_tarball

    do_commit(tarball.open('rb'), branch='pristine-lfs')
    do_commit(tarball.open('rb'), branch='pristine-lfs', message='blip %s %s %s')
    do_commit(tarball.open('rb'), branch='pristine-lfs', message='blip')

    # verify the file has indeed been committed
    assert do_verify(branch='pristine-lfs', tarball=tarball), 'Tarball doesn’t match the one in Git LFS'

    # now try a different file
    tarball.write_text('dummy')
    assert not do_verify(branch='pristine-lfs', tarball=tarball), 'Corrupted tarball not detected'
