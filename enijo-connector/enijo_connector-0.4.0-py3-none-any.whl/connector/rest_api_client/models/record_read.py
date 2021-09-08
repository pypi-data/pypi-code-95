import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.access_information import AccessInformation
from ..models.files import Files
from ..models.metadata import Metadata
from ..models.record_read_ext import RecordReadExt
from ..models.record_read_links import RecordReadLinks
from ..models.record_read_parent import RecordReadParent
from ..models.record_read_provenance import RecordReadProvenance
from ..models.record_read_tombstone import RecordReadTombstone
from ..models.record_read_versions import RecordReadVersions
from ..types import UNSET, Unset

T = TypeVar("T", bound="RecordRead")


@attr.s(auto_attribs=True)
class RecordRead:
    """  """

    id: Union[Unset, str] = UNSET
    parent: Union[Unset, RecordReadParent] = UNSET
    revision_id: Union[Unset, int] = UNSET
    versions: Union[Unset, RecordReadVersions] = UNSET
    is_published: Union[Unset, bool] = UNSET
    pids: Union[Unset, str] = UNSET
    metadata: Union[Unset, Metadata] = UNSET
    ext: Union[Unset, RecordReadExt] = UNSET
    provenance: Union[Unset, RecordReadProvenance] = UNSET
    access: Union[Unset, AccessInformation] = UNSET
    files: Union[Unset, Files] = UNSET
    tombstone: Union[Unset, RecordReadTombstone] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    updated: Union[Unset, datetime.datetime] = UNSET
    links: Union[Unset, RecordReadLinks] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        parent: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.parent, Unset):
            parent = self.parent.to_dict()

        revision_id = self.revision_id
        versions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.versions, Unset):
            versions = self.versions.to_dict()

        is_published = self.is_published
        pids = self.pids
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        ext: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ext, Unset):
            ext = self.ext.to_dict()

        provenance: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.provenance, Unset):
            provenance = self.provenance.to_dict()

        access: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.access, Unset):
            access = self.access.to_dict()

        files: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.files, Unset):
            files = self.files.to_dict()

        tombstone: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tombstone, Unset):
            tombstone = self.tombstone.to_dict()

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        updated: Union[Unset, str] = UNSET
        if not isinstance(self.updated, Unset):
            updated = self.updated.isoformat()

        links: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if parent is not UNSET:
            field_dict["parent"] = parent
        if revision_id is not UNSET:
            field_dict["revision_id"] = revision_id
        if versions is not UNSET:
            field_dict["versions"] = versions
        if is_published is not UNSET:
            field_dict["is_published"] = is_published
        if pids is not UNSET:
            field_dict["pids"] = pids
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if ext is not UNSET:
            field_dict["ext"] = ext
        if provenance is not UNSET:
            field_dict["provenance"] = provenance
        if access is not UNSET:
            field_dict["access"] = access
        if files is not UNSET:
            field_dict["files"] = files
        if tombstone is not UNSET:
            field_dict["tombstone"] = tombstone
        if created is not UNSET:
            field_dict["created"] = created
        if updated is not UNSET:
            field_dict["updated"] = updated
        if links is not UNSET:
            field_dict["links"] = links

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _parent = d.pop("parent", UNSET)
        parent: Union[Unset, RecordReadParent]
        if isinstance(_parent, Unset):
            parent = UNSET
        else:
            parent = RecordReadParent.from_dict(_parent)

        revision_id = d.pop("revision_id", UNSET)

        _versions = d.pop("versions", UNSET)
        versions: Union[Unset, RecordReadVersions]
        if isinstance(_versions, Unset):
            versions = UNSET
        else:
            versions = RecordReadVersions.from_dict(_versions)

        is_published = d.pop("is_published", UNSET)

        pids = d.pop("pids", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, Metadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = Metadata.from_dict(_metadata)

        _ext = d.pop("ext", UNSET)
        ext: Union[Unset, RecordReadExt]
        if isinstance(_ext, Unset):
            ext = UNSET
        else:
            ext = RecordReadExt.from_dict(_ext)

        _provenance = d.pop("provenance", UNSET)
        provenance: Union[Unset, RecordReadProvenance]
        if isinstance(_provenance, Unset):
            provenance = UNSET
        else:
            provenance = RecordReadProvenance.from_dict(_provenance)

        _access = d.pop("access", UNSET)
        access: Union[Unset, AccessInformation]
        if isinstance(_access, Unset):
            access = UNSET
        else:
            access = AccessInformation.from_dict(_access)

        _files = d.pop("files", UNSET)
        files: Union[Unset, Files]
        if isinstance(_files, Unset):
            files = UNSET
        else:
            files = Files.from_dict(_files)

        _tombstone = d.pop("tombstone", UNSET)
        tombstone: Union[Unset, RecordReadTombstone]
        if isinstance(_tombstone, Unset):
            tombstone = UNSET
        else:
            tombstone = RecordReadTombstone.from_dict(_tombstone)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        _updated = d.pop("updated", UNSET)
        updated: Union[Unset, datetime.datetime]
        if isinstance(_updated, Unset):
            updated = UNSET
        else:
            updated = isoparse(_updated)

        _links = d.pop("links", UNSET)
        links: Union[Unset, RecordReadLinks]
        if isinstance(_links, Unset):
            links = UNSET
        else:
            links = RecordReadLinks.from_dict(_links)

        record_read = cls(
            id=id,
            parent=parent,
            revision_id=revision_id,
            versions=versions,
            is_published=is_published,
            pids=pids,
            metadata=metadata,
            ext=ext,
            provenance=provenance,
            access=access,
            files=files,
            tombstone=tombstone,
            created=created,
            updated=updated,
            links=links,
        )

        record_read.additional_properties = d
        return record_read

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
