from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.location import Location

T = TypeVar("T", bound="LocationsBulkGet")


@attr.s(auto_attribs=True, repr=False)
class LocationsBulkGet:
    """  """

    _locations: List[Location]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("locations={}".format(repr(self._locations)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LocationsBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        locations = []
        for locations_item_data in self._locations:
            locations_item = locations_item_data.to_dict()

            locations.append(locations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locations": locations,
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

        locations_bulk_get = cls(
            locations=locations,
        )

        locations_bulk_get.additional_properties = d
        return locations_bulk_get

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
