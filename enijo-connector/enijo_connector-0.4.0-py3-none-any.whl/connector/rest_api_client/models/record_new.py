from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.access_information import AccessInformation
from ..models.metadata import Metadata
from ..models.record_new_files import RecordNewFiles
from ..types import UNSET, Unset

T = TypeVar("T", bound="RecordNew")


@attr.s(auto_attribs=True)
class RecordNew:
    """  """

    access: Union[Unset, AccessInformation] = UNSET
    files: Union[Unset, RecordNewFiles] = UNSET
    metadata: Union[Unset, Metadata] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        access: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.access, Unset):
            access = self.access.to_dict()

        files: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.files, Unset):
            files = self.files.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if access is not UNSET:
            field_dict["access"] = access
        if files is not UNSET:
            field_dict["files"] = files
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _access = d.pop("access", UNSET)
        access: Union[Unset, AccessInformation]
        if isinstance(_access, Unset):
            access = UNSET
        else:
            access = AccessInformation.from_dict(_access)

        _files = d.pop("files", UNSET)
        files: Union[Unset, RecordNewFiles]
        if isinstance(_files, Unset):
            files = UNSET
        else:
            files = RecordNewFiles.from_dict(_files)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, Metadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = Metadata.from_dict(_metadata)

        record_new = cls(
            access=access,
            files=files,
            metadata=metadata,
        )

        return record_new
