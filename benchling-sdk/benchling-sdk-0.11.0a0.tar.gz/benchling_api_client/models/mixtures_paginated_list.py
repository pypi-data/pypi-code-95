from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.mixture import Mixture

T = TypeVar("T", bound="MixturesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class MixturesPaginatedList:
    """  """

    _mixtures: List[Mixture]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("mixtures={}".format(repr(self._mixtures)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "MixturesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixtures = []
        for mixtures_item_data in self._mixtures:
            mixtures_item = mixtures_item_data.to_dict()

            mixtures.append(mixtures_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mixtures": mixtures,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mixtures = []
        _mixtures = d.pop("mixtures")
        for mixtures_item_data in _mixtures:
            mixtures_item = Mixture.from_dict(mixtures_item_data)

            mixtures.append(mixtures_item)

        next_token = d.pop("nextToken")

        mixtures_paginated_list = cls(
            mixtures=mixtures,
            next_token=next_token,
        )

        mixtures_paginated_list.additional_properties = d
        return mixtures_paginated_list

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def mixtures(self) -> List[Mixture]:
        return self._mixtures

    @mixtures.setter
    def mixtures(self, value: List[Mixture]) -> None:
        self._mixtures = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
