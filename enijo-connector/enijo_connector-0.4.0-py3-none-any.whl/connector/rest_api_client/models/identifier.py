from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="Identifier")


@attr.s(auto_attribs=True)
class Identifier:
    """Identifiers are described with the following subfields (note, we only support one identifier per scheme).

    Supported creator identifier schemes:

      - ORCID
      - GND
      - ISNI
      - ROR


    Supported affiliation identifier schemes:

      - ISNI
      - ROR"""

    identifier: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        identifier = cls(
            identifier=identifier,
        )

        identifier.additional_properties = d
        return identifier

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
