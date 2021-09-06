from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RouteHopFormat")


@attr.s(auto_attribs=True)
class RouteHopFormat:
    """ """

    hop: Union[Unset, str] = UNSET
    where: Union[Unset, None, str] = UNSET
    render: Union[Unset, bool] = UNSET
    format_: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hop = self.hop
        where = self.where
        render = self.render
        format_ = self.format_

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hop is not UNSET:
            field_dict["hop"] = hop
        if where is not UNSET:
            field_dict["where"] = where
        if render is not UNSET:
            field_dict["render"] = render
        if format_ is not UNSET:
            field_dict["format"] = format_

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hop = d.pop("hop", UNSET)

        where = d.pop("where", UNSET)

        render = d.pop("render", UNSET)

        format_ = d.pop("format", UNSET)

        route_hop_format = cls(
            hop=hop,
            where=where,
            render=render,
            format_=format_,
        )

        route_hop_format.additional_properties = d
        return route_hop_format

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
