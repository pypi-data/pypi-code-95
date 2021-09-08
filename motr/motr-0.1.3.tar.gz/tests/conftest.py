"""
PyTest Fixtures.
"""

import enum
import pathlib
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _restore_cwd(monkeypatch, base):
    monkeypatch.setattr(base, "chdir", monkeypatch.chdir)


class ToParent(enum.Enum):
    SELF = False
    PARENT = True


@pytest.fixture
def to_tmpdir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)
        yield tmpdir


@pytest.fixture(params=list(ToParent))
def to_parent(request):
    return request.param.value


@pytest.fixture
def implicit_expected(to_tmpdir, to_parent, monkeypatch):
    target = pathlib.Path(".")
    if to_parent:
        target /= "child"
        target.mkdir()
        monkeypatch.chdir(target)
    return pathlib.Path("motrfile.py").resolve()


@pytest.fixture
def implicit_actual(implicit_expected, to_tmpdir):
    return to_tmpdir / pathlib.Path("motrfile.py")


@pytest.fixture(scope="session", name="test_helpers")
def _test_helpers():
    import motr.test_helpers

    return motr.test_helpers


@pytest.fixture(scope="session")
def main():
    import motr.main

    return motr.main


@pytest.fixture(scope="session")
def exc():
    import motr.core.exc

    return motr.core.exc


@pytest.fixture(scope="session")
def registry():
    import motr.core.registry

    return motr.core.registry


@pytest.fixture(scope="session")
def result():
    import motr.core.result

    return motr.core.result


@pytest.fixture(scope="session")
def runner():
    import motr.core.runner

    return motr.core.runner


@pytest.fixture(scope="session")
def target():
    import motr.core.target

    return motr.core.target


@pytest.fixture(scope="session")
def base():
    import motr.controllers.base

    return motr.controllers.base


@pytest.fixture(scope="session")
def api():
    import motr.api

    return motr.api


@pytest.fixture(scope="session")
def io():
    import motr._api.actions.io

    return motr._api.actions.io


@pytest.fixture(scope="session")
def cmd():
    import motr._api.actions.cmd

    return motr._api.actions.cmd


@pytest.fixture(scope="session")
def mkdir():
    import motr._api.actions.mkdir

    return motr._api.actions.mkdir


@pytest.fixture(scope="session")
def write_bytes():
    import motr._api.actions.write_bytes

    return motr._api.actions.write_bytes
