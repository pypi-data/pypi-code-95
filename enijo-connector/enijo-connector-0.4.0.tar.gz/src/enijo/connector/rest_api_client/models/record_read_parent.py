from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.record_read_parent_access import RecordReadParentAccess
from ..types import UNSET, Unset

T = TypeVar("T", bound="RecordReadParent")


@attr.s(auto_attribs=True)
class RecordReadParent:
    """ The internal persistent identifier for all versions. """

    id: Union[Unset, str] = UNSET
    access: Union[Unset, RecordReadParentAccess] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        access: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.access, Unset):
            access = self.access.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if access is not UNSET:
            field_dict["access"] = access

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _access = d.pop("access", UNSET)
        access: Union[Unset, RecordReadParentAccess]
        if isinstance(_access, Unset):
            access = UNSET
        else:
            access = RecordReadParentAccess.from_dict(_access)

        record_read_parent = cls(
            id=id,
            access=access,
        )

        record_read_parent.additional_properties = d
        return record_read_parent

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
