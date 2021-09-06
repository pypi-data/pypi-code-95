from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProxyCapabilities")


@attr.s(auto_attribs=True)
class ProxyCapabilities:
    """ """

    type: Union[Unset, str] = UNSET
    name: Union[Unset, None, str] = UNSET
    version: Union[Unset, None, str] = UNSET
    send_modes: Union[Unset, List[str]] = UNSET
    buddy_modes: Union[Unset, List[str]] = UNSET
    supported_cmds: Union[Unset, List[str]] = UNSET
    rate_limited: Union[Unset, bool] = UNSET
    default_mode: Union[Unset, None, str] = UNSET
    started_at: Union[Unset, None, int] = UNSET
    workers: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type
        name = self.name
        version = self.version
        send_modes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.send_modes, Unset):
            send_modes = self.send_modes

        buddy_modes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.buddy_modes, Unset):
            buddy_modes = self.buddy_modes

        supported_cmds: Union[Unset, List[str]] = UNSET
        if not isinstance(self.supported_cmds, Unset):
            supported_cmds = self.supported_cmds

        rate_limited = self.rate_limited
        default_mode = self.default_mode
        started_at = self.started_at
        workers: Union[Unset, List[str]] = UNSET
        if not isinstance(self.workers, Unset):
            workers = self.workers

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["type"] = type
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if send_modes is not UNSET:
            field_dict["send-modes"] = send_modes
        if buddy_modes is not UNSET:
            field_dict["buddy-modes"] = buddy_modes
        if supported_cmds is not UNSET:
            field_dict["supported-cmds"] = supported_cmds
        if rate_limited is not UNSET:
            field_dict["rate-limited"] = rate_limited
        if default_mode is not UNSET:
            field_dict["default-mode"] = default_mode
        if started_at is not UNSET:
            field_dict["started-at"] = started_at
        if workers is not UNSET:
            field_dict["workers"] = workers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type", UNSET)

        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        send_modes = cast(List[str], d.pop("send-modes", UNSET))

        buddy_modes = cast(List[str], d.pop("buddy-modes", UNSET))

        supported_cmds = cast(List[str], d.pop("supported-cmds", UNSET))

        rate_limited = d.pop("rate-limited", UNSET)

        default_mode = d.pop("default-mode", UNSET)

        started_at = d.pop("started-at", UNSET)

        workers = cast(List[str], d.pop("workers", UNSET))

        proxy_capabilities = cls(
            type=type,
            name=name,
            version=version,
            send_modes=send_modes,
            buddy_modes=buddy_modes,
            supported_cmds=supported_cmds,
            rate_limited=rate_limited,
            default_mode=default_mode,
            started_at=started_at,
            workers=workers,
        )

        proxy_capabilities.additional_properties = d
        return proxy_capabilities

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
