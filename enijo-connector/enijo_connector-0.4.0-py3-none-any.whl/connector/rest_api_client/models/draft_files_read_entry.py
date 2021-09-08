import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.draft_files_read_entry_metadata import DraftFilesReadEntryMetadata
from ..models.draft_files_read_entry_status import DraftFilesReadEntryStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="DraftFilesReadEntry")


@attr.s(auto_attribs=True)
class DraftFilesReadEntry:
    """  """

    key: str
    updated: datetime.datetime
    created: datetime.datetime
    status: DraftFilesReadEntryStatus
    bucket_id: Union[Unset, str] = UNSET
    version_id: Union[Unset, str] = UNSET
    file_id: Union[Unset, str] = UNSET
    backend: Union[Unset, str] = UNSET
    mimetype: Union[Unset, str] = UNSET
    size: Union[Unset, int] = UNSET
    checksum: Union[Unset, str] = UNSET
    metadata: Union[Unset, None, DraftFilesReadEntryMetadata] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        key = self.key
        updated = self.updated.isoformat()

        created = self.created.isoformat()

        status = self.status.value

        bucket_id = self.bucket_id
        version_id = self.version_id
        file_id = self.file_id
        backend = self.backend
        mimetype = self.mimetype
        size = self.size
        checksum = self.checksum
        metadata: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict() if self.metadata else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "updated": updated,
                "created": created,
                "status": status,
            }
        )
        if bucket_id is not UNSET:
            field_dict["bucket_id"] = bucket_id
        if version_id is not UNSET:
            field_dict["version_id"] = version_id
        if file_id is not UNSET:
            field_dict["file_id"] = file_id
        if backend is not UNSET:
            field_dict["backend"] = backend
        if mimetype is not UNSET:
            field_dict["mimetype"] = mimetype
        if size is not UNSET:
            field_dict["size"] = size
        if checksum is not UNSET:
            field_dict["checksum"] = checksum
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        key = d.pop("key")

        updated = isoparse(d.pop("updated"))

        created = isoparse(d.pop("created"))

        status = DraftFilesReadEntryStatus(d.pop("status"))

        bucket_id = d.pop("bucket_id", UNSET)

        version_id = d.pop("version_id", UNSET)

        file_id = d.pop("file_id", UNSET)

        backend = d.pop("backend", UNSET)

        mimetype = d.pop("mimetype", UNSET)

        size = d.pop("size", UNSET)

        checksum = d.pop("checksum", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, None, DraftFilesReadEntryMetadata]
        if _metadata is None:
            metadata = None
        elif isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DraftFilesReadEntryMetadata.from_dict(_metadata)

        draft_files_read_entry = cls(
            key=key,
            updated=updated,
            created=created,
            status=status,
            bucket_id=bucket_id,
            version_id=version_id,
            file_id=file_id,
            backend=backend,
            mimetype=mimetype,
            size=size,
            checksum=checksum,
            metadata=metadata,
        )

        draft_files_read_entry.additional_properties = d
        return draft_files_read_entry

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
