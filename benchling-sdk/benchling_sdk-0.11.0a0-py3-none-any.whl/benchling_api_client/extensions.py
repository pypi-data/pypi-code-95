from typing import Any


class NotPresentError(Exception):
    path: str
    message: str
    parent_name: str

    def __init__(self, parent: Any, path: str):
        self.path = path
        self.parent_name = type(parent).__name__
        self.message = f"Attempted to read '{self.parent_name}.{self.path}', which is Unset"
        super().__init__(self.message)
