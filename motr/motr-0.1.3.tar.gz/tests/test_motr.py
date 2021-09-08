import re
from unittest import mock

import blessed
import oschmod
import pytest


def fake_open_for_read(exc_type):
    def open(path, mode):
        assert mode == "rb"
        raise exc_type

    return open


def not_found(path):
    return f"^MOTRfile {re.escape(str(path))} not found.$"


def not_a_file(path):
    return f"^MOTRfile at {re.escape(str(path))} is a directory.$"


def no_permission(path):
    return (
        "^Insufficient permissions to read MOTRfile at"
        f" {re.escape(str(path))}.$"
    )


def unknown_os_error(path):
    return (
        f"^Unexpected IO error reading MOTRfile at {re.escape(str(path))}."
        " Please file an issue.$"
    )


def unknown_general_error(path):
    return (
        f"Unexpected general error reading MOTRfile at {re.escape(str(path))}."
        " Please file an issue.$"
    )


def no_parse(path):
    return (
        f"^Could not parse MOTRfile at {re.escape(str(path))};"
        " encountered the following exception:"
    )


def runtime_exception(path):
    return (
        f"^The MOTRfile at {re.escape(str(path))}"
        " encountered the following exception:"
    )


def no_config(path):
    return (
        f"^The MOTRfile at {re.escape(str(path))}"
        " did not produce a configuration object.$"
    )


def invalid_config(path):
    return (
        f"^The MOTRfile at {re.escape(str(path))} "
        "produced an invalid configuration object:"
    )


@pytest.fixture(name="implicit_runner")
def _implicit_runner(test_helpers, exc):
    def implicit_runner(msg):
        with pytest.raises(exc.MOTRError, match=msg):
            with test_helpers.MOTRTest() as app:
                app.run()

    return implicit_runner


def test_no_config_implicit(implicit_expected, implicit_runner):
    msg = not_found(implicit_expected)
    implicit_runner(msg)


def test_not_a_file_implicit(implicit_actual, implicit_runner):
    implicit_actual.mkdir()
    msg = not_a_file(implicit_actual)
    implicit_runner(msg)


def test_no_permission_implicit(implicit_actual, implicit_runner):
    implicit_actual.touch()
    # If this doesn't work on Windows,
    # the first argument needs to be coerced to str.
    oschmod.set_mode(implicit_actual, "a-r")
    msg = no_permission(implicit_actual)
    implicit_runner(msg)


@pytest.mark.parametrize("char", [")", "\0"])
def test_unparseable_config_implicit(char, implicit_actual, implicit_runner):
    implicit_actual.write_text(char)
    msg = no_parse(implicit_actual)
    implicit_runner(msg)


def test_runtime_exception_config_implicit(implicit_actual, implicit_runner):
    implicit_actual.write_text("1/0")
    msg = runtime_exception(implicit_actual)
    implicit_runner(msg)


def test_no_config_obj_implicit(implicit_actual, implicit_runner):
    implicit_actual.touch()
    msg = no_config(implicit_actual)
    implicit_runner(msg)


def test_invalid_config_implicit(implicit_actual, implicit_runner):
    implicit_actual.write_text("MOTR_CONFIG = None")
    msg = invalid_config(implicit_actual)
    implicit_runner(msg)


UNKNOWN_ERROR_PARAMS = pytest.mark.parametrize(
    "msg_writer,patched_open",
    [
        (unknown_os_error, fake_open_for_read(OSError)),
        (unknown_general_error, fake_open_for_read(Exception)),
    ],
)


@UNKNOWN_ERROR_PARAMS
def test_unknown_error_implicit(
    implicit_actual, implicit_runner, msg_writer, patched_open
):
    implicit_actual.touch()
    msg = msg_writer(implicit_actual)
    with mock.patch("motr.controllers.base.open", new=patched_open):
        implicit_runner(msg)


LIST_PARAMS = pytest.mark.parametrize(
    "config,result",
    [
        (
            """\
import itertools

from motr import api


ACTION = object()  # Not much is needed if we're not running the tasks.

MOTR_CONFIG = api.build(
    itertools.chain(
        api.action(ACTION),
        api.target("default_target", ACTION, "default"),
        api.target("non_default_target", ACTION, "non_default"),
        api.skipped_name("non_default"),
    ),
)
""",
            """\
{term.green}Default Targets:
default
{term.normal}{term.yellow}Non-default Targets:
non_default
{term.normal}
""",
        ),
        (
            """\
import itertools

from motr import api


ACTION = object()  # Ditto

MOTR_CONFIG = api.build(
    itertools.chain(
        api.action(ACTION),
        api.target("target", ACTION, "default-actions"),
    ),
)
""",
            """\
{term.green}Default Targets:
default-actions
{term.normal}
""",
        ),
    ],
)

LIST_ARG = pytest.mark.parametrize(
    "list_arg", ["-l", "--list-targets", "--list"]
)
COLOR_ARG = pytest.mark.parametrize(
    "term,color_arg",
    [
        (blessed.Terminal(force_styling=None), "never"),
        (blessed.Terminal(force_styling=True), "always"),
    ],
)


@LIST_ARG
@LIST_PARAMS
@COLOR_ARG
def test_list_implicit(
    implicit_actual, test_helpers, list_arg, term, color_arg, config, result
):
    implicit_actual.write_text(config)

    with test_helpers.MOTRTest(argv=[list_arg, "--color", color_arg]) as app:
        app.run()

    assert app.last_rendered[1] == result.format(term=term)


EMPTY_REGISTRY = """\
from motr import api


MOTR_CONFIG = api.build(())
"""

# Should make it warn on empty registry?
EMPTY_MSG = """\
{term.yellow}No actions ran.{term.normal}
"""


@COLOR_ARG
def test_empty_registry_implicit(
    implicit_actual, test_helpers, term, color_arg
):
    implicit_actual.write_text(EMPTY_REGISTRY)

    with test_helpers.MOTRTest(argv=["--color", color_arg]) as app:
        app.run()

    assert app.last_rendered[1] == EMPTY_MSG.format(term=term)


@COLOR_ARG
def test_empty_registry_implicit_twice(
    implicit_actual, test_helpers, term, color_arg
):
    implicit_actual.write_text(EMPTY_REGISTRY)

    with test_helpers.MOTRTest(argv=["--color", color_arg]) as app:
        app.run()

    assert app.last_rendered[1] == EMPTY_MSG.format(term=term)

    with test_helpers.MOTRTest(argv=["--color", color_arg]) as app:
        app.run()

    assert app.last_rendered[1] == EMPTY_MSG.format(term=term)


BASIC_REGISTRY = """\
import pathlib

from motr import api
from motr._api.actions import io
from motr._api.requirements import name_target

target_file = pathlib.Path("target-file")

def changes():
    yield from api.write_bytes(io.Input(target_file), b"")
    yield from name_target.name_target(target_file, "test")


MOTR_CONFIG = api.build(changes())
"""


BASIC_MSG = """\
{term.green}Passed:
WriteBytes(path=PosixPath('target-file'), data=b''){term.normal}
"""


@COLOR_ARG
def test_basic_registry_implicit(
    implicit_actual, test_helpers, term, color_arg
):
    implicit_actual.write_text(BASIC_REGISTRY)

    with test_helpers.MOTRTest(argv=["--color", color_arg]) as app:
        app.run()

    assert app.last_rendered[1] == BASIC_MSG.format(term=term)


@COLOR_ARG
def test_basic_registry_targets(
    implicit_actual, test_helpers, term, color_arg
):
    implicit_actual.write_text(BASIC_REGISTRY)

    with test_helpers.MOTRTest(
        argv=["--color", color_arg, "--target", "test"]
    ) as app:
        app.run()

    assert app.last_rendered[1] == BASIC_MSG.format(term=term)
