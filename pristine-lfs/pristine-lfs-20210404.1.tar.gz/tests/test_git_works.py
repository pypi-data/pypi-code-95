import pytest


@pytest.mark.smoke
def test_git_works(fake_pristine_lfs):
    """
    This test succeeds when git and git-lfs work
    """
