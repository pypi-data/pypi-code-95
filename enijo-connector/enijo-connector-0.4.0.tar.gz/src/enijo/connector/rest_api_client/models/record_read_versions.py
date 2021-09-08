from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RecordReadVersions")


@attr.s(auto_attribs=True)
class RecordReadVersions:
    """  """

    index: Union[Unset, int] = UNSET
    is_latest: Union[Unset, bool] = UNSET
    is_latest_draft: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        index = self.index
        is_latest = self.is_latest
        is_latest_draft = self.is_latest_draft

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if index is not UNSET:
            field_dict["index"] = index
        if is_latest is not UNSET:
            field_dict["is_latest"] = is_latest
        if is_latest_draft is not UNSET:
            field_dict["is_latest_draft"] = is_latest_draft

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        index = d.pop("index", UNSET)

        is_latest = d.pop("is_latest", UNSET)

        is_latest_draft = d.pop("is_latest_draft", UNSET)

        record_read_versions = cls(
            index=index,
            is_latest=is_latest,
            is_latest_draft=is_latest_draft,
        )

        record_read_versions.additional_properties = d
        return record_read_versions

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
