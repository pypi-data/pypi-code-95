from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="FilesEntriesAdditionalProperty")


@attr.s(auto_attribs=True)
class FilesEntriesAdditionalProperty:
    """  """

    bucket_id: str
    version_id: str
    file_id: str
    backend: str
    key: str
    mimetype: str
    size: int
    checksum: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bucket_id = self.bucket_id
        version_id = self.version_id
        file_id = self.file_id
        backend = self.backend
        key = self.key
        mimetype = self.mimetype
        size = self.size
        checksum = self.checksum

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bucket_id": bucket_id,
                "version_id": version_id,
                "file_id": file_id,
                "backend": backend,
                "key": key,
                "mimetype": mimetype,
                "size": size,
                "checksum": checksum,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bucket_id = d.pop("bucket_id")

        version_id = d.pop("version_id")

        file_id = d.pop("file_id")

        backend = d.pop("backend")

        key = d.pop("key")

        mimetype = d.pop("mimetype")

        size = d.pop("size")

        checksum = d.pop("checksum")

        files_entries_additional_property = cls(
            bucket_id=bucket_id,
            version_id=version_id,
            file_id=file_id,
            backend=backend,
            key=key,
            mimetype=mimetype,
            size=size,
            checksum=checksum,
        )

        files_entries_additional_property.additional_properties = d
        return files_entries_additional_property

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
