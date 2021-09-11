from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="WarehouseCredentialsCreate")


@attr.s(auto_attribs=True, repr=False)
class WarehouseCredentialsCreate:
    """  """

    _expires_in: int

    def __repr__(self):
        fields = []
        fields.append("expires_in={}".format(repr(self._expires_in)))
        return "WarehouseCredentialsCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        expires_in = self._expires_in

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "expiresIn": expires_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        expires_in = d.pop("expiresIn")

        warehouse_credentials_create = cls(
            expires_in=expires_in,
        )

        return warehouse_credentials_create

    @property
    def expires_in(self) -> int:
        return self._expires_in

    @expires_in.setter
    def expires_in(self, value: int) -> None:
        self._expires_in = value
