import re
from typing import Union
from semantic_version import Version
from semver import VersionInfo


def pypi_version_to_semver(version):
    # type: (str) -> Union[VersionInfo, None]
    """
    Converts pypi version to VersionInfo if possible, if not returns None.
    :param version: PyPi version
    :return: VersionInfo object
    """
    suffix_expression = re.compile(r'(\.dev|[abc]|rc|\.post)\d+$')
    cleaned_version = suffix_expression.sub('', version)
    return semver_parse(cleaned_version)


def semver_parse(version_string):
    # type: (str) -> Union[VersionInfo, None]
    try:
        version = Version(version_string, partial=True)
        if not version.minor:
            version.minor = 0
        if not version.patch:
            version.patch = 0
        return VersionInfo.parse(str(version))
    except ValueError:
        return None
