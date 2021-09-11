from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.dropdown_field_definition_type import DropdownFieldDefinitionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownFieldDefinition")


@attr.s(auto_attribs=True, repr=False)
class DropdownFieldDefinition:
    """  """

    _id: str
    _is_required: bool
    _name: str
    _dropdown_id: Union[Unset, None, str] = UNSET
    _type: Union[Unset, DropdownFieldDefinitionType] = UNSET
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _is_multi: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("is_required={}".format(repr(self._is_required)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("dropdown_id={}".format(repr(self._dropdown_id)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("is_multi={}".format(repr(self._is_multi)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DropdownFieldDefinition({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        is_required = self._is_required
        name = self._name
        dropdown_id = self._dropdown_id
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        is_multi = self._is_multi

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "isRequired": is_required,
                "name": name,
            }
        )
        if dropdown_id is not UNSET:
            field_dict["dropdownId"] = dropdown_id
        if type is not UNSET:
            field_dict["type"] = type
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if is_multi is not UNSET:
            field_dict["isMulti"] = is_multi

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        is_required = d.pop("isRequired")

        name = d.pop("name")

        dropdown_id = d.pop("dropdownId", UNSET)

        type = None
        _type = d.pop("type", UNSET)
        if _type is not None and _type is not UNSET:
            type = DropdownFieldDefinitionType(_type)

        archive_record = None
        _archive_record = d.pop("archiveRecord", UNSET)
        if _archive_record is not None and not isinstance(_archive_record, Unset):
            archive_record = ArchiveRecord.from_dict(_archive_record)

        is_multi = d.pop("isMulti", UNSET)

        dropdown_field_definition = cls(
            id=id,
            is_required=is_required,
            name=name,
            dropdown_id=dropdown_id,
            type=type,
            archive_record=archive_record,
            is_multi=is_multi,
        )

        dropdown_field_definition.additional_properties = d
        return dropdown_field_definition

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
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def is_required(self) -> bool:
        return self._is_required

    @is_required.setter
    def is_required(self, value: bool) -> None:
        self._is_required = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def dropdown_id(self) -> Optional[str]:
        if isinstance(self._dropdown_id, Unset):
            raise NotPresentError(self, "dropdown_id")
        return self._dropdown_id

    @dropdown_id.setter
    def dropdown_id(self, value: Optional[str]) -> None:
        self._dropdown_id = value

    @dropdown_id.deleter
    def dropdown_id(self) -> None:
        self._dropdown_id = UNSET

    @property
    def type(self) -> DropdownFieldDefinitionType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: DropdownFieldDefinitionType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def archive_record(self) -> Optional[ArchiveRecord]:
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: Optional[ArchiveRecord]) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET

    @property
    def is_multi(self) -> bool:
        if isinstance(self._is_multi, Unset):
            raise NotPresentError(self, "is_multi")
        return self._is_multi

    @is_multi.setter
    def is_multi(self, value: bool) -> None:
        self._is_multi = value

    @is_multi.deleter
    def is_multi(self) -> None:
        self._is_multi = UNSET
