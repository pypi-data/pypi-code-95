from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.module_subcommand_channel import ModuleSubcommandChannel
from ..types import UNSET, Unset

T = TypeVar("T", bound="ModuleSubcommand")


@attr.s(auto_attribs=True)
class ModuleSubcommand:
    """ """

    command: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    msg: Union[Unset, ModuleSubcommandChannel] = UNSET
    priv: Union[Unset, ModuleSubcommandChannel] = UNSET
    org: Union[Unset, ModuleSubcommandChannel] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        command = self.command
        type = self.type
        description = self.description
        msg: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.msg, Unset):
            msg = self.msg.to_dict()

        priv: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.priv, Unset):
            priv = self.priv.to_dict()

        org: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.org, Unset):
            org = self.org.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if command is not UNSET:
            field_dict["command"] = command
        if type is not UNSET:
            field_dict["type"] = type
        if description is not UNSET:
            field_dict["description"] = description
        if msg is not UNSET:
            field_dict["msg"] = msg
        if priv is not UNSET:
            field_dict["priv"] = priv
        if org is not UNSET:
            field_dict["org"] = org

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        command = d.pop("command", UNSET)

        type = d.pop("type", UNSET)

        description = d.pop("description", UNSET)

        _msg = d.pop("msg", UNSET)
        msg: Union[Unset, ModuleSubcommandChannel]
        if isinstance(_msg, Unset):
            msg = UNSET
        else:
            msg = ModuleSubcommandChannel.from_dict(_msg)

        _priv = d.pop("priv", UNSET)
        priv: Union[Unset, ModuleSubcommandChannel]
        if isinstance(_priv, Unset):
            priv = UNSET
        else:
            priv = ModuleSubcommandChannel.from_dict(_priv)

        _org = d.pop("org", UNSET)
        org: Union[Unset, ModuleSubcommandChannel]
        if isinstance(_org, Unset):
            org = UNSET
        else:
            org = ModuleSubcommandChannel.from_dict(_org)

        module_subcommand = cls(
            command=command,
            type=type,
            description=description,
            msg=msg,
            priv=priv,
            org=org,
        )

        module_subcommand.additional_properties = d
        return module_subcommand

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
