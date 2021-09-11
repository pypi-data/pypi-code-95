from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.location import Location

T = TypeVar("T", bound="LocationsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class LocationsPaginatedList:
    """  """

    _locations: List[Location]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("locations={}".format(repr(self._locations)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LocationsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        locations = []
        for locations_item_data in self._locations:
            locations_item = locations_item_data.to_dict()

            locations.append(locations_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locations": locations,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        locations = []
        _locations = d.pop("locations")
        for locations_item_data in _locations:
            locations_item = Location.from_dict(locations_item_data)

            locations.append(locations_item)

        next_token = d.pop("nextToken")

        locations_paginated_list = cls(
            locations=locations,
            next_token=next_token,
        )

        locations_paginated_list.additional_properties = d
        return locations_paginated_list

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
    def locations(self) -> List[Location]:
        return self._locations

    @locations.setter
    def locations(self, value: List[Location]) -> None:
        self._locations = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
