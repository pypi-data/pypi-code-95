from __future__ import annotations

import typing

__all__ = ("Authentication",)


class Authentication:
    def __init__(self, client_id: int, client_secret: str):
        self.data: typing.Dict[typing.Union[str, int], typing.Union[str, int]] = {
            "client_id": client_id,
            "client_secret": client_secret,
        }

    def __repr__(self) -> str:
        return f"<Authentication ID={self.data['client_id']}>"

    def __getitem__(self, key: typing.Union[str, int]) -> typing.Any:
        return self.data[key]

    def __setitem__(self, key: typing.Union[str, int], value: typing.Any) -> typing.Any:
        self.data[key] = value

    @property
    def access_token(self) -> str:
        return self["token"]["access_token"]
