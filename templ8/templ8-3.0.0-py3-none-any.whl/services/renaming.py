import logging
import os
from typing import Any, Dict

from ..models.rename import Rename
from ..services.exceptions import InvalidRenameLookup, MissingRename
from ..utils.strings.paths import leads_path, path_tail

logger = logging.getLogger(__file__)


def rename_path(
    path: str,
    rename: Rename,
    collection_name: str,
    render_context: Dict[str, Any],
) -> str:

    if rename.token not in render_context:
        raise MissingRename(rename.token, collection_name)

    lookup = render_context[rename.token]

    if not isinstance(lookup, str) or len(lookup) == 0:
        raise InvalidRenameLookup(rename.token, lookup, collection_name)

    if not leads_path(rename.segment, path):
        return path

    return path.replace(
        rename.segment, os.path.join(path_tail(rename.segment), lookup), 1
    )
