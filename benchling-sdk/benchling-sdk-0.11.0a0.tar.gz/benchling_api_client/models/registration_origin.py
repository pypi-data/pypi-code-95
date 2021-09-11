import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

import attr
from dateutil.parser import isoparse

T = TypeVar("T", bound="RegistrationOrigin")


@attr.s(auto_attribs=True, repr=False)
class RegistrationOrigin:
    """  """

    _registered_at: datetime.datetime
    _origin_entry_id: Optional[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("registered_at={}".format(repr(self._registered_at)))
        fields.append("origin_entry_id={}".format(repr(self._origin_entry_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RegistrationOrigin({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        registered_at = self._registered_at.isoformat()

        origin_entry_id = self._origin_entry_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "registeredAt": registered_at,
                "originEntryId": origin_entry_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        registered_at = isoparse(d.pop("registeredAt"))

        origin_entry_id = d.pop("originEntryId")

        registration_origin = cls(
            registered_at=registered_at,
            origin_entry_id=origin_entry_id,
        )

        registration_origin.additional_properties = d
        return registration_origin

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
    def registered_at(self) -> datetime.datetime:
        return self._registered_at

    @registered_at.setter
    def registered_at(self, value: datetime.datetime) -> None:
        self._registered_at = value

    @property
    def origin_entry_id(self) -> Optional[str]:
        return self._origin_entry_id

    @origin_entry_id.setter
    def origin_entry_id(self, value: Optional[str]) -> None:
        self._origin_entry_id = value
