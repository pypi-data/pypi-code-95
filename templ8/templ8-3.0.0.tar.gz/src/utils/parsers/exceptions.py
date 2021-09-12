from typing import Set


class MissingDataclassArguments(Exception):
    def __init__(self, missing: Set[str]) -> None:
        super().__init__(
            f"Failed to map arguments into the dataclass, missing: {missing}."
        )


class FileParsingError(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(f"Failed to parse {path}.")


class UnsupportedFormat(Exception):
    def __init__(self, path: str, markup: str) -> None:
        super().__init__(f"Unable to parse {path}. Was expecting {markup}.")
