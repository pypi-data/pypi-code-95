from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="News")


@attr.s(auto_attribs=True)
class News:
    """ """

    time: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    news: Union[Unset, str] = UNSET
    sticky: Union[Unset, bool] = UNSET
    deleted: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        time = self.time
        name = self.name
        news = self.news
        sticky = self.sticky
        deleted = self.deleted
        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if time is not UNSET:
            field_dict["time"] = time
        if name is not UNSET:
            field_dict["name"] = name
        if news is not UNSET:
            field_dict["news"] = news
        if sticky is not UNSET:
            field_dict["sticky"] = sticky
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        time = d.pop("time", UNSET)

        name = d.pop("name", UNSET)

        news = d.pop("news", UNSET)

        sticky = d.pop("sticky", UNSET)

        deleted = d.pop("deleted", UNSET)

        id = d.pop("id", UNSET)

        news = cls(
            time=time,
            name=name,
            news=news,
            sticky=sticky,
            deleted=deleted,
            id=id,
        )

        news.additional_properties = d
        return news

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
