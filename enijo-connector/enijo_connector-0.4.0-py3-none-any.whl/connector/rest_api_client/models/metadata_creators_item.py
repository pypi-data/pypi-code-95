from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.metadata_creators_item_affiliations_item import (
    MetadataCreatorsItemAffiliationsItem,
)
from ..models.metadata_creators_item_person_or_org import (
    MetadataCreatorsItemPersonOrOrg,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="MetadataCreatorsItem")


@attr.s(auto_attribs=True)
class MetadataCreatorsItem:
    """  """

    person_or_org: MetadataCreatorsItemPersonOrOrg
    affiliations: Union[Unset, List[MetadataCreatorsItemAffiliationsItem]] = UNSET
    role: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        person_or_org = self.person_or_org.to_dict()

        affiliations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.affiliations, Unset):
            affiliations = []
            for affiliations_item_data in self.affiliations:
                affiliations_item = affiliations_item_data.to_dict()

                affiliations.append(affiliations_item)

        role = self.role

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "person_or_org": person_or_org,
            }
        )
        if affiliations is not UNSET:
            field_dict["affiliations"] = affiliations
        if role is not UNSET:
            field_dict["role"] = role

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        person_or_org = MetadataCreatorsItemPersonOrOrg.from_dict(
            d.pop("person_or_org")
        )

        affiliations = []
        _affiliations = d.pop("affiliations", UNSET)
        for affiliations_item_data in _affiliations or []:
            affiliations_item = MetadataCreatorsItemAffiliationsItem.from_dict(
                affiliations_item_data
            )

            affiliations.append(affiliations_item)

        role = d.pop("role", UNSET)

        metadata_creators_item = cls(
            person_or_org=person_or_org,
            affiliations=affiliations,
            role=role,
        )

        metadata_creators_item.additional_properties = d
        return metadata_creators_item

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
