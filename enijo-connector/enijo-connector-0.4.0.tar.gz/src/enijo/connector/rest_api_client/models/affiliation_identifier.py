from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.affiliation_identifier_scheme import AffiliationIdentifierScheme

T = TypeVar("T", bound="AffiliationIdentifier")


@attr.s(auto_attribs=True)
class AffiliationIdentifier:
    """  """

    identifier: str
    scheme: AffiliationIdentifierScheme
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        scheme = self.scheme.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "scheme": scheme,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        scheme = AffiliationIdentifierScheme(d.pop("scheme"))

        affiliation_identifier = cls(
            identifier=identifier,
            scheme=scheme,
        )

        affiliation_identifier.additional_properties = d
        return affiliation_identifier

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
