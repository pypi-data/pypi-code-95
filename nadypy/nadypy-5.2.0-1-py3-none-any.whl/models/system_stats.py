from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="SystemStats")


@attr.s(auto_attribs=True)
class SystemStats:
    """ """

    buddy_list_size: Union[Unset, int] = UNSET
    max_buddy_list_size: Union[Unset, int] = UNSET
    priv_channel_size: Union[Unset, int] = UNSET
    org_size: Union[Unset, int] = UNSET
    charinfo_cache_size: Union[Unset, int] = UNSET
    chatqueue_length: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        buddy_list_size = self.buddy_list_size
        max_buddy_list_size = self.max_buddy_list_size
        priv_channel_size = self.priv_channel_size
        org_size = self.org_size
        charinfo_cache_size = self.charinfo_cache_size
        chatqueue_length = self.chatqueue_length

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if buddy_list_size is not UNSET:
            field_dict["buddy_list_size"] = buddy_list_size
        if max_buddy_list_size is not UNSET:
            field_dict["max_buddy_list_size"] = max_buddy_list_size
        if priv_channel_size is not UNSET:
            field_dict["priv_channel_size"] = priv_channel_size
        if org_size is not UNSET:
            field_dict["org_size"] = org_size
        if charinfo_cache_size is not UNSET:
            field_dict["charinfo_cache_size"] = charinfo_cache_size
        if chatqueue_length is not UNSET:
            field_dict["chatqueue_length"] = chatqueue_length

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        buddy_list_size = d.pop("buddy_list_size", UNSET)

        max_buddy_list_size = d.pop("max_buddy_list_size", UNSET)

        priv_channel_size = d.pop("priv_channel_size", UNSET)

        org_size = d.pop("org_size", UNSET)

        charinfo_cache_size = d.pop("charinfo_cache_size", UNSET)

        chatqueue_length = d.pop("chatqueue_length", UNSET)

        system_stats = cls(
            buddy_list_size=buddy_list_size,
            max_buddy_list_size=max_buddy_list_size,
            priv_channel_size=priv_channel_size,
            org_size=org_size,
            charinfo_cache_size=charinfo_cache_size,
            chatqueue_length=chatqueue_length,
        )

        system_stats.additional_properties = d
        return system_stats

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
