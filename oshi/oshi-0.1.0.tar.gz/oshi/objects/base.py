from __future__ import annotations

__all__ = ("BaseObject",)


class BaseObject:
    """
    The base object that every object in this library will use.
    """

    def __init__(self, data: dict, *args, **kwargs):
        for key, value in data.items():
            if key == "id":
                continue

            try:
                setattr(self, key, value)
            except AttributeError:
                pass

        self.data = data

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ID={self.id}>"

    @property
    def id(self) -> int:
        return self.data["id"]
