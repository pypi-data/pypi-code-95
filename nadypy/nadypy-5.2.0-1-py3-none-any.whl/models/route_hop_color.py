from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RouteHopColor")


@attr.s(auto_attribs=True)
class RouteHopColor:
    """ """

    hop: Union[Unset, str] = UNSET
    where: Union[Unset, None, str] = UNSET
    tag_color: Union[Unset, None, str] = UNSET
    text_color: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hop = self.hop
        where = self.where
        tag_color = self.tag_color
        text_color = self.text_color

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hop is not UNSET:
            field_dict["hop"] = hop
        if where is not UNSET:
            field_dict["where"] = where
        if tag_color is not UNSET:
            field_dict["tag_color"] = tag_color
        if text_color is not UNSET:
            field_dict["text_color"] = text_color

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hop = d.pop("hop", UNSET)

        where = d.pop("where", UNSET)

        tag_color = d.pop("tag_color", UNSET)

        text_color = d.pop("text_color", UNSET)

        route_hop_color = cls(
            hop=hop,
            where=where,
            tag_color=tag_color,
            text_color=text_color,
        )

        route_hop_color.additional_properties = d
        return route_hop_color

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
