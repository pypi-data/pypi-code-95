import logging
from typing import List

from ..models.collection import Collection
from ..models.settings import Settings
from ..services.exceptions import (InvalidRenameLookup, MissingCollections,
                                   MissingRenderContext)
from ..services.finders import select_files
from ..services.runtime import finalize_render_context
from ..services.schemas import schema

logger = logging.getLogger(__file__)


def introspect_state(settings: Settings, collections: List[Collection]) -> None:
    logger.debug("Checking for missing collections.")
    missing_collections = set(settings.collections) - set(i.name for i in collections)

    if missing_collections:
        raise MissingCollections(missing_collections)

    logger.debug("Checking for missing render context.")

    for collection in collections:
        finalized_render_context = finalize_render_context(collection, settings)

        template_tokens = [
            name
            for path in select_files(collection, settings)
            for name in schema(path)["required"]
            if "required" in schema(path)
        ]

        rename_tokens = [rename.token for rename in collection.renames]

        required_context = set(template_tokens) | set(rename_tokens)
        missing_context = required_context - set(finalized_render_context.keys())

        if missing_context:
            raise MissingRenderContext(collection, missing_context)

        # By checking for InvalidRenameLookup errors early we avoid
        # aborting a templating run midway.
        logger.debug("Checking for invalid rename lookups.")
        for token in rename_tokens:

            # We've already checkied that the token is in the render context keys.
            lookup = finalized_render_context[token]

            if not isinstance(lookup, str) or len(lookup) == 0:
                raise InvalidRenameLookup(token, lookup, collection.name)
