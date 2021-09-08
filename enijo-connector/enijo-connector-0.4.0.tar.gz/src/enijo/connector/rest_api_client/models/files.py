from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.files_entries import FilesEntries
from ..models.files_meta import FilesMeta
from ..types import UNSET, Unset

T = TypeVar("T", bound="Files")


@attr.s(auto_attribs=True)
class Files:
    """ Records may have associated digital files. A record is not meant to be associated with a high number of files, as the files are stored inside the record and thus increase the overall size of the JSON document. """

    enabled: bool
    entries: Union[Unset, FilesEntries] = UNSET
    default_preview: Union[Unset, str] = UNSET
    order: Union[Unset, List[str]] = UNSET
    meta: Union[Unset, FilesMeta] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        enabled = self.enabled
        entries: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.entries, Unset):
            entries = self.entries.to_dict()

        default_preview = self.default_preview
        order: Union[Unset, List[str]] = UNSET
        if not isinstance(self.order, Unset):
            order = self.order

        meta: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enabled": enabled,
            }
        )
        if entries is not UNSET:
            field_dict["entries"] = entries
        if default_preview is not UNSET:
            field_dict["default_preview"] = default_preview
        if order is not UNSET:
            field_dict["order"] = order
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        enabled = d.pop("enabled")

        _entries = d.pop("entries", UNSET)
        entries: Union[Unset, FilesEntries]
        if isinstance(_entries, Unset):
            entries = UNSET
        else:
            entries = FilesEntries.from_dict(_entries)

        default_preview = d.pop("default_preview", UNSET)

        order = cast(List[str], d.pop("order", UNSET))

        _meta = d.pop("meta", UNSET)
        meta: Union[Unset, FilesMeta]
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = FilesMeta.from_dict(_meta)

        files = cls(
            enabled=enabled,
            entries=entries,
            default_preview=default_preview,
            order=order,
            meta=meta,
        )

        files.additional_properties = d
        return files

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
