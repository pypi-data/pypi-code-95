from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.organization import Organization
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="Project")


@attr.s(auto_attribs=True, repr=False)
class Project:
    """  """

    _id: str
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _name: Union[Unset, str] = UNSET
    _owner: Union[Unset, Organization, UserSummary] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("owner={}".format(repr(self._owner)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Project({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        name = self._name
        owner: Union[Unset, Dict[str, Any]]
        if isinstance(self._owner, Unset):
            owner = UNSET
        elif isinstance(self._owner, Organization):
            owner = UNSET
            if not isinstance(self._owner, Unset):
                owner = self._owner.to_dict()

        else:
            owner = UNSET
            if not isinstance(self._owner, Unset):
                owner = self._owner.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if name is not UNSET:
            field_dict["name"] = name
        if owner is not UNSET:
            field_dict["owner"] = owner

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        archive_record = None
        _archive_record = d.pop("archiveRecord", UNSET)
        if _archive_record is not None and not isinstance(_archive_record, Unset):
            archive_record = ArchiveRecord.from_dict(_archive_record)

        name = d.pop("name", UNSET)

        def _parse_owner(data: Union[Unset, Dict[str, Any]]) -> Union[Unset, Organization, UserSummary]:
            owner: Union[Unset, Organization, UserSummary]
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                owner = UNSET
                _owner = data
                if not isinstance(_owner, Unset):
                    owner = Organization.from_dict(_owner)

                return owner
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            owner = UNSET
            _owner = data
            if not isinstance(_owner, Unset):
                owner = UserSummary.from_dict(_owner)

            return owner

        owner = _parse_owner(d.pop("owner", UNSET))

        project = cls(
            id=id,
            archive_record=archive_record,
            name=name,
            owner=owner,
        )

        project.additional_properties = d
        return project

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
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def owner(self) -> Union[Organization, UserSummary]:
        if isinstance(self._owner, Unset):
            raise NotPresentError(self, "owner")
        return self._owner

    @owner.setter
    def owner(self, value: Union[Organization, UserSummary]) -> None:
        self._owner = value

    @owner.deleter
    def owner(self) -> None:
        self._owner = UNSET
