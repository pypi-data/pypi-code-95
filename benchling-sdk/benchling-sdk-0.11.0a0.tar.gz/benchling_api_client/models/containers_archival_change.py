from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

T = TypeVar("T", bound="ContainersArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class ContainersArchivalChange:
    """IDs of all items that were unarchived, grouped by resource type. This includes the IDs of containers that were unarchived."""

    _container_ids: List[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainersArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids = self._container_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "containerIds": container_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_ids = cast(List[str], d.pop("containerIds"))

        containers_archival_change = cls(
            container_ids=container_ids,
        )

        containers_archival_change.additional_properties = d
        return containers_archival_change

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
    def container_ids(self) -> List[str]:
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value
