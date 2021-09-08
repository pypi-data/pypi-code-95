from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.resource_type_id import ResourceTypeId

T = TypeVar("T", bound="MetadataResourceType")


@attr.s(auto_attribs=True)
class MetadataResourceType:
    """The type of the resource described by the record. The resource type must be selected from a controlled vocabulary which can be customized by each InvenioRDM instance.

    When interfacing with Datacite, this field is converted to a format compatible with 10. Resource Type` (i.e. type and subtype). DataCite allows free text for the specific subtype, however InvenioRDM requires this to come from a customizable controlled vocabulary.

    The resource type vocabulary also defines mappings to other vocabularies such as Schema.org, Citation Style Language, BibTeX, DataCite and OpenAIRE. These mappings are very important for the correct generation of citations due to how different types are being interpreted by reference management systems."""

    id: ResourceTypeId
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = ResourceTypeId(d.pop("id"))

        metadata_resource_type = cls(
            id=id,
        )

        metadata_resource_type.additional_properties = d
        return metadata_resource_type

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
