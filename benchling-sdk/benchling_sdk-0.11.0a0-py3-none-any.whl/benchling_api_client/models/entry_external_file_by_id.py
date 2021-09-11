from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.entry_external_file import EntryExternalFile

T = TypeVar("T", bound="EntryExternalFileById")


@attr.s(auto_attribs=True, repr=False)
class EntryExternalFileById:
    """  """

    _external_file: EntryExternalFile
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("external_file={}".format(repr(self._external_file)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryExternalFileById({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        external_file = self._external_file.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "externalFile": external_file,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        external_file = EntryExternalFile.from_dict(d.pop("externalFile"))

        entry_external_file_by_id = cls(
            external_file=external_file,
        )

        entry_external_file_by_id.additional_properties = d
        return entry_external_file_by_id

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def external_file(self) -> EntryExternalFile:
        return self._external_file

    @external_file.setter
    def external_file(self, value: EntryExternalFile) -> None:
        self._external_file = value
