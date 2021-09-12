import os

import pytest


@pytest.fixture
def tempdir():
    tempdir = tempfile.mkdtemp()
    return tempdir


@pytest.fixture(scope="module")
def datadir(request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    basename, _ = os.path.split(filename)
    return os.path.join(basename, "data")
