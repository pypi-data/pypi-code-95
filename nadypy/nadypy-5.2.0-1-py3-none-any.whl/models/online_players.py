from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.online_player import OnlinePlayer
from ..types import UNSET, Unset

T = TypeVar("T", bound="OnlinePlayers")


@attr.s(auto_attribs=True)
class OnlinePlayers:
    """This is the list of all players considered to be online by the bot"""

    org: Union[Unset, List[OnlinePlayer]] = UNSET
    private_channel: Union[Unset, List[OnlinePlayer]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        org: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.org, Unset):
            org = []
            for org_item_data in self.org:
                org_item = org_item_data.to_dict()

                org.append(org_item)

        private_channel: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.private_channel, Unset):
            private_channel = []
            for private_channel_item_data in self.private_channel:
                private_channel_item = private_channel_item_data.to_dict()

                private_channel.append(private_channel_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if org is not UNSET:
            field_dict["org"] = org
        if private_channel is not UNSET:
            field_dict["private_channel"] = private_channel

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        org = []
        _org = d.pop("org", UNSET)
        for org_item_data in _org or []:
            org_item = OnlinePlayer.from_dict(org_item_data)

            org.append(org_item)

        private_channel = []
        _private_channel = d.pop("private_channel", UNSET)
        for private_channel_item_data in _private_channel or []:
            private_channel_item = OnlinePlayer.from_dict(private_channel_item_data)

            private_channel.append(private_channel_item)

        online_players = cls(
            org=org,
            private_channel=private_channel,
        )

        online_players.additional_properties = d
        return online_players

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
