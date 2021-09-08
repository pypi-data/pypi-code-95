from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.creator_identifier import CreatorIdentifier
from ..models.metadata_creators_item_person_or_org_type import (
    MetadataCreatorsItemPersonOrOrgType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="MetadataCreatorsItemPersonOrOrg")


@attr.s(auto_attribs=True)
class MetadataCreatorsItemPersonOrOrg:
    """ The person or organization. """

    name: Union[Unset, str] = UNSET
    type: Union[Unset, MetadataCreatorsItemPersonOrOrgType] = UNSET
    given_name: Union[Unset, str] = UNSET
    family_name: Union[Unset, str] = UNSET
    identifiers: Union[Unset, List[CreatorIdentifier]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        given_name = self.given_name
        family_name = self.family_name
        identifiers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.identifiers, Unset):
            identifiers = []
            for identifiers_item_data in self.identifiers:
                identifiers_item = identifiers_item_data.to_dict()

                identifiers.append(identifiers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if type is not UNSET:
            field_dict["type"] = type
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if family_name is not UNSET:
            field_dict["family_name"] = family_name
        if identifiers is not UNSET:
            field_dict["identifiers"] = identifiers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, MetadataCreatorsItemPersonOrOrgType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = MetadataCreatorsItemPersonOrOrgType(_type)

        given_name = d.pop("given_name", UNSET)

        family_name = d.pop("family_name", UNSET)

        identifiers = []
        _identifiers = d.pop("identifiers", UNSET)
        for identifiers_item_data in _identifiers or []:
            identifiers_item = CreatorIdentifier.from_dict(identifiers_item_data)

            identifiers.append(identifiers_item)

        metadata_creators_item_person_or_org = cls(
            name=name,
            type=type,
            given_name=given_name,
            family_name=family_name,
            identifiers=identifiers,
        )

        metadata_creators_item_person_or_org.additional_properties = d
        return metadata_creators_item_person_or_org

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
