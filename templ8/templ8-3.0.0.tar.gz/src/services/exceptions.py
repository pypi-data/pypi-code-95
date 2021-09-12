from typing import List, Set

from ..models.collection import Collection


class DuplicateCollections(Exception):
    def __init__(self, name: str, paths: List[str]) -> None:
        super().__init__(
            f"Found multiple collections with the name: {name}. Paths: {paths}."
        )


class MissingCollections(Exception):
    def __init__(self, missing_collections: Set[str]) -> None:
        super().__init__(
            f"Could not find all the specified collections: {missing_collections}"
        )


class MissingRenderContext(Exception):
    def __init__(self, collection: Collection, missing_context: Set[str]) -> None:
        super().__init__(
            f"Missing required context: {missing_context}, in collection: {collection.name}"
        )


class MissingRename(Exception):
    def __init__(self, token: str, collection_name: str) -> None:
        super().__init__(
            f"Missing rename token: {token}, in collection: {collection_name}"
        )


class InvalidRenameLookup(Exception):
    def __init__(self, token: str, lookup: str, collection_name: str) -> None:
        super().__init__(
            f"""
            Invalid rename replacement: {lookup}, from token: {token},
            in collection: {collection_name}
            """
        )
