from typing import Any


class InvalidInitialization(Exception):
    def __init__(self, obj: Any) -> None:
        super().__init__(
            f"Expected a string or dictionary with a cmd field. Received: {obj}"
        )


class InvalidRename(Exception):
    def __init__(self, obj: Any) -> None:
        super().__init__(
            f"Expected a string or dictionary with a segment field. Received: {obj}"
        )
