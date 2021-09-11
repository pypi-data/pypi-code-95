import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.checkout_record import CheckoutRecord
from ..models.container_content import ContainerContent
from ..models.container_quantity import ContainerQuantity
from ..models.container_volume import ContainerVolume
from ..models.fields import Fields
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="Container")


@attr.s(auto_attribs=True, repr=False)
class Container:
    """  """

    _barcode: str
    _checkout_record: CheckoutRecord
    _contents: List[ContainerContent]
    _created_at: datetime.datetime
    _creator: UserSummary
    _fields: Fields
    _id: str
    _modified_at: datetime.datetime
    _name: str
    _parent_storage_id: str
    _parent_storage_schema: SchemaSummary
    _volume: ContainerVolume
    _web_url: str
    _project_id: Optional[str]
    _schema: Optional[SchemaSummary]
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _quantity: Union[Unset, ContainerQuantity] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("barcode={}".format(repr(self._barcode)))
        fields.append("checkout_record={}".format(repr(self._checkout_record)))
        fields.append("contents={}".format(repr(self._contents)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("parent_storage_id={}".format(repr(self._parent_storage_id)))
        fields.append("parent_storage_schema={}".format(repr(self._parent_storage_schema)))
        fields.append("volume={}".format(repr(self._volume)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("quantity={}".format(repr(self._quantity)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Container({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        barcode = self._barcode
        checkout_record = self._checkout_record.to_dict()

        contents = []
        for contents_item_data in self._contents:
            contents_item = contents_item_data.to_dict()

            contents.append(contents_item)

        created_at = self._created_at.isoformat()

        creator = self._creator.to_dict()

        fields = self._fields.to_dict()

        id = self._id
        modified_at = self._modified_at.isoformat()

        name = self._name
        parent_storage_id = self._parent_storage_id
        parent_storage_schema = self._parent_storage_schema.to_dict()

        volume = self._volume.to_dict()

        web_url = self._web_url
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        project_id = self._project_id
        quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._quantity, Unset):
            quantity = self._quantity.to_dict()

        schema = self._schema.to_dict() if self._schema else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "barcode": barcode,
                "checkoutRecord": checkout_record,
                "contents": contents,
                "createdAt": created_at,
                "creator": creator,
                "fields": fields,
                "id": id,
                "modifiedAt": modified_at,
                "name": name,
                "parentStorageId": parent_storage_id,
                "parentStorageSchema": parent_storage_schema,
                "volume": volume,
                "webURL": web_url,
                "projectId": project_id,
                "schema": schema,
            }
        )
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if quantity is not UNSET:
            field_dict["quantity"] = quantity

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        barcode = d.pop("barcode")

        checkout_record = CheckoutRecord.from_dict(d.pop("checkoutRecord"))

        contents = []
        _contents = d.pop("contents")
        for contents_item_data in _contents:
            contents_item = ContainerContent.from_dict(contents_item_data)

            contents.append(contents_item)

        created_at = isoparse(d.pop("createdAt"))

        creator = UserSummary.from_dict(d.pop("creator"))

        fields = Fields.from_dict(d.pop("fields"))

        id = d.pop("id")

        modified_at = isoparse(d.pop("modifiedAt"))

        name = d.pop("name")

        parent_storage_id = d.pop("parentStorageId")

        parent_storage_schema = SchemaSummary.from_dict(d.pop("parentStorageSchema"))

        volume = ContainerVolume.from_dict(d.pop("volume"))

        web_url = d.pop("webURL")

        archive_record = None
        _archive_record = d.pop("archiveRecord", UNSET)
        if _archive_record is not None and not isinstance(_archive_record, Unset):
            archive_record = ArchiveRecord.from_dict(_archive_record)

        project_id = d.pop("projectId")

        quantity: Union[Unset, ContainerQuantity] = UNSET
        _quantity = d.pop("quantity", UNSET)
        if not isinstance(_quantity, Unset):
            quantity = ContainerQuantity.from_dict(_quantity)

        schema = None
        _schema = d.pop("schema")
        if _schema is not None:
            schema = SchemaSummary.from_dict(_schema)

        container = cls(
            barcode=barcode,
            checkout_record=checkout_record,
            contents=contents,
            created_at=created_at,
            creator=creator,
            fields=fields,
            id=id,
            modified_at=modified_at,
            name=name,
            parent_storage_id=parent_storage_id,
            parent_storage_schema=parent_storage_schema,
            volume=volume,
            web_url=web_url,
            archive_record=archive_record,
            project_id=project_id,
            quantity=quantity,
            schema=schema,
        )

        container.additional_properties = d
        return container

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
    def checkout_record(self) -> CheckoutRecord:
        return self._checkout_record

    @checkout_record.setter
    def checkout_record(self, value: CheckoutRecord) -> None:
        self._checkout_record = value

    @property
    def contents(self) -> List[ContainerContent]:
        return self._contents

    @contents.setter
    def contents(self, value: List[ContainerContent]) -> None:
        self._contents = value

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
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
    def modified_at(self) -> datetime.datetime:
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
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
    def parent_storage_schema(self) -> SchemaSummary:
        return self._parent_storage_schema

    @parent_storage_schema.setter
    def parent_storage_schema(self, value: SchemaSummary) -> None:
        self._parent_storage_schema = value

    @property
    def volume(self) -> ContainerVolume:
        return self._volume

    @volume.setter
    def volume(self, value: ContainerVolume) -> None:
        self._volume = value

    @property
    def web_url(self) -> str:
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

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
    def project_id(self) -> Optional[str]:
        return self._project_id

    @project_id.setter
    def project_id(self, value: Optional[str]) -> None:
        self._project_id = value

    @property
    def quantity(self) -> ContainerQuantity:
        if isinstance(self._quantity, Unset):
            raise NotPresentError(self, "quantity")
        return self._quantity

    @quantity.setter
    def quantity(self, value: ContainerQuantity) -> None:
        self._quantity = value

    @quantity.deleter
    def quantity(self) -> None:
        self._quantity = UNSET

    @property
    def schema(self) -> Optional[SchemaSummary]:
        return self._schema

    @schema.setter
    def schema(self, value: Optional[SchemaSummary]) -> None:
        self._schema = value
