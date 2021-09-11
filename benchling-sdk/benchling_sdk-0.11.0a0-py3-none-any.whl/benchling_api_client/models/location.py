from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.archive_record import ArchiveRecord
from ..models.fields import Fields
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary

T = TypeVar("T", bound="Location")


@attr.s(auto_attribs=True, repr=False)
class Location:
    """  """

    _barcode: str
    _created_at: str
    _creator: UserSummary
    _fields: Fields
    _id: str
    _modified_at: str
    _name: str
    _parent_storage_id: str
    _web_url: str
    _archive_record: Optional[ArchiveRecord]
    _schema: Optional[SchemaSummary]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("barcode={}".format(repr(self._barcode)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("parent_storage_id={}".format(repr(self._parent_storage_id)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Location({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        barcode = self._barcode
        created_at = self._created_at
        creator = self._creator.to_dict()

        fields = self._fields.to_dict()

        id = self._id
        modified_at = self._modified_at
        name = self._name
        parent_storage_id = self._parent_storage_id
        web_url = self._web_url
        archive_record = self._archive_record.to_dict() if self._archive_record else None

        schema = self._schema.to_dict() if self._schema else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "barcode": barcode,
                "createdAt": created_at,
                "creator": creator,
                "fields": fields,
                "id": id,
                "modifiedAt": modified_at,
                "name": name,
                "parentStorageId": parent_storage_id,
                "webURL": web_url,
                "archiveRecord": archive_record,
                "schema": schema,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        barcode = d.pop("barcode")

        created_at = d.pop("createdAt")

        creator = UserSummary.from_dict(d.pop("creator"))

        fields = Fields.from_dict(d.pop("fields"))

        id = d.pop("id")

        modified_at = d.pop("modifiedAt")

        name = d.pop("name")

        parent_storage_id = d.pop("parentStorageId")

        web_url = d.pop("webURL")

        archive_record = None
        _archive_record = d.pop("archiveRecord")
        if _archive_record is not None:
            archive_record = ArchiveRecord.from_dict(_archive_record)

        schema = None
        _schema = d.pop("schema")
        if _schema is not None:
            schema = SchemaSummary.from_dict(_schema)

        location = cls(
            barcode=barcode,
            created_at=created_at,
            creator=creator,
            fields=fields,
            id=id,
            modified_at=modified_at,
            name=name,
            parent_storage_id=parent_storage_id,
            web_url=web_url,
            archive_record=archive_record,
            schema=schema,
        )

        location.additional_properties = d
        return location

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
    def barcode(self) -> str:
        return self._barcode

    @barcode.setter
    def barcode(self, value: str) -> None:
        self._barcode = value

    @property
    def created_at(self) -> str:
        return self._created_at

    @created_at.setter
    def created_at(self, value: str) -> None:
        self._created_at = value

    @property
    def creator(self) -> UserSummary:
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @property
    def fields(self) -> Fields:
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def modified_at(self) -> str:
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: str) -> None:
        self._modified_at = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def parent_storage_id(self) -> str:
        return self._parent_storage_id

    @parent_storage_id.setter
    def parent_storage_id(self, value: str) -> None:
        self._parent_storage_id = value

    @property
    def web_url(self) -> str:
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @property
    def archive_record(self) -> Optional[ArchiveRecord]:
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: Optional[ArchiveRecord]) -> None:
        self._archive_record = value

    @property
    def schema(self) -> Optional[SchemaSummary]:
        return self._schema

    @schema.setter
    def schema(self, value: Optional[SchemaSummary]) -> None:
        self._schema = value
