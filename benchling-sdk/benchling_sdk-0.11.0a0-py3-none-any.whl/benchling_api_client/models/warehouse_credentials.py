import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

import attr
from dateutil.parser import isoparse

T = TypeVar("T", bound="WarehouseCredentials")


@attr.s(auto_attribs=True, repr=False)
class WarehouseCredentials:
    """  """

    _expires_at: datetime.datetime
    _password: str
    _username: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("expires_at={}".format(repr(self._expires_at)))
        fields.append("password={}".format(repr(self._password)))
        fields.append("username={}".format(repr(self._username)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WarehouseCredentials({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        expires_at = self._expires_at.isoformat()

        password = self._password
        username = self._username

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "expiresAt": expires_at,
                "password": password,
                "username": username,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        expires_at = isoparse(d.pop("expiresAt"))

        password = d.pop("password")

        username = d.pop("username")

        warehouse_credentials = cls(
            expires_at=expires_at,
            password=password,
            username=username,
        )

        warehouse_credentials.additional_properties = d
        return warehouse_credentials

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def expires_at(self) -> datetime.datetime:
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: datetime.datetime) -> None:
        self._expires_at = value

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value
