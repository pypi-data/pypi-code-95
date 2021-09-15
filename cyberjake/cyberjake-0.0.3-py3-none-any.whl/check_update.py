"""Script to check for available updates."""
from distutils.version import LooseVersion
import json

try:
    import requests

    REQUESTS_PRESENT = True
except ModuleNotFoundError:
    REQUESTS_PRESENT = False


def check_update(project_name: str, current_version: str) -> bool:
    """Check version against pypi.org information

    **Requires Requests**

    :param project_name: Name of project to check
    :param current_version: Current version of project. Usually from __version__
    :return: Latest version is newer. Returns false if project can't be found
    :rtype: bool
    """
    if not REQUESTS_PRESENT:
        raise ModuleNotFoundError("Requests module needed")

    try:
        latest = LooseVersion(
            requests.get(f"https://pypi.org/pypi/{project_name}/json").json()["info"]["version"]
        )
    except json.decoder.JSONDecodeError:
        return False
    return latest > current_version
