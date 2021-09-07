import os
import pkg_resources
from fk.utils import read_file

import logging

logger = logging.getLogger(__name__)

__version__ = "0.0.0"
version_filename = "VERSION"

fk_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
fk_version_file = f"{fk_path}/{version_filename}"

if pkg_resources.resource_exists(__name__, version_filename):
    __version__ = pkg_resources.resource_string(__name__, version_filename).decode("utf-8").strip()
elif os.path.exists(fk_version_file):
    __version__ = read_file(fk_version_file)
else:
    logger.warning("No version found")
    pass
