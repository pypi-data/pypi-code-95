from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.affiliation_identifier import AffiliationIdentifier
from ..types import UNSET, Unset

T = TypeVar("T", bound="MetadataCreatorsItemAffiliationsItem")


@attr.s(auto_attribs=True)
class MetadataCreatorsItemAffiliationsItem:
    """  """

    name: str
    identifiers: Union[Unset, List[AffiliationIdentifier]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        identifiers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.identifiers, Unset):
            identifiers = []
            for identifiers_item_data in self.identifiers:
                identifiers_item = identifiers_item_data.to_dict()

                identifiers.append(identifiers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if identifiers is not UNSET:
            field_dict["identifiers"] = identifiers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        identifiers = []
        _identifiers = d.pop("identifiers", UNSET)
        for identifiers_item_data in _identifiers or []:
            identifiers_item = AffiliationIdentifier.from_dict(identifiers_item_data)

            identifiers.append(identifiers_item)

        metadata_creators_item_affiliations_item = cls(
            name=name,
            identifiers=identifiers,
        )

        metadata_creators_item_affiliations_item.additional_properties = d
        return metadata_creators_item_affiliations_item

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
