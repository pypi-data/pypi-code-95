from rockset.alias import *
from rockset.client import *
from rockset.collection import *
from rockset.cursor import *
from rockset.document import *
from rockset.exception import *
from rockset.field_mapping import *
from rockset.integration import *
from rockset.query import *
from rockset.source import *
from rockset.value import *
from rockset.workspace import *
from rockset.swagger_client.models import *
from rockset.swagger_client.api import *

import json
import pkg_resources


def get_latest_pypi_version():
    import requests
    try:
        pypa_req = requests.get('https://pypi.org/pypi/rockset/json')
        pypa_req.raise_for_status()
        latest_version = pypa_req.json()['info']['version']
        return latest_version
    # supress exceptions that end user would be unlikely to want
    # to deal with
    except requests.exceptions.HTTPError:
        return ''


def check_for_updates():
    installed_version = version()
    latest_version = get_latest_pypi_version()
    if not latest_version:
        return installed_version

    conformed_installed_version = pkg_resources.parse_version(installed_version)
    conformed_latest_version = pkg_resources.parse_version(latest_version)
    if conformed_installed_version < conformed_latest_version:
        return '{} (warning: newer version {} available)'.format(
            installed_version, latest_version
        )

    return '{} (latest)'.format(installed_version)


def version():
    version_file = pkg_resources.resource_filename('rockset', 'version.json')
    try:
        with open(version_file, 'r') as vf:
            version = json.load(vf).get('python', None)
            if version is None:
                version = pkg_resources.require('rockset')[0].version
    except OSError as e:
        raise FileNotFoundError(
            'could not locate version.json in install dir. '
            'please uninstall and reinstall package "rockset"'
        ) from e

    return version


__version__ = version()

__all__ = [
    "Alias",
    "Client",
    "Collection",
    "Cursor",
    "Document",
    "FieldMapping",
    "ClusteringKey",
    "F",
    "FieldRef",
    "P",
    "ParamDict",
    "ParamRef",
    "Q",
    "Query",
    "Source",
    "Workspace",
]
