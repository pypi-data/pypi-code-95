from pristine_lfs import do_list


def test_pristine_lfs_list(test_git_repo):
    ret = list(do_list(branch='pristine-lfs'))
    assert [test_git_repo.tarball.name] == ret, 'Expected tarball not found'

    ret = list(do_list(branch='debian/test'))
    assert ["debian/changelog"] == ret, 'This branch should only have the changelog'
