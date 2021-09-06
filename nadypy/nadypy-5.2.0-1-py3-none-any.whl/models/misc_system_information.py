from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.proxy_capabilities import ProxyCapabilities
from ..types import UNSET, Unset

T = TypeVar("T", bound="MiscSystemInformation")


@attr.s(auto_attribs=True)
class MiscSystemInformation:
    """ """

    using_chat_proxy: Union[Unset, bool] = UNSET
    proxy_capabilities: Union[Unset, ProxyCapabilities] = UNSET
    uptime: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        using_chat_proxy = self.using_chat_proxy
        proxy_capabilities: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.proxy_capabilities, Unset):
            proxy_capabilities = self.proxy_capabilities.to_dict()

        uptime = self.uptime

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if using_chat_proxy is not UNSET:
            field_dict["using_chat_proxy"] = using_chat_proxy
        if proxy_capabilities is not UNSET:
            field_dict["proxy_capabilities"] = proxy_capabilities
        if uptime is not UNSET:
            field_dict["uptime"] = uptime

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        using_chat_proxy = d.pop("using_chat_proxy", UNSET)

        _proxy_capabilities = d.pop("proxy_capabilities", UNSET)
        proxy_capabilities: Union[Unset, ProxyCapabilities]
        if isinstance(_proxy_capabilities, Unset):
            proxy_capabilities = UNSET
        else:
            proxy_capabilities = ProxyCapabilities.from_dict(_proxy_capabilities)

        uptime = d.pop("uptime", UNSET)

        misc_system_information = cls(
            using_chat_proxy=using_chat_proxy,
            proxy_capabilities=proxy_capabilities,
            uptime=uptime,
        )

        misc_system_information.additional_properties = d
        return misc_system_information

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
