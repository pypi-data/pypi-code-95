from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.assay_run_validation_status import AssayRunValidationStatus
from ..models.fields import Fields
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayRun")


@attr.s(auto_attribs=True, repr=False)
class AssayRun:
    """  """

    _fields: Fields
    _id: str
    _schema: Optional[SchemaSummary]
    _api_url: Union[Unset, str] = UNSET
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _created_at: Union[Unset, str] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _entry_id: Union[Unset, str] = UNSET
    _is_reviewed: Union[Unset, bool] = UNSET
    _project_id: Union[Unset, str] = UNSET
    _validation_comment: Union[Unset, str] = UNSET
    _validation_status: Union[Unset, AssayRunValidationStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("entry_id={}".format(repr(self._entry_id)))
        fields.append("is_reviewed={}".format(repr(self._is_reviewed)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("validation_comment={}".format(repr(self._validation_comment)))
        fields.append("validation_status={}".format(repr(self._validation_status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayRun({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        fields = self._fields.to_dict()

        id = self._id
        api_url = self._api_url
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        created_at = self._created_at
        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        entry_id = self._entry_id
        is_reviewed = self._is_reviewed
        project_id = self._project_id
        schema = self._schema.to_dict() if self._schema else None

        validation_comment = self._validation_comment
        validation_status: Union[Unset, int] = UNSET
        if not isinstance(self._validation_status, Unset):
            validation_status = self._validation_status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fields": fields,
                "id": id,
                "schema": schema,
            }
        )
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if creator is not UNSET:
            field_dict["creator"] = creator
        if entry_id is not UNSET:
            field_dict["entryId"] = entry_id
        if is_reviewed is not UNSET:
            field_dict["isReviewed"] = is_reviewed
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if validation_comment is not UNSET:
            field_dict["validationComment"] = validation_comment
        if validation_status is not UNSET:
            field_dict["validationStatus"] = validation_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        fields = Fields.from_dict(d.pop("fields"))

        id = d.pop("id")

        api_url = d.pop("apiURL", UNSET)

        archive_record = None
        _archive_record = d.pop("archiveRecord", UNSET)
        if _archive_record is not None and not isinstance(_archive_record, Unset):
            archive_record = ArchiveRecord.from_dict(_archive_record)

        created_at = d.pop("createdAt", UNSET)

        creator: Union[Unset, UserSummary] = UNSET
        _creator = d.pop("creator", UNSET)
        if not isinstance(_creator, Unset):
            creator = UserSummary.from_dict(_creator)

        entry_id = d.pop("entryId", UNSET)

        is_reviewed = d.pop("isReviewed", UNSET)

        project_id = d.pop("projectId", UNSET)

        schema = None
        _schema = d.pop("schema")
        if _schema is not None:
            schema = SchemaSummary.from_dict(_schema)

        validation_comment = d.pop("validationComment", UNSET)

        validation_status = None
        _validation_status = d.pop("validationStatus", UNSET)
        if _validation_status is not None and _validation_status is not UNSET:
            validation_status = AssayRunValidationStatus(_validation_status)

        assay_run = cls(
            fields=fields,
            id=id,
            api_url=api_url,
            archive_record=archive_record,
            created_at=created_at,
            creator=creator,
            entry_id=entry_id,
            is_reviewed=is_reviewed,
            project_id=project_id,
            schema=schema,
            validation_comment=validation_comment,
            validation_status=validation_status,
        )

        assay_run.additional_properties = d
        return assay_run

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
    def api_url(self) -> str:
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

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
    def created_at(self) -> str:
        if isinstance(self._created_at, Unset):
            raise NotPresentError(self, "created_at")
        return self._created_at

    @created_at.setter
    def created_at(self, value: str) -> None:
        self._created_at = value

    @created_at.deleter
    def created_at(self) -> None:
        self._created_at = UNSET

    @property
    def creator(self) -> UserSummary:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

    @property
    def entry_id(self) -> str:
        if isinstance(self._entry_id, Unset):
            raise NotPresentError(self, "entry_id")
        return self._entry_id

    @entry_id.setter
    def entry_id(self, value: str) -> None:
        self._entry_id = value

    @entry_id.deleter
    def entry_id(self) -> None:
        self._entry_id = UNSET

    @property
    def is_reviewed(self) -> bool:
        if isinstance(self._is_reviewed, Unset):
            raise NotPresentError(self, "is_reviewed")
        return self._is_reviewed

    @is_reviewed.setter
    def is_reviewed(self, value: bool) -> None:
        self._is_reviewed = value

    @is_reviewed.deleter
    def is_reviewed(self) -> None:
        self._is_reviewed = UNSET

    @property
    def project_id(self) -> str:
        if isinstance(self._project_id, Unset):
            raise NotPresentError(self, "project_id")
        return self._project_id

    @project_id.setter
    def project_id(self, value: str) -> None:
        self._project_id = value

    @project_id.deleter
    def project_id(self) -> None:
        self._project_id = UNSET

    @property
    def schema(self) -> Optional[SchemaSummary]:
        return self._schema

    @schema.setter
    def schema(self, value: Optional[SchemaSummary]) -> None:
        self._schema = value

    @property
    def validation_comment(self) -> str:
        if isinstance(self._validation_comment, Unset):
            raise NotPresentError(self, "validation_comment")
        return self._validation_comment

    @validation_comment.setter
    def validation_comment(self, value: str) -> None:
        self._validation_comment = value

    @validation_comment.deleter
    def validation_comment(self) -> None:
        self._validation_comment = UNSET

    @property
    def validation_status(self) -> AssayRunValidationStatus:
        if isinstance(self._validation_status, Unset):
            raise NotPresentError(self, "validation_status")
        return self._validation_status

    @validation_status.setter
    def validation_status(self, value: AssayRunValidationStatus) -> None:
        self._validation_status = value

    @validation_status.deleter
    def validation_status(self) -> None:
        self._validation_status = UNSET
