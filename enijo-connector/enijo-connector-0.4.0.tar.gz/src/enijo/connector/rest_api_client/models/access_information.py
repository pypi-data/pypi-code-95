from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.access_information_embargo import AccessInformationEmbargo
from ..models.access_information_files import AccessInformationFiles
from ..models.access_information_record import AccessInformationRecord
from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessInformation")


@attr.s(auto_attribs=True)
class AccessInformation:
    """ The access field denotes record-specific read (visibility) options. """

    record: AccessInformationRecord
    files: AccessInformationFiles
    emargo: Union[Unset, AccessInformationEmbargo] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        record = self.record.value

        files = self.files.value

        emargo: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.emargo, Unset):
            emargo = self.emargo.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "record": record,
                "files": files,
            }
        )
        if emargo is not UNSET:
            field_dict["emargo"] = emargo

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        record = AccessInformationRecord(d.pop("record"))

        files = AccessInformationFiles(d.pop("files"))

        _emargo = d.pop("emargo", UNSET)
        emargo: Union[Unset, AccessInformationEmbargo]
        if isinstance(_emargo, Unset):
            emargo = UNSET
        else:
            emargo = AccessInformationEmbargo.from_dict(_emargo)

        access_information = cls(
            record=record,
            files=files,
            emargo=emargo,
        )

        access_information.additional_properties = d
        return access_information

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
