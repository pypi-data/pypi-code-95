from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.record_read_parent_access_owned_by_item import (
    RecordReadParentAccessOwnedByItem,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="RecordReadParentAccess")


@attr.s(auto_attribs=True)
class RecordReadParentAccess:
    """  """

    owned_by: Union[Unset, List[RecordReadParentAccessOwnedByItem]] = UNSET
    links: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        owned_by: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.owned_by, Unset):
            owned_by = []
            for owned_by_item_data in self.owned_by:
                owned_by_item = owned_by_item_data.to_dict()

                owned_by.append(owned_by_item)

        links: Union[Unset, List[str]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if owned_by is not UNSET:
            field_dict["owned_by"] = owned_by
        if links is not UNSET:
            field_dict["links"] = links

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        owned_by = []
        _owned_by = d.pop("owned_by", UNSET)
        for owned_by_item_data in _owned_by or []:
            owned_by_item = RecordReadParentAccessOwnedByItem.from_dict(
                owned_by_item_data
            )

            owned_by.append(owned_by_item)

        links = cast(List[str], d.pop("links", UNSET))

        record_read_parent_access = cls(
            owned_by=owned_by,
            links=links,
        )

        record_read_parent_access.additional_properties = d
        return record_read_parent_access

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
