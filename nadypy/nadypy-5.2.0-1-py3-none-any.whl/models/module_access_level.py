from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModuleAccessLevel")


@attr.s(auto_attribs=True)
class ModuleAccessLevel:
    """ """

    name: Union[Unset, str] = UNSET
    value: Union[None, Unset, int, str] = UNSET
    numeric_value: Union[Unset, int] = UNSET
    enabled: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        value: Union[None, Unset, int, str]
        if isinstance(self.value, Unset):
            value = UNSET
        elif self.value is None:
            value = None
        else:
            value = self.value

        numeric_value = self.numeric_value
        enabled = self.enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if value is not UNSET:
            field_dict["value"] = value
        if numeric_value is not UNSET:
            field_dict["numeric_value"] = numeric_value
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        def _parse_value(data: object) -> Union[None, Unset, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int, str], data)

        value = _parse_value(d.pop("value", UNSET))

        numeric_value = d.pop("numeric_value", UNSET)

        enabled = d.pop("enabled", UNSET)

        module_access_level = cls(
            name=name,
            value=value,
            numeric_value=numeric_value,
            enabled=enabled,
        )

        module_access_level.additional_properties = d
        return module_access_level

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
