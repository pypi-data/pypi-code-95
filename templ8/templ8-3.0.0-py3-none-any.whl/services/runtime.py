import logging
from functools import partial, reduce
from typing import Any, Dict

from ..models.collection import Collection
from ..models.settings import Settings
from ..services.renaming import rename_path
from ..utils.collections.dicts import merge_dicts

logger = logging.getLogger(__file__)


def finalize_path(path: str, collection: Collection, settings: Settings) -> str:
    return reduce(
        partial(
            rename_path,
            collection_name=collection.name,
            render_context=finalize_render_context(collection, settings),
        ),
        collection.renames,
        path,
    )


def finalize_render_context(
    collection: Collection, settings: Settings
) -> Dict[str, Any]:
    return merge_dicts(collection.default_variables, settings.render_context)
