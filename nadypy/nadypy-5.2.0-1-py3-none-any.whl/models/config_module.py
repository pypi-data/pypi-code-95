from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigModule")


@attr.s(auto_attribs=True)
class ConfigModule:
    """ """

    name: Union[Unset, str] = UNSET
    num_commands_enabled: Union[Unset, int] = UNSET
    num_commands_disabled: Union[Unset, int] = UNSET
    num_events_enabled: Union[Unset, int] = UNSET
    num_events_disabled: Union[Unset, int] = UNSET
    num_settings: Union[Unset, int] = UNSET
    description: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        num_commands_enabled = self.num_commands_enabled
        num_commands_disabled = self.num_commands_disabled
        num_events_enabled = self.num_events_enabled
        num_events_disabled = self.num_events_disabled
        num_settings = self.num_settings
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if num_commands_enabled is not UNSET:
            field_dict["num_commands_enabled"] = num_commands_enabled
        if num_commands_disabled is not UNSET:
            field_dict["num_commands_disabled"] = num_commands_disabled
        if num_events_enabled is not UNSET:
            field_dict["num_events_enabled"] = num_events_enabled
        if num_events_disabled is not UNSET:
            field_dict["num_events_disabled"] = num_events_disabled
        if num_settings is not UNSET:
            field_dict["num_settings"] = num_settings
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        num_commands_enabled = d.pop("num_commands_enabled", UNSET)

        num_commands_disabled = d.pop("num_commands_disabled", UNSET)

        num_events_enabled = d.pop("num_events_enabled", UNSET)

        num_events_disabled = d.pop("num_events_disabled", UNSET)

        num_settings = d.pop("num_settings", UNSET)

        description = d.pop("description", UNSET)

        config_module = cls(
            name=name,
            num_commands_enabled=num_commands_enabled,
            num_commands_disabled=num_commands_disabled,
            num_events_enabled=num_events_enabled,
            num_events_disabled=num_events_disabled,
            num_settings=num_settings,
            description=description,
        )

        config_module.additional_properties = d
        return config_module

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
