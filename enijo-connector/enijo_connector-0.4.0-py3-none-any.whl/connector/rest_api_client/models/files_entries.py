from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.files_entries_additional_property import FilesEntriesAdditionalProperty

T = TypeVar("T", bound="FilesEntries")


@attr.s(auto_attribs=True)
class FilesEntries:
    """The entries field lists the associated digital files for the resource described by the record. The files must all be registered in Invenio-Files-REST store independently. This is to ensure that files can be tracked and fixity can be checked.
    The key represents a file path."""

    additional_properties: Dict[str, FilesEntriesAdditionalProperty] = attr.ib(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        files_entries = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = FilesEntriesAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        files_entries.additional_properties = additional_properties
        return files_entries

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> FilesEntriesAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: FilesEntriesAdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
