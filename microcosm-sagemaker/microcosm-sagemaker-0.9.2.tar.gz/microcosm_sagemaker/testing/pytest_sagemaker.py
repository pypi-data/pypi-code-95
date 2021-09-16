"""
Upload pytest runs to wandb

Adapted from the pastebin code:
https://github.com/pytest-dev/pytest/blob/e40bf1d1da6771f951bd4b6126fc3cb107a7c9e7/src/_pytest/pastebin.py

"""

from io import StringIO
from json import load
from logging import info, warning
from tempfile import NamedTemporaryFile, TemporaryFile

import pytest  # noqa: 401
import wandb  # noqa: 401

from microcosm_sagemaker.constants import ARTIFACT_CONFIGURATION_PATH, SagemakerPath


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    terminal_reporter = config.pluginmanager.getplugin("terminalreporter")

    # If no terminal reporter plugin is present, nothing we can do here;
    # this can happen when this function executes in a slave node
    # when using pytest-xdist, for example
    if terminal_reporter is None:
        return

    # Monkey-patch the write function
    config._pytestsessionfile = TemporaryFile('w+')
    oldwrite = terminal_reporter._tw.write

    def tee_write(s, **kwargs):
        oldwrite(s, **kwargs)
        config._pytestsessionfile.write(str(s))

    terminal_reporter._tw.write = tee_write


def pytest_unconfigure(config):
    # Only write the data upon test close if we have access to the written file
    if not hasattr(config, "_pytestsessionfile"):
        return

    # Get terminal contents and delete file
    config._pytestsessionfile.seek(0)
    sessionlog = config._pytestsessionfile.read()
    config._pytestsessionfile.close()

    del config._pytestsessionfile

    # Undo our patching in the terminal reporter
    terminal_reporter = config.pluginmanager.getplugin('terminalreporter')
    del terminal_reporter._tw.__dict__['write']

    # Write summary
    create_new_file(contents=sessionlog)


def pytest_terminal_summary(terminal_reporter):
    import _pytest.config  # noqa: 401

    if "failed" in terminal_reporter.stats:
        for rep in terminal_reporter.stats.get('failed'):
            file = StringIO()

            terminal_writer = _pytest.config.create_terminal_writer(terminal_reporter.config, file)
            rep.toterminal(terminal_writer)

            pytest_value = file.getvalue()
            assert len(pytest_value)

            create_new_file(contents=pytest_value)


def create_new_file(contents):
    """
    Uploads the provided contents to the wandb
    session that is linked to this artifact.

    """
    # Access our artifact's configuration file
    configuration_path = SagemakerPath.MODEL / ARTIFACT_CONFIGURATION_PATH

    # We are not operating in an environment that has access to an artifact file
    # No-op out of the upload
    if not configuration_path.exists():
        return

    with open(configuration_path) as file:
        configuration = load(file)
        run_path = configuration.get("wandb", {}).get("run_path", {})

    if not run_path:
        warning("Unable to upload logging file to `wandb`: no runpath found")
        return

    # Load the wandb run that is linked to this artifact
    api = wandb.Api()
    run = api.run(run_path)
    info(f"Writing results to wandb run: {run_path}")

    with NamedTemporaryFile(prefix="artifact-test-", suffix=".log", mode="w+") as file:
        file.write(contents)
        file.seek(0)

        run.upload_file(file.name, root="/")
