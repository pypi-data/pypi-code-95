from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.location_schema import LocationSchema

T = TypeVar("T", bound="LocationSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class LocationSchemasPaginatedList:
    """  """

    _next_token: str
    _location_schemas: List[LocationSchema]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("location_schemas={}".format(repr(self._location_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LocationSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        location_schemas = []
        for location_schemas_item_data in self._location_schemas:
            location_schemas_item = location_schemas_item_data.to_dict()

            location_schemas.append(location_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nextToken": next_token,
                "locationSchemas": location_schemas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        next_token = d.pop("nextToken")

        location_schemas = []
        _location_schemas = d.pop("locationSchemas")
        for location_schemas_item_data in _location_schemas:
            location_schemas_item = LocationSchema.from_dict(location_schemas_item_data)

            location_schemas.append(location_schemas_item)

        location_schemas_paginated_list = cls(
            next_token=next_token,
            location_schemas=location_schemas,
        )

        location_schemas_paginated_list.additional_properties = d
        return location_schemas_paginated_list

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
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @property
    def location_schemas(self) -> List[LocationSchema]:
        return self._location_schemas

    @location_schemas.setter
    def location_schemas(self, value: List[LocationSchema]) -> None:
        self._location_schemas = value
