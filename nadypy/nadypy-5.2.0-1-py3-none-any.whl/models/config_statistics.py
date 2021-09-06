from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigStatistics")


@attr.s(auto_attribs=True)
class ConfigStatistics:
    """ """

    active_tell_commands: Union[Unset, int] = UNSET
    active_priv_commands: Union[Unset, int] = UNSET
    active_org_commands: Union[Unset, int] = UNSET
    active_subcommands: Union[Unset, int] = UNSET
    active_aliases: Union[Unset, int] = UNSET
    active_events: Union[Unset, int] = UNSET
    active_help_commands: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        active_tell_commands = self.active_tell_commands
        active_priv_commands = self.active_priv_commands
        active_org_commands = self.active_org_commands
        active_subcommands = self.active_subcommands
        active_aliases = self.active_aliases
        active_events = self.active_events
        active_help_commands = self.active_help_commands

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active_tell_commands is not UNSET:
            field_dict["active_tell_commands"] = active_tell_commands
        if active_priv_commands is not UNSET:
            field_dict["active_priv_commands"] = active_priv_commands
        if active_org_commands is not UNSET:
            field_dict["active_org_commands"] = active_org_commands
        if active_subcommands is not UNSET:
            field_dict["active_subcommands"] = active_subcommands
        if active_aliases is not UNSET:
            field_dict["active_aliases"] = active_aliases
        if active_events is not UNSET:
            field_dict["active_events"] = active_events
        if active_help_commands is not UNSET:
            field_dict["active_help_commands"] = active_help_commands

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        active_tell_commands = d.pop("active_tell_commands", UNSET)

        active_priv_commands = d.pop("active_priv_commands", UNSET)

        active_org_commands = d.pop("active_org_commands", UNSET)

        active_subcommands = d.pop("active_subcommands", UNSET)

        active_aliases = d.pop("active_aliases", UNSET)

        active_events = d.pop("active_events", UNSET)

        active_help_commands = d.pop("active_help_commands", UNSET)

        config_statistics = cls(
            active_tell_commands=active_tell_commands,
            active_priv_commands=active_priv_commands,
            active_org_commands=active_org_commands,
            active_subcommands=active_subcommands,
            active_aliases=active_aliases,
            active_events=active_events,
            active_help_commands=active_help_commands,
        )

        config_statistics.additional_properties = d
        return config_statistics

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
