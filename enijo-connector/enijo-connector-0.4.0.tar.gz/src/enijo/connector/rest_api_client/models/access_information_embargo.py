import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessInformationEmbargo")


@attr.s(auto_attribs=True)
class AccessInformationEmbargo:
    """Embargo options for the record.
    The embargo field denotes when an embargo must be lifted, at which point the record is made publicly accessible.
    Only in the cases of "record": "restricted" or "files": "restricted" can an embargo be provided as input. However, once an embargo is lifted, the embargo section is kept for transparency."""

    active: bool
    until: Union[Unset, datetime.date] = UNSET
    reason: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        active = self.active
        until: Union[Unset, str] = UNSET
        if not isinstance(self.until, Unset):
            until = self.until.isoformat()

        reason = self.reason

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "active": active,
            }
        )
        if until is not UNSET:
            field_dict["until"] = until
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        active = d.pop("active")

        _until = d.pop("until", UNSET)
        until: Union[Unset, datetime.date]
        if isinstance(_until, Unset):
            until = UNSET
        else:
            until = isoparse(_until).date()

        reason = d.pop("reason", UNSET)

        access_information_embargo = cls(
            active=active,
            until=until,
            reason=reason,
        )

        access_information_embargo.additional_properties = d
        return access_information_embargo

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
