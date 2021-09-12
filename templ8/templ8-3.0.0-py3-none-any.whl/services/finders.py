import logging
import os
from typing import List

from walkmate import get_child_files

from ..models.collection import Collection
from ..models.settings import Settings
from ..services.exceptions import DuplicateCollections
from ..utils.collections.lists import group_by, sieve, sort_with
from ..utils.strings.paths import path_tail

logger = logging.getLogger(__file__)

core_templates = os.path.normpath(os.path.join(__file__, "..", "..", "core"))


def gather_collections(settings: Settings) -> List[Collection]:
    collections = []
    collection_sources = settings.collection_sources

    logger.debug("Gathering collections, sources: %s", collection_sources)

    if not settings.skip_core_templates:
        collection_sources.append(core_templates)
        logger.debug("Included core templates at: %s", core_templates)

    else:
        logger.debug("Skipped including core templates.")

    for collection_source in collection_sources:
        logger.debug("Looking for collections in: %s", collection_source)

        for path in get_child_files(
            root=collection_source,
            max_depth=2,
            match_name="metadata.json",
        ):
            logger.info(path, extra={"progress": True})
            collection = Collection.parse(path)

            if collection.name in settings.collections:
                logger.debug("Including %s collection", collection.name)
                collections.append(collection)

    for name, group in filter(
        lambda x: len(x[1]) > 1,
        group_by(collections, "name").items(),
    ):
        raise DuplicateCollections(name, [path_tail(i.root) for i in group])

    return sort_with(collections, settings.collections, lambda x: x.name)


def filtered_select(
    paths: List[str], root: str, settings: Settings, extra_excludes: List[str]
) -> List[str]:
    return sieve(
        paths,
        lambda path: os.path.relpath(path, root),
        settings.includes if len(settings.includes) > 0 else None,
        [*settings.excludes, *extra_excludes],
    )


def select_files(collection: Collection, settings: Settings) -> List[str]:
    return filtered_select(
        get_child_files(path_tail(collection.root)),
        path_tail(collection.root),
        settings,
        ["metadata.json"],
    )


def select_top_level(settings: Settings) -> List[str]:
    return filtered_select(
        [i for i in os.listdir(settings.cwd) if os.path.isfile(i)],
        settings.cwd,
        settings,
        [os.path.relpath(settings.settings_file, settings.cwd)],
    )
