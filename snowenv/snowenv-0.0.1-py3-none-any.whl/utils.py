import logging
import subprocess
import importlib.metadata


def get_version() -> str:
    """Checks _version.py or build metadata for package version.
    Returns:
        str: Version string.
    """

    try:
        from ._version import version  # pylint: disable=import-error

        return version
    except ModuleNotFoundError:
        logging.debug("No _version.py found")

    try:
        return importlib.metadata.version("snowenv")
    except importlib.metadata.PackageNotFoundError:
        logging.warning("No version found in metadata")

    return "0.0.0-UNKONWN"


def shell(command: str) -> int:
    """Executes shell command.

    Args:
        command (str): Shell command.

    Returns:
        int: Return code (0 = ok, otherwise error).
    """

    p = subprocess.Popen(command, shell=True)
    p.communicate()
    return p.returncode
