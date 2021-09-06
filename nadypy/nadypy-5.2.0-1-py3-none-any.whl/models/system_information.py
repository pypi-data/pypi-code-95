from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.basic_system_information import BasicSystemInformation
from ..models.channel_info import ChannelInfo
from ..models.config_statistics import ConfigStatistics
from ..models.memory_information import MemoryInformation
from ..models.misc_system_information import MiscSystemInformation
from ..models.system_stats import SystemStats
from ..types import UNSET, Unset

T = TypeVar("T", bound="SystemInformation")


@attr.s(auto_attribs=True)
class SystemInformation:
    """ """

    basic: Union[Unset, BasicSystemInformation] = UNSET
    memory: Union[Unset, MemoryInformation] = UNSET
    misc: Union[Unset, MiscSystemInformation] = UNSET
    config: Union[Unset, ConfigStatistics] = UNSET
    stats: Union[Unset, SystemStats] = UNSET
    channels: Union[Unset, List[ChannelInfo]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        basic: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.basic, Unset):
            basic = self.basic.to_dict()

        memory: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.memory, Unset):
            memory = self.memory.to_dict()

        misc: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.misc, Unset):
            misc = self.misc.to_dict()

        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        stats: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()

        channels: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.channels, Unset):
            channels = []
            for channels_item_data in self.channels:
                channels_item = channels_item_data.to_dict()

                channels.append(channels_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if basic is not UNSET:
            field_dict["basic"] = basic
        if memory is not UNSET:
            field_dict["memory"] = memory
        if misc is not UNSET:
            field_dict["misc"] = misc
        if config is not UNSET:
            field_dict["config"] = config
        if stats is not UNSET:
            field_dict["stats"] = stats
        if channels is not UNSET:
            field_dict["channels"] = channels

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _basic = d.pop("basic", UNSET)
        basic: Union[Unset, BasicSystemInformation]
        if isinstance(_basic, Unset):
            basic = UNSET
        else:
            basic = BasicSystemInformation.from_dict(_basic)

        _memory = d.pop("memory", UNSET)
        memory: Union[Unset, MemoryInformation]
        if isinstance(_memory, Unset):
            memory = UNSET
        else:
            memory = MemoryInformation.from_dict(_memory)

        _misc = d.pop("misc", UNSET)
        misc: Union[Unset, MiscSystemInformation]
        if isinstance(_misc, Unset):
            misc = UNSET
        else:
            misc = MiscSystemInformation.from_dict(_misc)

        _config = d.pop("config", UNSET)
        config: Union[Unset, ConfigStatistics]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = ConfigStatistics.from_dict(_config)

        _stats = d.pop("stats", UNSET)
        stats: Union[Unset, SystemStats]
        if isinstance(_stats, Unset):
            stats = UNSET
        else:
            stats = SystemStats.from_dict(_stats)

        channels = []
        _channels = d.pop("channels", UNSET)
        for channels_item_data in _channels or []:
            channels_item = ChannelInfo.from_dict(channels_item_data)

            channels.append(channels_item)

        system_information = cls(
            basic=basic,
            memory=memory,
            misc=misc,
            config=config,
            stats=stats,
            channels=channels,
        )

        system_information.additional_properties = d
        return system_information

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
